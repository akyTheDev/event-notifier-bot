"""Unit tests for config module."""

from src.core import configuration


class TestConfiguration:
    def test_ok(self):
        assert str(configuration.DB.psql_url) == (
            "postgresql+asyncpg://dbuser:dbpass@localhost:5432/postgres"
        )
        assert str(configuration.AUTH.USER) == "username"
        assert str(configuration.AUTH.PASS) == "password"

