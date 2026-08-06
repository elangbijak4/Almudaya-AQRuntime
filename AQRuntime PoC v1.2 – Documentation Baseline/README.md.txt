# README.md

# AQRuntime PoC v1.2 Documentation Baseline

Version: PoC v1.2

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language models locally.
Version PoC v1.2 introduces Smart Download Inspection (`/api/pull/inspect`), Installed Detection, Interactive Resume Modal with cached byte progress bar, and Reset Cache Engine (`/api/pull/reset`).

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

## 4. Key Evolution Features in PoC v1.2

- Smart Download Inspection Engine (`inspect_download_state`).
- 100% Installed Detection Notification.
- Partial Download Detection & Interactive Resume Modal in Web GUI.
- Two User Options: Resume Download vs Reset Cache & Redownload from 0%.
- REST API Endpoints (`/api/pull/inspect` & `/api/pull/reset`).
