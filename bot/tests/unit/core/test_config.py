"""Unit tests for config."""

from src.core.config import configuration

class TestConfiguration:
    def test_ok(self):
        assert str(configuration.API.USER) == "username"
        assert str(configuration.API.PASS) == "password"
        assert str(configuration.API.URL) == "http://localhost:8000/"
        assert str(configuration.TELEGRAM_TOKEN) == "token"
        assert configuration.REDIS.PASS == "redis"
        assert configuration.REDIS.PORT == 6379
        assert configuration.REDIS.HOST=="localhost"

