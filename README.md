# AQRuntime PoC v0.1

AQRuntime is a local CLI runtime for downloading, storing, loading, and running
Hugging Face language models.

## Setup

Use Python 3.10 or newer, create an isolated environment, then install the
project from its root directory:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

The installation creates the `aq` command. Without activation on Windows, use
`.\.venv\Scripts\aq.exe <command>`.

## Commands

```bash
aq version
aq pull TinyLlama/TinyLlama-1.1B-Chat-v1.0
aq list
aq run tinyllama
aq remove tinyllama
```

Downloaded models are saved in `models/`. Runtime configuration is in
`config/runtime.yaml`, and persistent logs are written to `logs/runtime.log`.

## Tests

```bash
python -m unittest discover -s tests -v
```
