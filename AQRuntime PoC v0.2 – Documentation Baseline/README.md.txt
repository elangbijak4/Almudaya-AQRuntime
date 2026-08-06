# README.md

# AQRuntime PoC v0.2 Documentation Baseline

Version: PoC v0.2

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language models locally.
Version PoC v0.2 introduces full model repository name resolution to prevent directory collisions when managing multiple models from the same owner, improved RAM efficiency on 16 GB RAM systems, and enhanced error handling.

## 2. Setup

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

## 3. Supported Commands

```bash
aq pull <model>
aq list
aq run <model>
aq remove <model>
aq version
```

## 4. Key Evolution Features in PoC v0.2

- Sanitized model storage keys (e.g., `google/gemma-2-2b-it` -> `google-gemma-2-2b-it`).
- Backward compatibility for short model folder aliases.
- Optimized RAM memory consumption during model loading (`low_cpu_mem_usage` and `torch_dtype` auto-selection).
- Detailed runtime logging and user-friendly error messages for missing models or download issues.
