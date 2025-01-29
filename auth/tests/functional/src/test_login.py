from http import HTTPStatus

import pytest
from sqlalchemy import select

from db.sqlalchemy import User


LOGIN_ROUTE = '/api/v1/login/'


@pytest.mark.asyncio
async def test_validation(db_session):
    stmt = select(User)
    result = await db_session.scalars(stmt)
    assert len(result.all()) == 2
