from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from helpline import __version__
from helpline.backends.ollama import OllamaBackend, OllamaError, model_is_installed
from helpline.config import load_settings
from helpline.os_info import detect_os, detect_shell
from helpline.parse import ParseError
from helpline.translator import Translator
from helpline.types import ShellFamily, TargetOS, TranslationRequest


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args, rest = parser.parse_known_args(list(argv) if argv is not None else None)

    if rest == ["doctor"]:
        return _cmd_doctor(args)

    query = " ".join(rest).strip()
    if not query:
        parser.error("missing natural-language query (or run: helpline doctor)")

    try:
        target_os = TargetOS.from_name(args.os) if args.os else detect_os()
        if args.shell:
            shell = ShellFamily(args.shell)
        else:
            shell = detect_shell(target_os)
        settings = load_settings(model=args.model, ollama_host=args.host)
        translator = Translator(OllamaBackend(settings))
        result = translator.translate(
            TranslationRequest(query=query, target_os=target_os, shell=shell)
        )
    except (ValueError, ParseError, OllamaError) as exc:
        print(f"helpline: {exc}", file=sys.stderr)
        return 1

    if args.json:
        payload = {
            "command": result.command,
            "notes": result.notes,
            "os": target_os.value,
            "shell": shell.value,
            "model": result.model,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(result.command)
        if args.verbose and result.notes:
            print(result.notes, file=sys.stderr)
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    settings = load_settings(model=args.model, ollama_host=args.host)
    backend = OllamaBackend(settings)
    try:
        tags = backend.ping()
    except OllamaError as exc:
        print(f"helpline: {exc}", file=sys.stderr)
        return 1

    names = [str(item.get("name", "")) for item in tags.get("models", [])]
    print(f"Ollama reachable at {settings.ollama_host}")
    print(f"Configured model: {settings.model}")
    print(f"Detected OS: {detect_os().value}")
    if model_is_installed(settings.model, names):
        print("Model is available locally.")
        return 0
    print(f"Model not found. Installed: {', '.join(names) or '(none)'}")
    print(f"Pull it with: ollama pull {settings.model}")
    return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="helpline",
        description=(
            "Translate a natural-language request into a shell command for this OS. "
            "Requires a local Ollama server and an open-weights model."
        ),
    )
    parser.add_argument("--version", action="version", version=f"helpline {__version__}")
    parser.add_argument(
        "--os",
        help="Override detected OS (windows, linux, macos).",
    )
    parser.add_argument(
        "--shell",
        choices=[item.value for item in ShellFamily],
        help="Override command dialect (default: powershell on Windows, posix elsewhere).",
    )
    parser.add_argument(
        "--model",
        help="Ollama model name (default: HELPLINE_MODEL or qwen2.5-coder:3b).",
    )
    parser.add_argument(
        "--host",
        help="Ollama base URL (default: HELPLINE_OLLAMA_HOST, OLLAMA_HOST, or http://127.0.0.1:11434).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print command, notes, OS, and model as JSON.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print model notes to stderr.",
    )
    parser.epilog = "Examples: helpline list files modified today | helpline doctor"
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
