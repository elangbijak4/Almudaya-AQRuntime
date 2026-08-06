# README.md

# AQRuntime PoC v1.4 Documentation Baseline

Version: PoC v1.4

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language models locally.
Version PoC v1.4 fixes GGUF model inference engine execution (`_generate_gguf`), enabling smooth chat completion for GGUF 4-bit models without PyTorch runtime crashes.

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

## 4. Key Evolution Features in PoC v1.4

- GGUF Dual Inference Routing (`_generate_gguf`).
- Native GGUF text generation for `GGUFModelWrapper` and `SimulatedGGUFModel`.
- Fixes PyTorch `self.tokenizer(...)` TypeError crashes on GGUF models.
