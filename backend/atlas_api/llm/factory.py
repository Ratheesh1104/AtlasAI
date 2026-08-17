from functools import lru_cache

from django.conf import settings

from .base import LLMError, LLMProvider
from .gemini import GeminiProvider
from .openai_compatible import OpenAICompatibleProvider

_PROVIDERS = {
    "gemini": lambda: GeminiProvider(
        api_key=settings.GEMINI_API_KEY,
        base_url=settings.GEMINI_API_BASE_URL,
        default_model=settings.ATLAS_LLM_MODEL or settings.GEMINI_MODEL,
        temperature=settings.ATLAS_LLM_TEMPERATURE,
        timeout=settings.ATLAS_LLM_TIMEOUT,
    ),
    "openai_compatible": lambda: OpenAICompatibleProvider(
        api_key=settings.OPENAI_COMPATIBLE_API_KEY,
        base_url=settings.OPENAI_COMPATIBLE_BASE_URL,
        default_model=settings.ATLAS_LLM_MODEL or settings.OPENAI_COMPATIBLE_MODEL,
        temperature=settings.ATLAS_LLM_TEMPERATURE,
        timeout=settings.ATLAS_LLM_TIMEOUT,
    ),
}


@lru_cache(maxsize=None)
def _build(provider_name: str) -> LLMProvider:
    try:
        factory = _PROVIDERS[provider_name]
    except KeyError:
        raise LLMError(
            f"Unknown LLM_PROVIDER={provider_name!r}; expected one of {sorted(_PROVIDERS)}"
        ) from None
    return factory()


def get_llm_provider() -> LLMProvider:
    """Return the configured LLM provider, selected via the LLM_PROVIDER env var."""
    return _build(settings.ATLAS_LLM_PROVIDER)
