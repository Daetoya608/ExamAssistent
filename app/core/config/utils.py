from os import environ
from functools import lru_cache
from urllib.parse import urlparse

from app.core.config.default import DefaultSettings


@lru_cache
def get_settings() -> DefaultSettings:
    env = environ.get("ENV", "local")
    if env == "local":
        return DefaultSettings()
    # ...
    # space for other settings
    # ...
    return DefaultSettings()  # fallback to default


def get_hostname(url: str) -> str:
    return urlparse(url).netloc
