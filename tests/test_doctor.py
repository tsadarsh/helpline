from __future__ import annotations

from types import SimpleNamespace

from helpline import cli
from helpline.backends.ollama import OllamaError


def test_doctor_success(monkeypatch, capsys) -> None:
    settings = SimpleNamespace(model="qwen2.5-coder:3b", ollama_host="http://127.0.0.1:11434")
    monkeypatch.setattr(cli, "load_settings", lambda **kwargs: settings)

    class Fake:
        def __init__(self, _settings: object) -> None:
            pass

        def ping(self) -> dict:
            return {"models": [{"name": "qwen2.5-coder:3b"}]}

    monkeypatch.setattr(cli, "OllamaBackend", Fake)
    code = cli.main(["doctor"])
    out = capsys.readouterr().out
    assert code == 0
    assert "reachable" in out
    assert "available locally" in out


def test_doctor_missing_model(monkeypatch, capsys) -> None:
    settings = SimpleNamespace(model="qwen2.5-coder:3b", ollama_host="http://127.0.0.1:11434")
    monkeypatch.setattr(cli, "load_settings", lambda **kwargs: settings)

    class Fake:
        def __init__(self, _settings: object) -> None:
            pass

        def ping(self) -> dict:
            return {"models": []}

    monkeypatch.setattr(cli, "OllamaBackend", Fake)
    code = cli.main(["doctor"])
    out = capsys.readouterr().out
    assert code == 2
    assert "ollama pull" in out


def test_doctor_offline(monkeypatch, capsys) -> None:
    settings = SimpleNamespace(model="qwen2.5-coder:3b", ollama_host="http://127.0.0.1:11434")
    monkeypatch.setattr(cli, "load_settings", lambda **kwargs: settings)

    class Fake:
        def __init__(self, _settings: object) -> None:
            pass

        def ping(self) -> dict:
            raise OllamaError("down")

    monkeypatch.setattr(cli, "OllamaBackend", Fake)
    code = cli.main(["doctor"])
    err = capsys.readouterr().err
    assert code == 1
    assert "down" in err
