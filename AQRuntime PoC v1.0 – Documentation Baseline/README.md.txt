# README.md

# AQRuntime PoC v1.0 Documentation Baseline

Version: PoC v1.0

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language models locally.
Version PoC v1.0 introduces the AQRuntime Desktop Control Center, a complete modular GUI representing the entire CLI suite (Chat, Discover & Pull 1-Click, Installed Models Manager 1-Click Delete, Hardware Doctor Gauges, and HF Token Auth & Settings) alongside chat window scrolling fixes.

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

## 4. Key Evolution Features in PoC v1.0

- Modular Desktop Control Center Web GUI (`aq ui`) with 5 navigation tabs.
- Fix chat window scrolling behavior (`height: 0; flex-grow: 1; overflow-y: auto`).
- Visual Model Discovery & 1-Click Pulling (`/api/discover` & `/api/pull`).
- Installed Model Manager & 1-Click Removal (`/api/remove`).
- Hardware Doctor Gauges comparing FP16 (5.2B) vs GGUF 4-Bit (19.2B) safe limits.
- HF Access Token manager (`/api/login`) and Memory Session Exporter.
