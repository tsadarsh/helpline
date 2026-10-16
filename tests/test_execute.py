from __future__ import annotations

from types import SimpleNamespace

import pytest

from helpline.execute import ExecError, run_command
from helpline.types import ShellFamily


def test_posix_runs_via_shell() -> None:
    seen: dict[str, object] = {}

    def runner(command, *, shell=False, executable=None):
        seen["command"] = command
        seen["shell"] = shell
        seen["executable"] = executable
        return SimpleNamespace(returncode=7)

    code = run_command("ls ~", shell=ShellFamily.POSIX, runner=runner)
    assert code == 7
    assert seen["command"] == "ls ~"
    assert seen["shell"] is True
    assert seen["executable"]


def test_powershell_uses_argv() -> None:
    seen: dict[str, object] = {}

    def runner(argv):
        seen["argv"] = list(argv)
        return SimpleNamespace(returncode=0)

    code = run_command("Get-ChildItem ~", shell=ShellFamily.POWERSHELL, runner=runner)
    assert code == 0
    argv = seen["argv"]
    assert argv[-2:] == ["-Command", "Get-ChildItem ~"]
    assert "-NoProfile" in argv


def test_empty_command_rejected() -> None:
    with pytest.raises(ExecError, match="empty"):
        run_command("  ", shell=ShellFamily.POSIX, runner=lambda *a, **k: None)
