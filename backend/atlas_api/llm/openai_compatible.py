import requests

from .base import LLMError, LLMProvider


class OpenAICompatibleProvider(LLMProvider):
    """Any Chat Completions-compatible endpoint (OpenAI, Azure, the previous
    Emergent proxy, self-hosted vLLM, etc). Kept as an alternative to Gemini
    so switching providers is a config change, not a rewrite.
    """

    def __init__(self, *, api_key: str, base_url: str, default_model: str, temperature: float, timeout: int):
        if not api_key:
            raise LLMError("OPENAI_COMPATIBLE_API_KEY is not set")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.temperature = temperature
        self.timeout = timeout

    def complete(self, *, system: str, user: str, json_mode: bool, model: str | None = None) -> str:
        url = f"{self.base_url}/chat/completions"
        body = {
            "model": model or self.default_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": self.temperature,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        try:
            r = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=body,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise LLMError(f"LLM request failed: {exc}") from exc

        if not r.ok:
            raise LLMError(f"LLM error {r.status_code}: {r.text}")

        data = r.json()
        try:
            return data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError) as exc:
            raise LLMError(f"Unexpected completion response shape: {data}") from exc
