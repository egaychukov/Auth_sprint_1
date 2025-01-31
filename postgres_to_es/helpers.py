import logging
from contextlib import contextmanager

import psycopg2
from elasticsearch import Elasticsearch
from psycopg2.extras import DictCursor

genres_es_schema = {
    "settings": {
        "refresh_interval": "1s",
        "analysis": {
            "filter": {
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_"
                },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                },
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english"
                },
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_"
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            },
            "analyzer": {
                "ru_en": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer",
                        "russian_stop",
                        "russian_stemmer"
                    ]
                }
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {
                "type": "keyword"
            },
            "name": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "description": {
                "type": "text",
                "analyzer": "ru_en"
            }
        }
    }
}

persons_es_schema = {
    "settings": {
        "refresh_interval": "1s",
        "analysis": {
            "filter": {
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_"
                },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                },
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english"
                },
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_"
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            },
            "analyzer": {
                "ru_en": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer",
                        "russian_stop",
                        "russian_stemmer"
                    ]
                }
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {
                "type": "keyword"
            },
            "full_name": {
                "type": "text",
                "analyzer": "ru_en"
            }
        }
    }
}

es_schema = {
    "settings": {
        "refresh_interval": "1s",
        "analysis": {
            "filter": {
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_"
                },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                },
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english"
                },
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_"
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            },
            "analyzer": {
                "ru_en": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer",
                        "russian_stop",
                        "russian_stemmer"
                    ]
                }
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {
                "type": "keyword"
            },
            "imdb_rating": {
                "type": "float"
            },
            "genres": {
                "type": "keyword"
            },
            "title": {
                "type": "text",
                "analyzer": "ru_en",
                "fields": {
                    "raw": {
                        "type": "keyword"
                    }
                }
            },
            "description": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "directors_names": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "actors_names": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "writers_names": {
                "type": "text",
                "analyzer": "ru_en"
            },
            "directors": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "id": {
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text",
                        "analyzer": "ru_en"
                    }
                }
            },
            "actors": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "id": {
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text",
                        "analyzer": "ru_en"
                    }
                }
            },
            "writers": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "id": {
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text",
                        "analyzer": "ru_en"
                    }
                }
            }
        }
    }
}


@contextmanager
def pg_conn_context(dsl: dict):
    conn = psycopg2.connect(**dsl, cursor_factory=DictCursor)
    try:
        yield conn
    except psycopg2.Error as exc:
        logging.error(f'Postgres database error: {exc}')
    finally:
        conn.close()


def genres_postgres_to_elastic(pg_raw_data: list) -> list:
    transformed_data = []
    if not pg_raw_data:
        return []
    for data in pg_raw_data:
        full_data = {
            "id": str(data['id']),
            "name": data['name'],
            "description": data['description']
        }
        transformed_data.append(full_data)
    return transformed_data


def persons_postgres_to_elastic(pg_raw_data: list) -> list:
    transformed_data = []
    if not pg_raw_data:
        return []
    for data in pg_raw_data:
        full_data = {
            "id": str(data['id']),
            "full_name": data['full_name']
        }
        transformed_data.append(full_data)
    return transformed_data


def postgres_to_elastic(pg_raw_data: list) -> list:
    transformed_data = []

    if not pg_raw_data:
        return []

    for data in pg_raw_data:
        full_data = {
            "id": str(data["id"]),
            "imdb_rating": data["rating"],
            "genres": data["genres"],
            "title": data["title"],
            "description": data["description"],
            "directors_names": ", ".join(
                [
                    person["person_name"]
                    for person in data["persons"]
                    if person["person_role"] == "director"
                ]
            ),
            "actors_names": ", ".join(
                [
                    person["person_name"]
                    for person in data["persons"]
                    if person["person_role"] == "actor"
                ]
            ),
            "writers_names": ", ".join(
                [
                    person["person_name"]
                    for person in data["persons"]
                    if person["person_role"] == "writer"
                ]
            ),
            "directors": [
                {"id": person["person_id"], "name": person["person_name"]}
                for person in data["persons"]
                if person["person_role"] == "director"
            ],
            "actors": [
                {"id": person["person_id"], "name": person["person_name"]}
                for person in data["persons"]
                if person["person_role"] == "actor"
            ],
            "writers": [
                {"id": person["person_id"], "name": person["person_name"]}
                for person in data["persons"]
                if person["person_role"] == "writer"
            ],
        }
        transformed_data.append(full_data)

    return transformed_data


def create_indexes_if_not_exists(host) -> None:
    with Elasticsearch(host) as client:
        if not client.indices.exists(index="movies"):
            logging.info("There is no index with name 'movies', creating...")
            client.indices.create(index="movies", body=es_schema)
        if not client.indices.exists(index="genre"):
            logging.info("There is no index with name 'genre', creating...")
            client.indices.create(index="genre", body=genres_es_schema)
        if not client.indices.exists(index="person"):
            logging.info("There is no index with name 'person', creating...")
            client.indices.create(index="person", body=persons_es_schema)
