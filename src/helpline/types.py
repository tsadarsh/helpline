from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TargetOS(str, Enum):
    """Operating system whose native command dialect should be produced."""

    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"

    @classmethod
    def from_name(cls, value: str) -> TargetOS:
        key = value.strip().lower()
        aliases = {
            "win": cls.WINDOWS,
            "win32": cls.WINDOWS,
            "windows": cls.WINDOWS,
            "linux": cls.LINUX,
            "gnu": cls.LINUX,
            "darwin": cls.MACOS,
            "mac": cls.MACOS,
            "macos": cls.MACOS,
            "osx": cls.MACOS,
        }
        try:
            return aliases[key]
        except KeyError as exc:
            valid = ", ".join(sorted({item.value for item in cls}))
            raise ValueError(f"Unknown OS {value!r}. Expected one of: {valid}") from exc


class ShellFamily(str, Enum):
    """Command dialect to emit for the target OS."""

    POSIX = "posix"
    POWERSHELL = "powershell"

    @classmethod
    def default_for(cls, target_os: TargetOS) -> ShellFamily:
        if target_os is TargetOS.WINDOWS:
            return cls.POWERSHELL
        return cls.POSIX


@dataclass(frozen=True)
class TranslationRequest:
    query: str
    target_os: TargetOS
    shell: ShellFamily


@dataclass(frozen=True)
class TranslationResult:
    command: str
    notes: str | None = None
    model: str | None = None
