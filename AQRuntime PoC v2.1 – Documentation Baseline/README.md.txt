# README.md

# AQRuntime PoC v2.1 Documentation Baseline

Version: PoC v2.1

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language models locally.
Version PoC v2.1 introduces GitHub Release Edition features: Speed & Performance Monitor (`tokens_per_second`), Document & Code Reader (File Attachment `📎`), Persona Preset Library, and 1-Click Chat Exporter.

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
aq run <model> [--runtime <provider>] [--memory | --no-memory] [--session <name>] [--system <prompt>]
aq runtime list
aq runtime info <provider>
aq memory <list|clear|export> [name]
aq remove <model>
aq version
```

## 4. Key Evolution Features in PoC v2.1

- Speed & Performance Telemetry Monitor (`tokens_per_second`, `latency_seconds`, `total_seconds`).
- Document & Code Reader File Attachment (`📎`) button for `.py`, `.txt`, `.json`, `.md`, `.log`, `.csv`.
- Persona Presets Library dropdown in Tab 1 sidebar.
- 1-Click Chat Exporter (`📥 Export Chat (.md)`).
- Living Development History file (`docs/Development_History.md`).
