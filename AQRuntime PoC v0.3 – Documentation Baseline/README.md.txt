# README.md

# AQRuntime PoC v0.3 Documentation Baseline

Version: PoC v0.3

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language models locally.
Version PoC v0.3 introduces Smart Hardware Detection & Live/Offline Model Discovery (`aq discover`), automatically matching online and cached models with host computing specs.

## 2. Setup

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

## 3. Supported Commands

```bash
aq discover
aq pull <model>
aq list
aq run <model>
aq remove <model>
aq version
```

## 4. Key Evolution Features in PoC v0.3

- `aq discover`: Detects host CPU and RAM specs and lists compatible models.
- Live internet discovery with automatic fallback to bundled permanent cache (`config/catalog_cache.json`).
- Sanitized model storage keys (`owner-repository`).
- RAM-efficient model loading.
