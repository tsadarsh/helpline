from __future__ import annotations

from helpline.prompts import build_prompt, examples_for
from helpline.types import ShellFamily, TargetOS, TranslationRequest


def _request(os: TargetOS, query: str = "list files") -> TranslationRequest:
    return TranslationRequest(query=query, target_os=os, shell=ShellFamily.default_for(os))


def test_prompt_includes_os_rules_and_query() -> None:
    prompt = build_prompt(_request(TargetOS.MACOS, "find me all the files with foobar"))
    assert "macos" in prompt.system.lower()
    assert "BSD" in prompt.system
    assert "PowerShell" in prompt.system
    assert prompt.user == "find me all the files with foobar"


def test_linux_prompt_asks_for_gnu_tools() -> None:
    prompt = build_prompt(_request(TargetOS.LINUX))
    assert "GNU" in prompt.system
    assert "Do not emit PowerShell" in prompt.system


def test_windows_prompt_asks_for_powershell() -> None:
    prompt = build_prompt(_request(TargetOS.WINDOWS))
    assert "PowerShell" in prompt.system
    assert "Get-ChildItem" in prompt.system


def test_examples_cover_user_stories() -> None:
    for os in TargetOS:
        queries = [query for query, _command in examples_for(os)]
        assert any("foobar" in query for query in queries)
        assert any("5MB" in query or "5mb" in query.lower() for query in queries)
        assert any("home dir" in query for query in queries)

    macos = dict(examples_for(TargetOS.MACOS))
    assert macos["list all files in my home dir"] == "ls ~"


def test_prompt_warns_against_glued_tilde() -> None:
    prompt = build_prompt(_request(TargetOS.MACOS, "list all files in my home dir"))
    assert "never 'ls ~l'" in prompt.system


def test_empty_query_rejected() -> None:
    import pytest

    with pytest.raises(ValueError, match="empty"):
        build_prompt(_request(TargetOS.LINUX, "   "))
