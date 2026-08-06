# README.md

# AQRuntime PoC v2.4 Documentation Baseline

Version: PoC v2.4

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language, vision, and audio models locally.
Version PoC v2.4 introduces GitHub Final Release Edition: Explicit `aq help` CLI Command, Dynamic Max Output Tokens Control (`64` to `8192` tokens), Quantization Precision Level Badges (`Q4_K_M`, `Q5_K_M`, `Q8_0`, `FP16`), and Full Offline Mode Verification.

## 2. Setup

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
aq ui
```

## 3. Supported Commands

```bash
aq help
aq ui [--host HOST] [--port PORT] [--no-browser]
aq serve [--host HOST] [--port PORT]
aq doctor
aq discover [query|nvidia|vision|audio]
aq login <token>
aq pull <model> [--token <token>] [--yes]
aq list
aq run <model> [--runtime <provider>] [--max-tokens <num>] [--memory | --no-memory] [--session <name>] [--system <prompt>]
aq runtime list
aq runtime info <provider>
aq memory <list|clear|export> [name]
aq remove <model>
aq version
```

## 4. Key Evolution Features in PoC v2.4

- Explicit `aq help` CLI Command displaying formatted user manual and parameter guide.
- Dynamic Max Output Tokens Control (`max_tokens` up to 8192 tokens) in Web GUI and CLI.
- Quantization Precision Level Badges (`Q4_K_M`, `Q5_K_M`, `Q8_0`, `FP16`).
- Full Offline Mode Execution Verification.
- Living Development History file (`docs/Development_History.md`).
