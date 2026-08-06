# README.md

# AQRuntime PoC v1.6 Documentation Baseline

Version: PoC v1.6

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language models locally.
Version PoC v1.6 introduces GATED Error Diagnostics, Download Completion Toast & Auto-Switch to Chat, NVIDIA Open Models Discovery Catalog, and the living Development History Document (`docs/Development_History.md`).

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
aq discover [query|nvidia]
aq login <token>
aq pull <model> [--token <token>] [--yes]
aq list
aq run <model> [--memory | --no-memory] [--session <name>] [--system <prompt>]
aq memory <list|clear|export> [name]
aq remove <model>
aq version
```

## 4. Key Evolution Features in PoC v1.6

- Friendly GATED Model Error Diagnostic instructions in chat (`aq login <token>`).
- Download Status Terminal Hint banner in Web UI.
- Download Completion Toast Notification & Auto-Switch to Chat tab.
- NVIDIA Open Models Discovery Provider (`aq discover nvidia`) & UI Filter.
- Living Development History log (`docs/Development_History.md`).
