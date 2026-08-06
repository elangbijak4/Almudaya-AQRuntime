# README.md

# AQRuntime PoC v2.0 Documentation Baseline

Version: PoC v2.0

Status: Frozen

---

## 1. Purpose

AQRuntime is a lightweight AI Runtime for downloading, storing, loading, and running Hugging Face language models locally.
Version PoC v2.0 introduces the Pluggable Heterogeneous Execution Engine & Hardware Acceleration Provider Architecture (Intel NPU, Intel Arc iGPU/dGPU, OpenVINO, DirectML, CUDA, ONNX, CPU, and Cloud APIs), fallback priority chain, and new CLI commands (`aq runtime list` & `aq runtime info`).

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
aq discover [query|nvidia]
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

## 4. Key Evolution Features in PoC v2.0

- Pluggable Execution Provider System (`src/aqruntime/runtime/providers/`).
- Priority Fallback Chain Engine (`Intel NPU` -> `Intel Arc` -> `OpenVINO` -> `DirectML` -> `CUDA` -> `CPU` -> `Cloud`).
- New CLI commands: `aq runtime list` and `aq runtime info <provider>`.
- Web Control Center GUI Execution Runtime Selector dropdown in Tab 1 and Tab 5.
- REST API Endpoint `GET /api/runtimes`.
