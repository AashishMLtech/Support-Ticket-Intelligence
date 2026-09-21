"""LLM abstractions."""

from typing import Protocol


class LLMClient(Protocol):
    """Protocol implemented by supported LLM providers."""

    @property
    def configured(self) -> bool:
        """Whether the client has enough credentials/configuration to run."""

    @property
    def model_name(self) -> str:
        """Provider model name."""

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict:
        """Return parsed JSON from an LLM completion."""
