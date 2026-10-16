from __future__ import annotations

import pytest

from helpline.os_info import detect_os, detect_shell
from helpline.types import ShellFamily, TargetOS


@pytest.mark.parametrize(
    ("platform", "expected"),
    [
        ("win32", TargetOS.WINDOWS),
        ("Windows", TargetOS.WINDOWS),
        ("darwin", TargetOS.MACOS),
        ("linux", TargetOS.LINUX),
        ("linux2", TargetOS.LINUX),
        ("freebsd13", TargetOS.LINUX),
    ],
)
def test_detect_os(platform: str, expected: TargetOS) -> None:
    assert detect_os(platform) == expected


@pytest.mark.parametrize(
    ("target", "shell"),
    [
        (TargetOS.WINDOWS, ShellFamily.POWERSHELL),
        (TargetOS.LINUX, ShellFamily.POSIX),
        (TargetOS.MACOS, ShellFamily.POSIX),
    ],
)
def test_detect_shell(target: TargetOS, shell: ShellFamily) -> None:
    assert detect_shell(target) == shell


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("mac", TargetOS.MACOS),
        ("osx", TargetOS.MACOS),
        ("win", TargetOS.WINDOWS),
        ("GNU", TargetOS.LINUX),
    ],
)
def test_from_name_aliases(name: str, expected: TargetOS) -> None:
    assert TargetOS.from_name(name) is expected


def test_from_name_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="Unknown OS"):
        TargetOS.from_name("amiga")
