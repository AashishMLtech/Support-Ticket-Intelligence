"""Groq LLM client."""

import json

from app.core.config import Settings
from app.core.exceptions import LLMUnavailableError


class GroqClient:
    """Minimal Groq client using the official SDK when configured."""

    def __init__(self, settings: Settings):
        self._settings = settings

    @property
    def configured(self) -> bool:
        return bool(self._settings.groq_api_key)

    @property
    def model_name(self) -> str:
        return self._settings.groq_model

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict:
        """Call Groq and parse a JSON object."""

        if not self.configured:
            raise LLMUnavailableError(
                "GROQ_API_KEY is not configured. Add it to .env to enable /query."
            )
        try:
            from groq import Groq
        except ImportError as exc:
            raise LLMUnavailableError("Install requirements.txt to enable Groq support.") from exc

        client = Groq(api_key=self._settings.groq_api_key)
        response = client.chat.completions.create(
            model=self._settings.groq_model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            timeout=self._settings.llm_timeout_seconds,
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)
