from os import environ
from functools import lru_cache

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
