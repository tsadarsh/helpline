# helpline

Turn a regular English request into a **shell command for the OS you are on**.

```text
$ helpline find me all the files in the cwd that has the word foobar in its content
grep -rnw . -e "foobar"
```

Helpline does **not** run the command. It prints it so you can read it, edit it, or pipe it yourself.

A local **open-weights** model (via [Ollama](https://ollama.com)) does the translation. Nothing is sent to a cloud API.

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) running locally
- A small coding model, default `qwen2.5-coder:3b` (fast, open weights)

```bash
ollama pull qwen2.5-coder:3b
```

## Install

```bash
python3 -m pip install -e ".[dev]"
```

## Usage

```bash
helpline list directories edited in the last 24 hours bigger than 5MB
helpline --os windows find files containing foobar
helpline --json count lines in all python files
helpline doctor
```

| Flag | Purpose |
| --- | --- |
| `--os {windows,linux,macos}` | Generate for another OS |
| `--shell {posix,powershell}` | Override dialect |
| `--model NAME` | Ollama model (`HELPLINE_MODEL`) |
| `--host URL` | Ollama base URL |
| `--json` | Structured output |
| `-v` / `--verbose` | Print model notes on stderr |

Environment:

- `HELPLINE_MODEL` — default `qwen2.5-coder:3b`
- `HELPLINE_OLLAMA_HOST` or `OLLAMA_HOST` — default `http://127.0.0.1:11434`

## How it chooses commands

1. Detect OS (`win32` → Windows / PowerShell, `darwin` → macOS / BSD userland, otherwise Linux / GNU).
2. Build a strict JSON prompt with OS-specific rules and few-shot examples.
3. Ask the local Ollama chat API (`temperature=0`, `format=json`).
4. Parse `{"command": "...", "notes": "..."}` and print `command`.

## Tests

```bash
python3 -m pytest
```

Network is not required; the Ollama client is mocked.

## Layout

```text
src/helpline/           # installable package
  cli.py                # argparse entry point
  translator.py         # prompt → model → parse
  prompts.py            # OS-specific instructions
  backends/ollama.py    # local HTTP client
tests/                  # unit tests
```
