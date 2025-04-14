"""Test fixtures."""

from base64 import b64encode
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.app import app
from src.core import configuration
from .database import session_manager


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_manager.get_session() as session:
        yield session


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        token: str =f"{configuration.AUTH.USER}:{configuration.AUTH.PASS}"
        client.headers.update(
            {

                "Authorization": f'Basic {b64encode(token.encode("utf-8")).decode("utf-8")}'
            }
        )
        yield client
