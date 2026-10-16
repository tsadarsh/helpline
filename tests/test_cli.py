from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from helpline import cli
from helpline.types import TranslationResult
from tests.helpers import FakeBackend


class _FakeTranslator:
    def __init__(self, result: TranslationResult) -> None:
        self.result = result
        self.request = None

    def translate(self, request: object) -> TranslationResult:
        self.request = request
        return self.result


def _patch_translator(monkeypatch, fake: _FakeTranslator) -> None:
    monkeypatch.setattr(cli, "load_settings", lambda **kwargs: SimpleNamespace())
    monkeypatch.setattr(cli, "OllamaBackend", lambda settings: FakeBackend("{}"))
    monkeypatch.setattr(cli, "Translator", lambda backend: fake)


def test_cli_runs_command(monkeypatch, capsys) -> None:
    result = TranslationResult(command='grep -rnw . -e "foobar"', notes=None, model="m")
    fake = _FakeTranslator(result)
    _patch_translator(monkeypatch, fake)
    called: dict[str, object] = {}

    def fake_run(command, *, shell):
        called["command"] = command
        called["shell"] = shell
        return 0

    monkeypatch.setattr(cli, "run_command", fake_run)

    code = cli.main(["--os", "macos", "find", "me", "all", "the", "files", "with", "foobar"])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out == ""
    assert called["command"] == 'grep -rnw . -e "foobar"'
    assert fake.request is not None
    assert fake.request.target_os.value == "macos"


def test_cli_print_does_not_run(monkeypatch, capsys) -> None:
    result = TranslationResult(command="ls ~", notes=None, model="m")
    fake = _FakeTranslator(result)
    _patch_translator(monkeypatch, fake)

    def boom(*_args, **_kwargs):
        raise AssertionError("should not execute")

    monkeypatch.setattr(cli, "run_command", boom)

    code = cli.main(["--print", "list", "all", "files", "in", "my", "home", "dir"])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.strip() == "ls ~"


def test_cli_json(monkeypatch, capsys) -> None:
    result = TranslationResult(command="Get-ChildItem", notes="PowerShell", model="m")
    fake = _FakeTranslator(result)
    _patch_translator(monkeypatch, fake)

    def boom(*_args, **_kwargs):
        raise AssertionError("json mode should not execute")

    monkeypatch.setattr(cli, "run_command", boom)

    code = cli.main(["--json", "--os", "windows", "list", "files"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["command"] == "Get-ChildItem"
    assert payload["os"] == "windows"
    assert payload["shell"] == "powershell"


def test_cli_missing_query_exits() -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main([])
    assert exc.value.code == 2


def test_cli_backend_error(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "load_settings", lambda **kwargs: SimpleNamespace())

    class Boom:
        def __init__(self, settings: object) -> None:
            pass

        def complete(self, prompt: object) -> str:
            raise cli.OllamaError("offline")

    monkeypatch.setattr(cli, "OllamaBackend", Boom)
    code = cli.main(["list", "files"])
    captured = capsys.readouterr()
    assert code == 1
    assert "offline" in captured.err
