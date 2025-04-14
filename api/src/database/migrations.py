"""Migrations module."""

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel

from src.core import configuration
from src.models import Event

_ = Event


async def migrate():
    """Run migrations."""
    url: str = str(configuration.DB.psql_url)

    engine: AsyncSession = create_async_engine(
        url,
        echo=True,
        future=True,
        pool_size=20,
        max_overflow=20,
        pool_recycle=3600,
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(migrate())
