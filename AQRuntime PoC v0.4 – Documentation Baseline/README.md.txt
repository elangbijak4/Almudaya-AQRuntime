# README.md

# AQRuntime PoC v0.4 Documentation Baseline

Version: PoC v0.4

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language models locally.
Version PoC v0.4 introduces Gated Model Detection and Hugging Face User Access Token Authentication (`aq login` & `aq pull --token`), helping users seamlessly access models requiring license approvals.

## 2. Setup

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

## 3. Supported Commands

```bash
aq discover [query]
aq login <token>
aq pull <model> [--token <token>]
aq list
aq run <model>
aq remove <model>
aq version
```

## 4. Key Evolution Features in PoC v0.4

- `aq login <token>`: Save Hugging Face User Access Token locally.
- Gated Model detection with step-by-step guidance for accepting license terms.
- `[GATED]` status indicators in `aq discover` output.
- Optional `--token` parameter for `aq pull`.
