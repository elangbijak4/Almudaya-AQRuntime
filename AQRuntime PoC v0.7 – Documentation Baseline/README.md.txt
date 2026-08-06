# README.md

# AQRuntime PoC v0.7 Documentation Baseline

Version: PoC v0.7

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language models locally.
Version PoC v0.7 introduces a Local HTTP REST API Server (`aq serve`) supporting OpenAI-compatible endpoints (`/v1/chat/completions`, `/v1/models`, `/health`), and Custom System Prompt configuration.

## 2. Setup & Server

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
aq serve --port 8000
```

## 3. Supported Commands

```bash
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

## 4. Key Evolution Features in PoC v0.7

- Local HTTP REST API Server (`aq serve`) supporting OpenAI-compatible `/v1/chat/completions` and `/v1/models`.
- Custom system prompt overriding (`aq run model --system "Custom prompt"`).
- Health check endpoint `/health`.
