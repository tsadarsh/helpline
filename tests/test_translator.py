from __future__ import annotations

import pytest

from helpline.translator import Translator
from helpline.types import ShellFamily, TargetOS, TranslationRequest
from tests.helpers import FakeBackend


def test_translator_parses_backend_json() -> None:
    backend = FakeBackend('{"command": "ls", "notes": ""}')
    result = Translator(backend).translate(
        TranslationRequest("list files", TargetOS.LINUX, ShellFamily.POSIX)
    )
    assert result.command == "ls"
    assert result.model == "fake-model"
    assert backend.last_prompt is not None
    assert "linux" in backend.last_prompt.system.lower()
    assert backend.last_prompt.user == "list files"


def test_translator_rejects_empty_command() -> None:
    backend = FakeBackend('{"command": "", "notes": "cannot do that"}')
    with pytest.raises(ValueError, match="cannot do that"):
        Translator(backend).translate(
            TranslationRequest("???", TargetOS.MACOS, ShellFamily.POSIX)
        )
