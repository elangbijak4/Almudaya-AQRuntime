# README.md

# AQRuntime PoC v2.3 Documentation Baseline

Version: PoC v2.3

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language, vision, and audio models locally.
Version PoC v2.3 introduces Voice Audio & Speech Engine: Microphone Recording (`🎙️`), Text-to-Speech Read Aloud (`🔊`), Audio API Endpoint (`/api/audio/transcribe`), and Audio Catalog Discovery (`aq discover audio`).

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
aq discover [query|nvidia|vision|audio]
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

## 4. Key Evolution Features in PoC v2.3

- Voice Audio & Speech Engine (`AudioProcessor`).
- Live Microphone Voice Input (`🎙️`) and Audio Transcribe API (`POST /api/audio/transcribe`).
- Text-to-Speech Output (`🔊 Read Aloud`) on AI chat bubbles.
- Audio Model Discovery Catalog (`aq discover audio`).
- Living Development History file (`docs/Development_History.md`).
