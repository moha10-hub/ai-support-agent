"""Impostazioni dell'agente, lette da variabili d'ambiente o dal file .env."""

from functools import lru_cache
from typing import Literal, Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_MODELS = {
    "gemini": "gemini-3.5-flash-lite",
    "openai": "gpt-4o-mini",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- API ordini (mock) ---
    orders_api_url: str = "http://127.0.0.1:8001"
    orders_api_timeout_seconds: float = 5.0

    # --- LLM ---
    llm_provider: Literal["gemini", "openai"] = "gemini"
    llm_model: Optional[str] = None  # se vuoto si usa il modello di default del provider
    llm_temperature: Optional[float] = None  # se vuoto vale il default del provider
    llm_timeout_seconds: float = 30.0
    google_api_key: Optional[SecretStr] = None
    openai_api_key: Optional[SecretStr] = None

    @property
    def model_name(self) -> str:
        return self.llm_model or DEFAULT_MODELS[self.llm_provider]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()