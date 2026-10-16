from __future__ import annotations

from helpline.config import DEFAULT_MODEL, load_settings


def test_defaults() -> None:
    settings = load_settings(environ={})
    assert settings.model == DEFAULT_MODEL
    assert settings.ollama_host == "http://127.0.0.1:11434"


def test_env_overrides() -> None:
    settings = load_settings(
        environ={
            "HELPLINE_MODEL": "qwen2.5-coder:7b",
            "HELPLINE_OLLAMA_HOST": "localhost:11435",
        }
    )
    assert settings.model == "qwen2.5-coder:7b"
    assert settings.ollama_host == "http://localhost:11435"


def test_cli_overrides_env() -> None:
    settings = load_settings(
        model="tinyllama",
        ollama_host="http://example:1",
        environ={"HELPLINE_MODEL": "ignored"},
    )
    assert settings.model == "tinyllama"
    assert settings.ollama_host == "http://example:1"
