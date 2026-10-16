from __future__ import annotations

import json
from urllib.error import URLError

import pytest

from helpline.backends.ollama import OllamaBackend, OllamaError, model_is_installed
from helpline.config import load_settings
from helpline.prompts import Prompt


class _FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._raw = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._raw

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None


class _FakeOpener:
    def __init__(self, payload: dict | None = None, *, error: Exception | None = None) -> None:
        self.payload = payload
        self.error = error
        self.requests: list[object] = []

    def urlopen(self, request: object, timeout: float = 0) -> _FakeResponse:
        self.requests.append(request)
        if self.error:
            raise self.error
        assert self.payload is not None
        return _FakeResponse(self.payload)


def test_complete_reads_message_content() -> None:
    opener = _FakeOpener({"message": {"content": '{"command": "pwd"}'}})
    backend = OllamaBackend(load_settings(environ={}), opener=opener)
    text = backend.complete(Prompt(system="sys", user="user"))
    assert text == '{"command": "pwd"}'
    assert opener.requests


def test_complete_offline() -> None:
    opener = _FakeOpener(error=URLError("connection refused"))
    backend = OllamaBackend(load_settings(environ={}), opener=opener)
    with pytest.raises(OllamaError, match="ollama pull"):
        backend.complete(Prompt(system="s", user="u"))


def test_complete_reports_api_error() -> None:
    opener = _FakeOpener({"error": "model not found"})
    backend = OllamaBackend(load_settings(environ={}), opener=opener)
    with pytest.raises(OllamaError, match="model not found"):
        backend.complete(Prompt(system="s", user="u"))


@pytest.mark.parametrize(
    ("configured", "installed", "ok"),
    [
        ("qwen2.5-coder:3b", ["qwen2.5-coder:3b"], True),
        ("qwen2.5-coder", ["qwen2.5-coder:3b"], True),
        ("qwen2.5-coder:7b", ["qwen2.5-coder:3b"], False),
        ("tinyllama", ["qwen2.5-coder:3b"], False),
    ],
)
def test_model_is_installed(configured: str, installed: list[str], ok: bool) -> None:
    assert model_is_installed(configured, installed) is ok


def test_ping() -> None:
    opener = _FakeOpener({"models": [{"name": "qwen2.5-coder:3b"}]})
    backend = OllamaBackend(load_settings(environ={}), opener=opener)
    tags = backend.ping()
    assert tags["models"][0]["name"] == "qwen2.5-coder:3b"

