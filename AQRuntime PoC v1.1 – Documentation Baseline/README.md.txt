# README.md

# AQRuntime PoC v1.1 Documentation Baseline

Version: PoC v1.1

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language models locally.
Version PoC v1.1 introduces Background Async Model Pulling (`/api/pull` & `/api/pull/status`), live progress polling, auto-resume quota safety, and real-time GUI download progress modals.

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

## 4. Key Evolution Features in PoC v1.1

- Async Background Model Download Engine in `ModelManager`.
- Real-Time Progress Status endpoint (`GET /api/pull/status`).
- Auto-resume download quota safety guarantee.
- Real-Time Download Progress Modal in Web GUI (`index.html`).
