from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from helpline.config import Settings
from helpline.prompts import Prompt


class OllamaError(RuntimeError):
    """Network or API failure talking to a local Ollama server."""


class OllamaBackend:
    """Calls a local Ollama HTTP API (open-weights models, no cloud)."""

    def __init__(
        self,
        settings: Settings,
        *,
        opener: Any | None = None,
    ) -> None:
        self.settings = settings
        self.model = settings.model
        self._opener = opener or urllib.request

    def complete(self, prompt: Prompt) -> str:
        payload = {
            "model": self.settings.model,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
            "messages": [
                {"role": "system", "content": prompt.system},
                {"role": "user", "content": prompt.user},
            ],
        }
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.settings.ollama_host}/api/chat",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self._opener.urlopen(request, timeout=self.settings.timeout_seconds) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise OllamaError(_http_message(exc.code, detail, self.settings)) from exc
        except urllib.error.URLError as exc:
            raise OllamaError(_offline_message(self.settings, exc)) from exc
        except TimeoutError as exc:
            raise OllamaError(
                f"Ollama timed out after {self.settings.timeout_seconds:.0f}s "
                f"({self.settings.ollama_host}). Try a smaller model or increase wait time."
            ) from exc

        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise OllamaError("Ollama returned a non-JSON body") from exc

        error = data.get("error")
        if error:
            raise OllamaError(str(error))

        message = data.get("message") or {}
        content = message.get("content")
        if not isinstance(content, str):
            raise OllamaError("Ollama response was missing message.content")
        return content

    def ping(self) -> dict[str, Any]:
        request = urllib.request.Request(
            f"{self.settings.ollama_host}/api/tags",
            method="GET",
        )
        try:
            with self._opener.urlopen(request, timeout=5) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            raise OllamaError(_offline_message(self.settings, exc)) from exc


def model_is_installed(configured: str, installed: list[str]) -> bool:
    want = configured.strip().lower()
    want_base, _, want_tag = want.partition(":")
    for raw in installed:
        name = raw.strip().lower()
        if not name:
            continue
        if name == want:
            return True
        base, _, tag = name.partition(":")
        if base != want_base:
            continue
        if not want_tag or tag == want_tag:
            return True
    return False


def _offline_message(settings: Settings, exc: BaseException) -> str:
    return (
        f"Could not reach Ollama at {settings.ollama_host} ({exc}). "
        "Install Ollama, start the server (`ollama serve`), then pull the model: "
        f"`ollama pull {settings.model}`."
    )


def _http_message(code: int, detail: str, settings: Settings) -> str:
    snippet = detail.strip()[:400]
    extra = f" {snippet}" if snippet else ""
    if code == 404:
        return (
            f"Ollama does not have model {settings.model!r}.{extra} "
            f"Run: ollama pull {settings.model}"
        )
    return f"Ollama HTTP {code}.{extra}"
