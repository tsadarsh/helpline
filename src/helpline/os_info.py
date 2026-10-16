from __future__ import annotations

import sys

from helpline.types import ShellFamily, TargetOS


def detect_os(platform: str | None = None) -> TargetOS:
    """Map a sys.platform-style string to a supported TargetOS."""
    name = (platform if platform is not None else sys.platform).lower()
    if name.startswith("win"):
        return TargetOS.WINDOWS
    if name == "darwin":
        return TargetOS.MACOS
    return TargetOS.LINUX


def detect_shell(target_os: TargetOS | None = None) -> ShellFamily:
    """Choose the default command dialect for the given (or current) OS."""
    return ShellFamily.default_for(target_os if target_os is not None else detect_os())
