from __future__ import annotations

from dataclasses import dataclass

from helpline.types import ShellFamily, TargetOS, TranslationRequest

JSON_SCHEMA_HINT = '{"command": "<exact command>", "notes": "<optional one-line caveat or empty string>"}'


@dataclass(frozen=True)
class Prompt:
    system: str
    user: str


_OS_RULES: dict[TargetOS, str] = {
    TargetOS.LINUX: (
        "Target: Linux with GNU coreutils, GNU find, GNU grep, bash-compatible syntax.\n"
        "Prefer portable POSIX where it is equally clear; otherwise use GNU flags "
        "(-printf, --max-depth, GNU date).\n"
        "Do not use macOS/BSD-only flags (stat -f, find -print0 with BSD semantics as the only option).\n"
        "Do not emit PowerShell."
    ),
    TargetOS.MACOS: (
        "Target: macOS with BSD userland (BSD find, BSD grep, BSD sed, BSD stat).\n"
        "Do not use GNU-only flags such as find -printf, grep -P, or sed -r unless you "
        "explicitly call g-prefixed GNU tools that may not be installed.\n"
        "zsh/bash syntax is fine. Do not emit PowerShell."
    ),
    TargetOS.WINDOWS: (
        "Target: Windows PowerShell 5.1+ / PowerShell 7.\n"
        "Emit PowerShell, not bash, not cmd.exe internal syntax unless a well-known "
        "external binary (git, curl) is clearly the right tool.\n"
        "Use cmdlets (Get-ChildItem, Select-String, Where-Object) for filesystem and text search."
    ),
}

_EXAMPLES: dict[TargetOS, tuple[tuple[str, str], ...]] = {
    TargetOS.LINUX: (
        (
            "list all files in my home dir",
            "ls ~",
        ),
        (
            "find me all the files in the cwd that has the word foobar in its content",
            'grep -rnw . -e "foobar"',
        ),
        (
            "list directories that were edited in the last 24 hours and are bigger than 5MB",
            "find . -mindepth 1 -maxdepth 1 -type d -mtime -1 -exec sh -c "
            '\'size=$(du -sm "$1" | cut -f1); [ "$size" -gt 5 ] && echo "$1 ($size MB)"\' _ {} \\;',
        ),
    ),
    TargetOS.MACOS: (
        (
            "list all files in my home dir",
            "ls ~",
        ),
        (
            "find me all the files in the cwd that has the word foobar in its content",
            'grep -rnw . -e "foobar"',
        ),
        (
            "list directories that were edited in the last 24 hours and are bigger than 5MB",
            "find . -mindepth 1 -maxdepth 1 -type d -mtime -1 -exec sh -c "
            '\'size=$(du -sm "$1" | cut -f1); [ "$size" -gt 5 ] && echo "$1 ($size MB)"\' _ {} \\;',
        ),
    ),
    TargetOS.WINDOWS: (
        (
            "list all files in my home dir",
            "Get-ChildItem -Force $HOME",
        ),
        (
            "find me all the files in the cwd that has the word foobar in its content",
            "Get-ChildItem -Recurse -File | Select-String -Pattern 'foobar'",
        ),
        (
            "list directories that were edited in the last 24 hours and are bigger than 5MB",
            "$cutoff = (Get-Date).AddHours(-24); Get-ChildItem -Directory | "
            "Where-Object { $_.LastWriteTime -gt $cutoff -and "
            "((Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | "
            "Measure-Object Length -Sum).Sum -gt 5MB) } | "
            "ForEach-Object { '{0} ({1:N1} MB)' -f $_.Name, "
            "(((Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | "
            "Measure-Object Length -Sum).Sum) / 1MB) }",
        ),
    ),
}


def build_prompt(request: TranslationRequest) -> Prompt:
    if not request.query.strip():
        raise ValueError("Query must not be empty")

    examples = "\n".join(
        f"User: {query}\nAssistant: {{\"command\": {_json_escape(command)}, \"notes\": \"\"}}"
        for query, command in _EXAMPLES[request.target_os]
    )
    system = (
        "You convert a human's natural-language request into a single shell command.\n"
        "Return ONLY valid JSON matching this shape (no markdown, no extra keys):\n"
        f"{JSON_SCHEMA_HINT}\n\n"
        f"Operating system: {request.target_os.value}\n"
        f"Shell dialect: {request.shell.value}\n"
        f"{_OS_RULES[request.target_os]}\n\n"
        "Rules:\n"
        "- One command only. Pipelines, &&, ||, and ; chains are allowed when needed.\n"
        "- Prefer tools that ship with the OS. Do not invent flags.\n"
        "- ~ is the home directory. Never glue letters onto it (use 'ls ~' or 'ls $HOME', "
        "never 'ls ~l').\n"
        "- Do not add destructive flags (rm -rf, Remove-Item -Recurse -Force, format, "
        "dd of=) unless the user clearly asked to delete or overwrite.\n"
        "- Do not wrap the command in comments or an explanation outside JSON.\n"
        "- If the request is ambiguous, pick the most common interpretation and mention "
        "the assumption in notes.\n"
        "- If the task cannot be done with a command, still return JSON with command "
        "set to an empty string and explain in notes.\n\n"
        f"Examples:\n{examples}"
    )
    user = request.query.strip()
    return Prompt(system=system, user=user)


def _json_escape(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def examples_for(target_os: TargetOS) -> tuple[tuple[str, str], ...]:
    return _EXAMPLES[target_os]


def default_shell_label(shell: ShellFamily) -> str:
    return shell.value
