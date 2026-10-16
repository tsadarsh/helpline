from __future__ import annotations

import pytest

from helpline.parse import ParseError, parse_model_output


def test_parse_plain_json() -> None:
    result = parse_model_output('{"command": "ls -la", "notes": "hidden files"}', model="m")
    assert result.command == "ls -la"
    assert result.notes == "hidden files"
    assert result.model == "m"


def test_parse_fenced_json() -> None:
    text = """```json
{"command": "pwd", "notes": ""}
```"""
    assert parse_model_output(text).command == "pwd"
    assert parse_model_output(text).notes is None


def test_parse_json_embedded_in_prose() -> None:
    text = 'Sure, use this:\n{"command": "date", "notes": null}\n'
    assert parse_model_output(text).command == "date"


def test_parse_bare_command_fallback() -> None:
    assert parse_model_output("grep -rnw . -e foobar").command == "grep -rnw . -e foobar"


def test_parse_rejects_empty() -> None:
    with pytest.raises(ParseError, match="empty"):
        parse_model_output("  ")


def test_parse_rejects_missing_command() -> None:
    with pytest.raises(ParseError, match="command"):
        parse_model_output('{"notes": "hi"}')


def test_parse_rejects_chatty_prose() -> None:
    with pytest.raises(ParseError):
        parse_model_output("Here is a great idea without a command.")
