"""App configurations."""

from pydantic import BaseModel, PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class SqlDBConfigurations(BaseModel):
    """Sql DB configurations class.

    Attributes:
        HOST: Database host
        PORT: Database port.
        USER: Database user.
        PASSWORD: Database password.
        NAME: Database name.
    """

    HOST: str
    PORT: int
    USER: str
    PASS: str
    NAME: str

    @computed_field
    def psql_url(self) -> PostgresDsn:
        """Generate database URL.

        Returns:
                Database URL.
        """
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.USER,
            password=self.PASS,
            host=self.HOST,
            path=self.NAME,
            port=self.PORT,
        )


class AuthConfigurations(BaseModel):
    """Auth configurations class."""

    USER: str
    PASS: str


class Configuration(BaseSettings):
    """Project settings class."""

    model_config = SettingsConfigDict(env_nested_delimiter="__")

    DB: SqlDBConfigurations
    AUTH: AuthConfigurations


configuration: Configuration = Configuration()
