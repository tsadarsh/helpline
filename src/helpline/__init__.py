"""Helpline: natural-language to OS-specific shell commands."""

__version__ = "0.1.0"

from helpline.types import ShellFamily, TargetOS, TranslationRequest, TranslationResult

__all__ = [
    "ShellFamily",
    "TargetOS",
    "TranslationRequest",
    "TranslationResult",
    "__version__",
]
