from __future__ import annotations

from helpline.backends.base import LLMBackend
from helpline.parse import parse_model_output
from helpline.prompts import build_prompt
from helpline.types import TranslationRequest, TranslationResult


class Translator:
    """Build an OS-aware prompt, call the local model, parse a command."""

    def __init__(self, backend: LLMBackend) -> None:
        self.backend = backend

    def translate(self, request: TranslationRequest) -> TranslationResult:
        prompt = build_prompt(request)
        raw = self.backend.complete(prompt)
        result = parse_model_output(raw, model=getattr(self.backend, "model", None))
        if not result.command:
            notes = result.notes or "Model returned an empty command"
            raise ValueError(notes)
        return result
