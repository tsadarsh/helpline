from __future__ import annotations

import json
import re
from typing import Any

from helpline.types import TranslationResult

_FENCE_RE = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.DOTALL | re.IGNORECASE)
_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


class ParseError(ValueError):
    """Raised when model output cannot be turned into a TranslationResult."""


def parse_model_output(text: str, *, model: str | None = None) -> TranslationResult:
    raw = (text or "").strip()
    if not raw:
        raise ParseError("Model returned an empty response")

    fenced = _FENCE_RE.match(raw)
    if fenced:
        raw = fenced.group(1).strip()

    data = _load_json(raw)
    if data is not None:
        return _result_from_mapping(data, model=model)

    match = _OBJECT_RE.search(raw)
    if match:
        data = _load_json(match.group(0))
        if data is not None:
            return _result_from_mapping(data, model=model)

    if _looks_like_bare_command(raw):
        return TranslationResult(command=_first_command_line(raw), model=model)

    raise ParseError(f"Could not parse model output as JSON or a command:\n{text}")


def _load_json(raw: str) -> dict[str, Any] | None:
    try:
        loaded = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return loaded if isinstance(loaded, dict) else None


def _result_from_mapping(data: dict[str, Any], *, model: str | None) -> TranslationResult:
    command = data.get("command", data.get("cmd"))
    if command is None:
        raise ParseError("JSON is missing a 'command' field")
    if not isinstance(command, str):
        raise ParseError("'command' must be a string")
    notes = data.get("notes") or data.get("note")
    if notes is not None and not isinstance(notes, str):
        raise ParseError("'notes' must be a string when present")
    notes = notes.strip() if isinstance(notes, str) and notes.strip() else None
    return TranslationResult(command=command.strip(), notes=notes, model=model)


def _looks_like_bare_command(raw: str) -> bool:
    first = raw.splitlines()[0].strip()
    if not first or first[0] in "{[":
        return False
    lowered = first.lower()
    if lowered.startswith(("here ", "sure", "the command", "i would", "you can")):
        return False
    return True


def _first_command_line(raw: str) -> str:
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return raw.strip()
