# README.md

# AQRuntime PoC v0.6 Documentation Baseline

Version: PoC v0.6

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language models locally.
Version PoC v0.6 introduces Pre-Installation Hardware Diagnostics & Minimal Model Guidance, as well as Pre-Download File Size Warnings and Interactive Confirmation Prompts for `aq pull`.

## 2. Setup & Diagnostics

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
aq doctor
```

## 3. Supported Commands

```bash
aq doctor
aq discover [query]
aq login <token>
aq pull <model> [--token <token>] [--yes]
aq list
aq run <model> [--memory | --no-memory] [--session <name>]
aq memory <list|clear|export> [name]
aq remove <model>
aq version
```

## 4. Key Evolution Features in PoC v0.6

- Pre-installation hardware diagnostic check & minimal model recommendation (`aq doctor`).
- Interactive abort option if system hardware falls below minimum requirements (4.0 GB RAM).
- Pre-download repository file size estimation and network warning.
- Interactive user confirmation prompt before downloading models (`Proceed with download? [y/N]`).
- `--yes` / `-y` flag to bypass confirmation prompt for automated scripts.
