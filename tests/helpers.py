from __future__ import annotations

from dataclasses import dataclass

from helpline.prompts import Prompt


@dataclass
class FakeBackend:
    response: str
    model: str = "fake-model"
    last_prompt: Prompt | None = None

    def complete(self, prompt: Prompt) -> str:
        self.last_prompt = prompt
        return self.response
