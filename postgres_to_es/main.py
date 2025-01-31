import logging
import os
from time import sleep

from dotenv import load_dotenv
from psycopg2.extensions import connection as _connection
from elasticsearch import Elasticsearch

from extractor import PostgresExtractor
from helpers import pg_conn_context, postgres_to_elastic, create_indexes_if_not_exists, genres_postgres_to_elastic, \
    persons_postgres_to_elastic
from loader import ElasticSearchLoader
from state_warehouse import State, JsonFileStorage

load_dotenv()

logging.basicConfig(level=logging.INFO)


def start_etl_process(pg_connection: _connection, es_client: Elasticsearch, state: State):
    for table_name, raw_pg_film_data, table_data in PostgresExtractor(pg_connection, state).extract_data():
        ready_full_films_data = postgres_to_elastic(raw_pg_film_data)
        if table_name == "genre":
            genres_data = genres_postgres_to_elastic(table_data)
            ElasticSearchLoader(es_client).load_data(genres_data, index_name="genre")
        if table_name == "person":
            persons_data = persons_postgres_to_elastic(table_data)
            ElasticSearchLoader(es_client).load_data(persons_data, index_name="person")
        ElasticSearchLoader(es_client).load_data(ready_full_films_data, index_name="movies")


if __name__ == '__main__':
    dsl = {
        "dbname": os.environ.get("POSTGRES_DB"),
        "user": os.environ.get("POSTGRES_USER"),
        "password": os.environ.get("POSTGRES_PASSWORD"),
        "host": os.environ.get("POSTGRES_HOST"),
        "port": os.environ.get("POSTGRES_PORT", 5432)
    }

    while True:
        logging.info("Starting ETL process.")
        state = State(JsonFileStorage("state.json"))
        ELASTIC_SEARCH_STRING = f"http://{os.environ.get('ELASTIC_HOST')}:{os.environ.get('ELASTIC_PORT')}"
        create_indexes_if_not_exists(ELASTIC_SEARCH_STRING)
        elastic_client = Elasticsearch(ELASTIC_SEARCH_STRING)
        with pg_conn_context(dsl) as pg_conn:
            start_etl_process(pg_conn, elastic_client, state)
        logging.info(
            f"ETL finished successfully. Next ETL will be in {int(os.environ.get("ITERATION_DELAY"))} seconds.")
        sleep(int(os.environ.get("ITERATION_DELAY")))
