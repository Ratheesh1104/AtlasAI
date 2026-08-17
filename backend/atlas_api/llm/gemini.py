import requests

from .base import LLMError, LLMProvider


class GeminiProvider(LLMProvider):
    """Google Gemini via the free-tier Generative Language REST API.

    Docs: https://ai.google.dev/gemini-api/docs — an API key from
    https://aistudio.google.com/apikey is enough, no billing account required
    for the default free-tier models (e.g. gemini-2.0-flash).
    """

    def __init__(self, *, api_key: str, base_url: str, default_model: str, temperature: float, timeout: int):
        if not api_key:
            raise LLMError("GEMINI_API_KEY is not set")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.temperature = temperature
        self.timeout = timeout

    def complete(self, *, system: str, user: str, json_mode: bool, model: str | None = None) -> str:
        model_name = model or self.default_model
        url = f"{self.base_url}/models/{model_name}:generateContent"
        generation_config = {"temperature": self.temperature}
        if json_mode:
            generation_config["response_mime_type"] = "application/json"
        body = {
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": generation_config,
        }
        try:
            r = requests.post(
                url,
                params={"key": self.api_key},
                json=body,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise LLMError(f"Gemini request failed: {exc}") from exc

        if not r.ok:
            raise LLMError(f"Gemini error {r.status_code}: {r.text}")

        data = r.json()
        try:
            candidate = data["candidates"][0]
            parts = candidate["content"]["parts"]
            return "".join(p.get("text", "") for p in parts)
        except (KeyError, IndexError) as exc:
            raise LLMError(f"Unexpected Gemini response shape: {data}") from exc
