import logging

import backoff
import psycopg2

from state_warehouse import State


class PostgresExtractor:
    TABLES = ["film_work", "genre", "person"]

    def __init__(self, pg_connection, state: State) -> None:
        self.pg_connection = pg_connection
        self.cursor = self.pg_connection.cursor()
        self.state = state

    @backoff.on_exception(wait_gen=backoff.expo, exception=psycopg2.Error)
    def extract_data(self):
        table_handlers_mapping = {
            "film_work": self.film_work_extract_handler,
            "genre": self.genres_extract_handler,
            "person": self.persons_extract_handler,
        }

        for table_name in self.TABLES:
            logging.info(f"Extracting data from table {table_name}")
            full_film_data, table_data = table_handlers_mapping[table_name]()
            yield table_name, full_film_data, table_data

    def film_work_extract_handler(self) -> tuple[list, list]:
        film_work_ids, last_modified = self.get_ids(table="film_work", state=self.state.get_state("film_work_modified"))
        if not film_work_ids:
            return [], []
        self.state.set_state("film_work_modified", last_modified)
        films_info = self.get_full_film_work_info(film_work_ids)
        return films_info, films_info

    def genres_extract_handler(self) -> tuple[list, list]:
        genre_ids, last_modified = self.get_ids(table="genre", state=self.state.get_state("genre_modified"))
        if not genre_ids:
            return [], []
        genres_info = self.get_genres(genre_ids)
        self.state.set_state("genre_modified", last_modified)
        film_work_ids = self.get_film_work_ids_by_rel_ids("genre", genre_ids)
        return self.get_full_film_work_info(film_work_ids) if film_work_ids else [], genres_info

    def persons_extract_handler(self) -> tuple[list, list]:
        person_ids, last_modified = self.get_ids(table="person", state=self.state.get_state("person_modified"))
        if not person_ids:
            return [], []
        persons_info = self.get_persons(person_ids)
        self.state.set_state("person_modified", last_modified)
        film_work_ids = self.get_film_work_ids_by_rel_ids("person", person_ids)
        return self.get_full_film_work_info(film_work_ids) if film_work_ids else [], persons_info

    def get_ids(self, table: str, state: State) -> tuple[list[str], str]:
        self.cursor.execute(
            f"""
                SELECT DISTINCT id, modified
                FROM content.{table}
                WHERE modified > '{state}'
                ORDER BY modified;
            """
        )
        row_ids, last_modified = [], None
        for row in self.cursor.fetchall():
            row_ids.append(str(row["id"]))
            last_modified = row["modified"]
        return row_ids, str(last_modified)

    def get_film_work_ids_by_rel_ids(self, rel_table: str, rel_ids: list[str]) -> list[str]:
        self.cursor.execute(
            f"""
                SELECT DISTINCT fw.id
                FROM content.film_work fw
                LEFT JOIN content.{rel_table}_film_work rel_fw ON rel_fw.film_work_id = fw.id
                WHERE rel_fw.{rel_table}_id IN {tuple(rel_ids)};
            """
        )
        data = self.cursor.fetchall()
        return [fw["id"] for fw in data]

    def get_genres(self, ids: list[str]) -> list:
        query = f"""
                SELECT DISTINCT id, name, description
                FROM content.genre
                WHERE content.genre.id IN {tuple(ids)};
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_persons(self, ids: list[str]) -> list:
        query = f"""
                SELECT DISTINCT id, full_name
                FROM content.person
                WHERE content.person.id IN {tuple(ids)};
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_full_film_work_info(self, film_work_ids: list[str]) -> list:
        query = f"""
            SELECT
            fw.id, fw.title, fw.description, fw.rating, fw.type, fw.created, fw.modified,
            COALESCE (
                   json_agg(
                       DISTINCT jsonb_build_object(
                           'person_role', pfw.role,
                           'person_id', p.id,
                           'person_name', p.full_name
                       )
                   ) FILTER (WHERE p.id is not null),
                   '[]'
            ) as persons,
            array_agg(DISTINCT g.name) AS genres
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person p ON p.id = pfw.person_id
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
            WHERE fw.id IN {tuple(film_work_ids)}
            GROUP BY fw.id
            ORDER BY fw.modified;
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
