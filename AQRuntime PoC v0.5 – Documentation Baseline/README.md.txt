# README.md

# AQRuntime PoC v0.5 Documentation Baseline

Version: PoC v0.5

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language models locally.
Version PoC v0.5 introduces a Dual-Tier Conversation Memory System (Short-Term Memory sliding window & Long-Term Memory JSON persistence), allowing models to retain context across session restarts under user control.

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
aq run <model> [--memory | --no-memory] [--session <name>]
aq memory <list|clear|export> [name]
aq remove <model>
aq version
```

## 4. Key Evolution Features in PoC v0.5

- Dual-Tier Conversation Memory (Short-Term Memory sliding window & Long-Term Memory persistent JSON files).
- User memory controls (`--memory`, `--no-memory`, `--session <name>`).
- Memory management subcommands (`aq memory list`, `aq memory clear`, `aq memory export`).
