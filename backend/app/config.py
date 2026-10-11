"""Loads configuration from environment variables / a .env file."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings. All fields are optional so the server starts without them."""

    ANTHROPIC_API_KEY: str | None = None
    MODEL_NAME: str | None = None
    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return the settings, created once and then cached."""
    return Settings()
