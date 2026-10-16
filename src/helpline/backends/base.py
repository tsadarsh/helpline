from __future__ import annotations

from typing import Protocol

from helpline.prompts import Prompt


class LLMBackend(Protocol):
    """Minimal interface so tests can swap the real Ollama client."""

    model: str

    def complete(self, prompt: Prompt) -> str: ...
