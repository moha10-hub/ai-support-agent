"""Impostazioni dell'agente, lette da variabili d'ambiente o dal file .env."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    orders_api_url: str = "http://127.0.0.1:8001"
    orders_api_timeout_seconds: float = 5.0


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()