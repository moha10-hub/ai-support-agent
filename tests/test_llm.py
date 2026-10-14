import pytest

from app.config import Settings
from app.llm import MissingApiKeyError, build_llm


def test_gemini_without_key_gives_clear_error():
    # _env_file=None: ignora il tuo .env vero, il test deve funzionare anche se hai la chiave.
    settings = Settings(_env_file=None, llm_provider="gemini", google_api_key=None)
    with pytest.raises(MissingApiKeyError, match="GOOGLE_API_KEY"):
        build_llm(settings)


def test_gemini_with_empty_key_gives_clear_error():
    # Caso reale: nel .env c'è "GOOGLE_API_KEY=" senza valore, che arriva come stringa vuota.
    settings = Settings(_env_file=None, llm_provider="gemini", google_api_key="")
    with pytest.raises(MissingApiKeyError, match="GOOGLE_API_KEY"):
        build_llm(settings)


def test_model_name_defaults_per_provider():
    assert Settings(_env_file=None, llm_provider="gemini", llm_model=None).model_name == "gemini-3.5-flash-lite"
    assert Settings(_env_file=None, llm_provider="openai", llm_model=None).model_name == "gpt-4o-mini"
    assert Settings(_env_file=None, llm_provider="gemini", llm_model="altro").model_name == "altro"