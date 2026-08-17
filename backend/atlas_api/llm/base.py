from abc import ABC, abstractmethod


class LLMError(Exception):
    """Raised when a provider fails to produce a usable completion."""


class LLMProvider(ABC):
    """Common interface every LLM backend must implement.

    Call sites in atlas_api never talk to a provider SDK directly — they go
    through complete_json()/complete_text() so the provider (Gemini, any
    OpenAI-compatible endpoint, ...) can be swapped via the LLM_PROVIDER env
    var without touching business logic.
    """

    @abstractmethod
    def complete(self, *, system: str, user: str, json_mode: bool, model: str | None = None) -> str:
        """Return the raw text completion for a system+user prompt pair."""
        raise NotImplementedError

    def complete_json(self, *, system: str, user: str, model: str | None = None) -> dict:
        import json

        raw = self.complete(system=system, user=user, json_mode=True, model=model)
        try:
            return json.loads(raw)
        except (TypeError, ValueError):
            return {"raw": raw}

    def complete_text(self, *, system: str, user: str, model: str | None = None) -> str:
        return self.complete(system=system, user=user, json_mode=False, model=model)
