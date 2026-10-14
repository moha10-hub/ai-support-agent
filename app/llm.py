"""Crea il modello di linguaggio scelto in .env (Gemini gratis di default, OpenAI opzionale)."""

from langchain_core.language_models import BaseChatModel

from app.config import Settings


class MissingApiKeyError(RuntimeError):
    """La chiave API del provider scelto non è configurata."""


def build_llm(settings: Settings) -> BaseChatModel:
    # Gli import dei provider sono dentro le funzioni: serve installare solo quello che usi.
    if settings.llm_provider == "gemini":
        if settings.google_api_key is None:
            raise MissingApiKeyError(
                "GOOGLE_API_KEY mancante. Creala gratis su https://aistudio.google.com/apikey "
                "e scrivila nel file .env"
            )
        from langchain_google_genai import ChatGoogleGenerativeAI

        options = {}
        if settings.llm_temperature is not None:
            options["temperature"] = settings.llm_temperature
        return ChatGoogleGenerativeAI(
            model=settings.model_name,
            api_key=settings.google_api_key.get_secret_value(),
            timeout=settings.llm_timeout_seconds,
            max_retries=2,
            **options,
        )

    if settings.openai_api_key is None:
        raise MissingApiKeyError("OPENAI_API_KEY mancante: scrivila nel file .env")
    from langchain_openai import ChatOpenAI  # richiede: pip install langchain-openai

    options = {}
    if settings.llm_temperature is not None:
        options["temperature"] = settings.llm_temperature
    return ChatOpenAI(
        model=settings.model_name,
        api_key=settings.openai_api_key.get_secret_value(),
        timeout=settings.llm_timeout_seconds,
        max_retries=2,
        **options,
    )