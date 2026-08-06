# README.md

# AQRuntime PoC v1.3 Documentation Baseline

Version: PoC v1.3

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language models locally.
Version PoC v1.3 introduces Sleep Prevention & OS Power Lock Engine (`PowerLockManager`), preventing host operating systems and displays from sleep/hibernate while downloads are active.

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

## 4. Key Evolution Features in PoC v1.3

- Sleep Prevention & OS Power Lock Engine (`SetThreadExecutionState`).
- Browser Screen Wake Lock API (`navigator.wakeLock`).
- Live GUI Protection Badge (`🛡️ Sleep Lock Active`).
- Cross-platform safe power lock management.
