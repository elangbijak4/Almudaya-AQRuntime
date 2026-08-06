# README.md

# AQRuntime PoC v1.5 Documentation Baseline

Version: PoC v1.5

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language models locally.
Version PoC v1.5 introduces Cross-Model Memory Continuity & New Chat Session Control (`copy_session`, `get_session_messages`, `POST /api/memory/copy`, `GET /api/memory/session`, `➕ New Chat` button, and Model Switch Modal).

## 2. Setup

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

## 4. Key Evolution Features in PoC v1.5

- "➕ New Chat" Button next to Model Selection dropdown in Web Control Center.
- Model Switch Modal: Option to Transfer Topic to New Model vs Start Fresh Chat.
- REST API Endpoints (`GET /api/memory/session` & `POST /api/memory/copy`).
- Automatic chat window synchronization when switching models in UI.
