# README.md

# AQRuntime PoC v0.8 Documentation Baseline

Version: PoC v0.8

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language models locally.
Version PoC v0.8 introduces an Integrated Web UI Dashboard (`aq ui`) featuring single-command browser launch, visual model selection, chat interface, custom system prompt editor, hardware monitor, and visual memory management.

## 2. Setup & Web UI

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
aq ui
```

## 3. Supported Commands

```bash
aq ui [--host HOST] [--port PORT] [--no-browser]
aq serve [--host HOST] [--port PORT]
aq doctor
aq discover [query]
aq login <token>
aq pull <model> [--token <token>] [--yes]
aq list
aq run <model> [--memory | --no-memory] [--session <name>] [--system <prompt>]
aq memory <list|clear|export> [name]
aq remove <model>
aq version
```

## 4. Key Evolution Features in PoC v0.8

- Integrated Web UI Dashboard launched via `aq ui`.
- Automatic default web browser launching.
- Dark Glassmorphism Web UI interface (`/ui`).
- Visual model selector, live chat bubble interface, system prompt editor, hardware diagnostic monitor, and memory manager.
- REST API extensions (`/api/doctor`, `/api/memory`, `/api/memory/clear`, `/api/memory/export`).
