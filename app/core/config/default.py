from os import environ

from pydantic_settings import BaseSettings, SettingsConfigDict


class DefaultSettings(BaseSettings):
    """
    Default configs for application.

    Usually, we have three environments: for development, testing and production.
    But in this situation, we only have standard settings for local development.
    """

    ENV: str = environ.get("ENV", "local")
    # PATH_PREFIX: str = environ.get("PATH_PREFIX", "/api/v1")
    APP_HOST: str = environ.get("APP_HOST", "http://127.0.0.1")
    APP_PORT: int = int(environ.get("APP_PORT", "8080"))

    POSTGRES_DB: str = environ.get("POSTGRES_DB", "shortener_db")
    POSTGRES_HOST: str = environ.get("POSTGRES_HOST", "localhost")
    POSTGRES_USER: str = environ.get("POSTGRES_USER", "user")
    POSTGRES_PORT: int = int(environ.get("POSTGRES_PORT", "5432")[-4:])
    POSTGRES_PASSWORD: str = environ.get("POSTGRES_PASSWORD", "hackme")

    CHUNK_SIZE: int = int(environ.get("CHUNK_SIZE", 800))
    CHUNK_OVERLAP: int = int(environ.get("CHUNK_OVERLAP", 200))

    # FRONTEND_URL: str = environ.get("FRONTEND_URL", "http://localhost:3000")

    # JWT_SECRET_KEY: str = environ.get("JWT_SECRET_KEY", "secret")
    # JWT_AUDIENCE: str = environ.get("JWT_AUDIENCE", "promoters")
    # JWT_ISSUER: str = environ.get("JWT_ISSUER", "promoter-app")
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    #     environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    # )
    # REFRESH_TOKEN_EXPIRE_DAYS: int = int(environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "14"))

    # SENTRY_DSN: str = environ.get(
    #     "SENTRY_DSN",
    #     "",
    # )
    # SENTRY_ENVIRONMENT: str = environ.get("SENTRY_ENVIRONMENT", "local")
    # SENTRY_TRACES_SAMPLE_RATE: float = float(
    #     environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1")
    # )
    # SENTRY_PROFILES_SAMPLE_RATE: float = float(
    #     environ.get("SENTRY_PROFILES_SAMPLE_RATE", "0.1")
    # )
    # SENTRY_SEND_DEFAULT_PII: bool = (
    #     environ.get("SENTRY_SEND_DEFAULT_PII", "false").lower() == "true"
    # )

    @property
    def database_settings(self) -> dict:
        """
        Get all settings for connection with database.
        """
        return {
            "database": self.POSTGRES_DB,
            "user": self.POSTGRES_USER,
            "password": self.POSTGRES_PASSWORD,
            "host": self.POSTGRES_HOST,
            "port": self.POSTGRES_PORT,
        }

    @property
    def database_uri(self) -> str:
        """
        Get uri for connection with database.
        """
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}".format(
            **self.database_settings,
        )

    @property
    def database_uri_sync(self) -> str:
        """
        Get uri for connection with database.
        """
        return "postgresql://{user}:{password}@{host}:{port}/{database}".format(
            **self.database_settings,
        )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
