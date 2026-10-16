from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_MODEL = "qwen2.5-coder:3b"
DEFAULT_OLLAMA_HOST = "http://127.0.0.1:11434"


@dataclass(frozen=True)
class Settings:
    model: str
    ollama_host: str
    timeout_seconds: float = 120.0


def load_settings(
    *,
    model: str | None = None,
    ollama_host: str | None = None,
    environ: dict[str, str] | None = None,
) -> Settings:
    env = environ if environ is not None else os.environ
    host = (
        ollama_host
        or env.get("HELPLINE_OLLAMA_HOST")
        or env.get("OLLAMA_HOST")
        or DEFAULT_OLLAMA_HOST
    )
    if not host.startswith(("http://", "https://")):
        host = f"http://{host}"
    return Settings(
        model=(model or env.get("HELPLINE_MODEL") or DEFAULT_MODEL).strip(),
        ollama_host=host.rstrip("/"),
    )
