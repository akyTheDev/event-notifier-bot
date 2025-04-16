"""App configurations."""

from pydantic import BaseModel, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisConfiguration(BaseModel):
    """Redis configuration class."""

    HOST: str
    PORT: int
    PASS: str


class ApiConfigurations(BaseModel):
    """Api configurations class."""

    USER: str
    PASS: str
    URL: HttpUrl


class Configuration(BaseSettings):
    """Project settings class."""

    model_config = SettingsConfigDict(env_nested_delimiter="__")

    API: ApiConfigurations
    REDIS: RedisConfiguration
    TELEGRAM_TOKEN: str


configuration: Configuration = Configuration()
