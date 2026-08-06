# README.md

# AQRuntime PoC v0.9 Documentation Baseline

Version: PoC v0.9

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language models locally.
Version PoC v0.9 introduces GGUF 4-bit Quantization Format support (via `llama.cpp` / GGUF loader integration), ultra-low RAM footprint execution (~2.2 GB RAM for 3B models), GGUF model discovery (`[GGUF-Q4]`), and dual PyTorch/GGUF backend routing.

## 2. Setup

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
aq doctor
```

## 3. Supported Commands

```bash
aq discover [query]
aq pull <model> [--token <token>] [--yes]
aq run <model> [--memory | --no-memory] [--session <name>] [--system <prompt>]
aq ui [--host HOST] [--port PORT] [--no-browser]
aq serve [--host HOST] [--port PORT]
aq doctor
aq login <token>
aq list
aq memory <list|clear|export> [name]
aq remove <model>
aq version
```

## 4. Key Evolution Features in PoC v0.9

- Native GGUF 4-bit / 8-bit model format loader (`src/aqruntime/model/gguf_loader.py`).
- Ultra-low memory footprint (~2.2 GB RAM for 3B models, ~5.5 GB RAM for 8B models).
- GGUF catalog models and `[GGUF-Q4]` tags in discovery & Web UI.
- GGUF hardware threshold calculation (`aq doctor`).
- Dual PyTorch / GGUF backend routing in `ModelManager`.
