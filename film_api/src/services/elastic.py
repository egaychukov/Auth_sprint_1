from typing import Any, Annotated

from fastapi import Depends
from elasticsearch import AsyncElasticsearch, NotFoundError

from core.config import settings
from db.elastic import get_elastic
from models.common import ListRequest, SearchRequest


class ElasticService:
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_doc_by_id(self, index: str, doc_id: str) -> dict[str, Any] | None:
        try:
            doc = await self.elastic.get(index=index, id=doc_id)
        except NotFoundError:
            return None
        return doc['_source']

    async def search_docs(self, index: str, request: SearchRequest, fields: list[str]) -> list[dict[str, Any]] | None:
        if not fields:
            return None
        try:
            docs = await self.elastic.search(index=index, body={
                'from': request.page_number * request.page_size,
                'size': request.page_size,
                'query': {'bool': {'should': [{'match': {field: request.query}} for field in fields]}}
            })
        except NotFoundError:
            return None
        return [doc['_source'] for doc in docs['hits']['hits']]

    async def get_exact_docs(self, index: str, request: ListRequest, fields: list[str] = []) -> list[dict[
        str, Any]] | None:
        body = {'query': {'match_all': {}}}
        if request.query and fields:
            body['query'] = {'bool': {'should': [{'term': {field: request.query}} for field in fields]}}
        if (request.page_number is not None) and (request.page_size is not None):
            body['size'], body['from'] = request.page_size, request.page_number * request.page_size
        if request.sort:
            body['sort'] = [{request.sort[1:]: 'desc' if request.sort[0] == '-' else 'asc'}]
        docs = await self._fetch_documents(index, body)
        return [doc['_source'] for doc in docs] if docs else None

    async def get_exact_docs_by_nested(self, index: str, query: str, fields: list[str]) -> list[dict[str, Any]] | None:
        if not fields:
            return None
        nested_queries = []
        for field in fields:
            arr, _ = field.split('.')
            nested_queries.append({'nested': {'path': arr, 'query': {'bool': {'must': {'match': {field: query}}}}}})
        docs = await self._fetch_documents(index, {'query': {'bool': {'should': nested_queries}}})
        return [doc['_source'] for doc in docs] if docs else None

    async def _fetch_documents(self, index: str, query: dict[str, Any]) -> list[dict[str, Any]] | None:
        try:
            if ('from' in query) and ('size' in query):
                search_response = await self.elastic.search(index=index, body=query)
                return search_response["hits"]["hits"]
            result = []
            from_, size = 0, settings.es_load_batch_size
            while True:
                search_response = await self.elastic.search(
                    index=index,
                    body={
                        **query,
                        'from': from_,
                        'size': size
                    })
                hits = search_response["hits"]["hits"]
                if not hits:
                    break
                from_ += size
                result.extend(hits)
            return result
        except NotFoundError:
            return None


def get_elastic_service(
        elastic: Annotated[AsyncElasticsearch, Depends(get_elastic)]
) -> ElasticService:
    return ElasticService(elastic)
