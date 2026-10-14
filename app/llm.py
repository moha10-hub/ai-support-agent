"""Crea il modello di linguaggio scelto in .env (Gemini gratis di default, OpenAI opzionale)."""

from typing import Optional

from langchain_core.language_models import BaseChatModel
from pydantic import SecretStr

from app.config import Settings


class MissingApiKeyError(RuntimeError):
    """La chiave API del provider scelto non è configurata."""


def _key_value(key: Optional[SecretStr]) -> str:
    """Restituisce la chiave, oppure "" se manca.

    Nel .env una riga `GOOGLE_API_KEY=` vuota arriva come stringa vuota, non come None.
    """
    return key.get_secret_value().strip() if key is not None else ""


def build_llm(settings: Settings) -> BaseChatModel:
    # Gli import dei provider sono dentro le funzioni: serve installare solo quello che usi.
    options = {}
    if settings.llm_temperature is not None:
        options["temperature"] = settings.llm_temperature

    if settings.llm_provider == "gemini":
        google_key = _key_value(settings.google_api_key)
        if not google_key:
            raise MissingApiKeyError(
                "GOOGLE_API_KEY mancante o vuota. Creala gratis su https://aistudio.google.com/apikey, "
                "scrivila nel file .env dopo GOOGLE_API_KEY= e salva il file."
            )
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=settings.model_name,
            api_key=google_key,
            timeout=settings.llm_timeout_seconds,
            max_retries=2,
            **options,
        )

    openai_key = _key_value(settings.openai_api_key)
    if not openai_key:
        raise MissingApiKeyError("OPENAI_API_KEY mancante o vuota: scrivila nel file .env e salva.")
    from langchain_openai import ChatOpenAI  # richiede: pip install langchain-openai

    return ChatOpenAI(
        model=settings.model_name,
        api_key=openai_key,
        timeout=settings.llm_timeout_seconds,
        max_retries=2,
        **options,
    )