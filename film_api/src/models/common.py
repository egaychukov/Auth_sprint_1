from pydantic import BaseModel, Field


class ListRequest(BaseModel):
    page_number: int | None = Field(None, ge=0)
    page_size: int | None = Field(None, gt=0)
    sort: str | None = Field(None, pattern=r'^[-+][a-zA-Z_]+$')
    query: str | None = None


class SearchRequest(BaseModel):
    page_number: int = Field(..., ge=0)
    page_size: int = Field(..., gt=0)
    query: str
