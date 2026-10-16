from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Callable, Sequence
from typing import Any

from helpline.types import ShellFamily

Runner = Callable[..., Any]


class ExecError(RuntimeError):
    """The generated command could not be started."""


def run_command(
    command: str,
    *,
    shell: ShellFamily,
    runner: Runner | None = None,
) -> int:
    """Run the translated command with the user's stdout/stdin/stderr.

    Returns the command's process exit code.
    """
    if not command.strip():
        raise ExecError("Refusing to run an empty command")

    run = runner or subprocess.run
    if shell is ShellFamily.POWERSHELL:
        completed = run(_powershell_argv(command))
    else:
        completed = run(
            command,
            shell=True,
            executable=_posix_shell(),
        )
    return int(getattr(completed, "returncode", 0))


def _powershell_argv(command: str) -> Sequence[str]:
    return [_powershell_executable(), "-NoProfile", "-NonInteractive", "-Command", command]


def _powershell_executable() -> str:
    for name in ("pwsh", "powershell"):
        found = shutil.which(name)
        if found:
            return found
    return "powershell"


def _posix_shell() -> str:
    return os.environ.get("SHELL") or "/bin/sh"
