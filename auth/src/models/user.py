from typing import Annotated

from pydantic import BaseModel, Field, AfterValidator


def pwd_validator(pwd: str) -> str:
    if not pwd:
        raise ValueError('The password is required')
    if len(pwd) < 8:
        raise ValueError('The password must be at least 8 chars')
    if not any(char.isdigit() for char in pwd):
        raise ValueError('The password must contain digits')
    return pwd


class UserCreateRequest(BaseModel):
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)
    login: str = Field(..., min_length=5, max_length=15)
    password: Annotated[str, AfterValidator(pwd_validator)]


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    login: str

    class Config:
        orm_mode = True
