# AQRuntime User Guide & Manual

**Version**: PoC v2.4 (Release 2.4.0) - GitHub Final Release Edition  
**Category**: Local AI Model Runtime Infrastructure  
**Target Systems**: Windows, Linux, macOS  

---

## Executive Overview

**AQRuntime** is a lightweight, high-performance local AI runtime for downloading, storing, discovering, and executing Large Language Models (LLMs), Vision models, and Voice Audio models locally on personal computers without cloud dependencies.

### Key Capabilities

- **Explicit CLI Help Guide (`aq help`)**: Formatted reference command manual explaining all 15+ CLI subcommands and parameter flags.
- **Dynamic Max Output Tokens Control (`max_tokens`)**: Configurable generation length slider (`64` to `8192` tokens) in Web GUI and `--max-tokens` CLI flag for producing long-form text documents.
- **Quantization Precision Level Badges (`Q4_K_M`, `Q5_K_M`, `Q8_0`, `FP16`)**: Tagged GGUF quantization levels explicitly displayed in CLI `aq list` and Web UI Model Hub / Installed cards.
- **Voice Audio Speech-to-Text (`🎙️`)**: Live Microphone Recorder Button (`🔴 Recording...`) and REST API (`POST /api/audio/transcribe`) for converting speech audio to text.
- **Text-to-Speech Read Aloud (`🔊`)**: Read assistant responses aloud with natural human voice using Web Speech Synthesis API (`window.speechSynthesis`).
- **Audio Discovery Catalog (`aq discover audio`)**: Dedicated CLI query filter and Web UI Model Hub filter button (**`🎙️ Audio Models`**) for open-source speech models (`openai/whisper-tiny` ~390 MB RAM).
- **Speed & Performance Monitor Telemetry**: Live tokens per second (`tokens_per_second`) and latency calculation displayed as performance badges under model responses (`⚡ 18.5 tok/s • 0.42s latency`).
- **Document & Code Reader File Attachment (`📎`)**: Attach local text files (`.py`, `.txt`, `.json`, `.md`, `.log`, `.csv`) directly into chat prompts via HTML5 `FileReader`.
- **Multimodal Vision Engine (`🖼️`)**: Image Upload (`.png`, `.jpg`, `.jpeg`, `.webp`), Live Preview Canvas, and OpenAI Base64 Multimodal API support.
- **Persona Preset Library**: Quick-select System Prompt gallery in Tab 1 sidebar (Default Assistant, Python Coding Expert, Indonesian Translator, Technical Content Editor, Science Scholar).
- **1-Click Chat Exporter (`📥 Export Chat (.md)`)**: Instantly download active chat logs to formatted Markdown files.
- **Heterogeneous Hardware Acceleration Provider Engine**: Modular execution providers (`src/aqruntime/runtime/providers/`) supporting `cpu`, `intel_openvino` (Intel NPU & Intel Arc iGPU), `directml`, `cuda`, `onnx`, `cloud_openai`, and `cloud_huggingface`.
- **Automatic Priority Fallback Chain**: Smart priority execution chain (`Intel NPU` -> `Intel Arc` -> `OpenVINO` -> `DirectML` -> `CUDA` -> `CPU` -> `Cloud`).
- **Hardware Runtime Diagnostics (`aq runtime list` & `aq runtime info <provider>`)**: Detailed CLI inspection of installed hardware acceleration drivers and task capabilities (LLM, Embedding, Vision).
- **Web Control Center GUI Execution Runtime Selector**: Dynamic hardware provider dropdown in Tab 1 (Chat & Infer) and Tab 5 (Settings).
- **GATED Model Diagnostics & Missing Model Guidance**: Formats Hugging Face authorization errors (`GatedRepoError`) and missing model errors into step-by-step Indonesian guidance in chat.
- **Download Completion Toast & Auto-Switch**: Toast notification upon 100% download completion, auto-setting the active model and switching directly to Tab 1 (Chat & Infer).
- **NVIDIA Open Models Discovery Catalog (`aq discover nvidia`)**: Dedicated CLI discovery provider and Web UI Model Hub filter button for NVIDIA open models.
- **Living Development History Document (`docs/Development_History.md`)**: Full chronological history tracking of all evolution cycles.
- **Cross-Model Memory Continuity & New Chat Control**: Transfer conversation topics across different installed models or start fresh with 1-click via "➕ New Chat".
- **GGUF Dual Inference Routing Engine**: Native text completion routing for GGUF 4-bit / 8-bit quantized models (`_generate_gguf`) eliminating PyTorch tokenizer runtime errors.
- **Sleep Prevention & OS Power Lock Engine**: Native Windows Win32 API (`SetThreadExecutionState`) & HTML5 Screen Wake Lock preventing host OS sleep/hibernate during active downloads.
- **Smart Download Inspection & Interactive Resume Modal**: Automatically detects if a model is 100% installed or partially downloaded, offering an interactive Glassmorphism Modal with visual cached progress.
- **Async Background Model Download Engine (`/api/pull` & `/api/pull/status`)**: Non-blocking background thread download manager with live status polling.
- **AQRuntime Desktop Control Center (`aq ui`)**: Full-featured 5-tab Desktop GUI Control Center (`aq ui`) providing 100% visual access to the entire CLI suite.
- **Conversation Scrollbar Fix**: Smooth, responsive auto-scrolling chat bubble layout.
- **GGUF 4-Bit Quantization Engine**: Native GGUF 4-bit model loader (`src/aqruntime/model/gguf_loader.py`) enabling ultra-low memory footprint execution (~2.2 GB RAM for 3B models, ~5.5 GB RAM for 8B models).
- **GGUF Model Discovery (`aq discover gguf`)**: Tailored discovery catalog for GGUF 4-bit models tagged `[GGUF-Q4]`.
- **Integrated Web UI Dashboard (`aq ui`)**: Single-command Web UI dashboard launch (`aq ui`) that automatically opens your default browser to `http://127.0.0.1:8000/ui`.
- **Modern Dark Glassmorphism Interface**: Single-page application featuring visual model selector, live chat bubble window, custom system prompt editor, live hardware RAM monitor, and memory manager.
- **Local HTTP REST API Server (`aq serve`)**: OpenAI-compatible REST API endpoints (`/v1/chat/completions`, `/v1/models`, `/health`) to connect external Web UIs, extensions, and local scripts.
- **Custom System Prompt Override (`--system`)**: Customize assistant persona and instructions per session.
- **Pre-Installation Hardware Diagnostic (`aq doctor`)**: Verifies system hardware capabilities against minimum software requirements (4.0 GB RAM) and points out the lightest entry model.
- **Pre-Download File Size Warning & Confirmation (`aq pull`)**: Calculates estimated repository download sizes and prompts interactive user confirmation (`Proceed with download? [y/N]`).
- **Dual-Tier Conversation Memory (`aq memory` & `aq run -m`)**: Short-Term Memory sliding window and Long-Term Memory persistent JSON sessions.
- **User Privacy & Control**: Choose persistent memory or run in ephemeral/incognito mode (`--no-memory`).
- **Smart Hardware Discovery (`aq discover`)**: Automatically inspects host RAM and CPU capacity, offering tailored model recommendations.
- **Online & Offline Dual-Mode Catalog**: Dynamically queries Hugging Face Hub live while seamlessly falling back to a permanent offline local catalog cache.
- **Hugging Face Authentication (`aq login`)**: Securely authenticates and downloads Gated Models requiring license authorizations.
- **Collision-Free Storage Isolation**: Multi-model storage keys prevent folder overwrites.
- **RAM Memory Optimization**: Low memory footprint model loading (`low_cpu_mem_usage`, auto-dtype FP16/BF16) tailored for 16 GB RAM devices.
- **Interactive Multi-Turn Chat REPL (`aq run`)**: Native chat template formatting with automatic memory release upon exit.

---

## 1. Quick Start Tutorial (Step-by-Step for New Users)

### Prerequisites

- **Python**: Version 3.10 or newer (64-bit).
- **RAM**: Minimum 4.0 GB total RAM (8 GB – 16 GB recommended for 1.5B–3.8B models).
- **Storage**: At least 10 GB free disk space for model weights.
- **Operating System**: Windows 10/11, Ubuntu 20.04+, or macOS 12+.

### Step 1: Clone or Open Project Directory

Open Command Prompt (`cmd`), PowerShell, or Terminal, and navigate to the project directory:

```bash
# Windows Command Prompt / PowerShell
cd /d D:\AQRuntime
```

### Step 2: Create & Activate Virtual Environment

Create an isolated virtual environment and install AQRuntime:

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell
# or: .\.venv\Scripts\activate.bat   # Command Prompt (cmd)

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

Install AQRuntime in editable mode:

```bash
python -m pip install -e .
```

### Step 3: Launch Integrated Web UI Dashboard

Run `aq ui` to start the local server and automatically open the Web UI Dashboard in your browser:

```bash
aq ui
```

Verify version:

```bash
aq version
```

---

## 2. Comprehensive Command Reference

AQRuntime provides **10 primary CLI commands**.

```
 Usage: aq [OPTIONS] COMMAND [ARGS]...

 Commands:
   ui        Launch local HTTP server and open Web UI Dashboard in browser.
   serve     Launch local OpenAI-compatible HTTP REST API Server.
   doctor    Run pre-installation hardware requirement diagnostic.
   discover  Discover compatible models matching host hardware specifications.
   login     Save Hugging Face User Access Token for gated models.
   pull      Download a model repository and store it locally.
   list      Display locally installed models.
   run       Load a model and launch interactive inference chat session.
   memory    Manage saved conversation memory sessions.
   remove    Remove a locally installed model directory.
   version   Display the AQRuntime version.
```

---

### Command 1: `aq ui`

**Purpose**: Launch local HTTP server and automatically open the integrated Web UI Dashboard in your default web browser.

#### Syntax
```bash
aq ui [--host HOST] [--port PORT] [--no-browser]
```

#### Arguments & Parameters
- `--host`, `-h` *(Optional, String)*: Host IP address (default: `127.0.0.1`).
- `--port`, `-p` *(Optional, Integer)*: Port number (default: `8000`).
- `--no-browser` *(Optional, Flag)*: Do not automatically open the web browser.

#### Dashboard URL
`http://127.0.0.1:8000/ui`

---

### Command 2: `aq serve`

**Purpose**: Launch a local OpenAI-compatible HTTP REST API server allowing external Web UIs, browser extensions, and scripts to interact with installed models.

#### Syntax
```bash
aq serve [--host HOST] [--port PORT]
```

#### Arguments & Parameters
- `--host`, `-h` *(Optional, String)*: Host IP address (default: `127.0.0.1`).
- `--port`, `-p` *(Optional, Integer)*: Port number (default: `8000`).

#### Endpoints Summary
- `GET /health`: Server status and version check.
- `GET /v1/models`: List installed models in OpenAI-compatible JSON format.
- `POST /v1/chat/completions`: Generate assistant responses from user message arrays.

#### Example Output
```text
==================================================================
               AQRuntime HTTP REST API Server                     
==================================================================
Server Host     : http://127.0.0.1:8000
Health Check    : http://127.0.0.1:8000/health
Models List     : http://127.0.0.1:8000/v1/models
Chat Endpoint   : http://127.0.0.1:8000/v1/chat/completions
API Standard    : OpenAI API Compatible
==================================================================
```

---

### Command 2: `aq doctor`

**Purpose**: Verify system hardware capabilities against minimum software requirements (4.0 GB RAM) and show minimal entry model guidance.

#### Syntax
```bash
aq doctor
```

#### Example Output
```text
==================================================================
             AQRuntime Setup Hardware Diagnostic                  
==================================================================
OS          : Windows 11
Total RAM   : 15.52 GB (Available: 4.73 GB)
CPU Cores   : 18
------------------------------------------------------------------
Status      : [PASS] System meets minimum hardware requirements.
Entry Model : Lightest recommended model is 'TinyLlama/TinyLlama-1.1B-Chat-v1.0' (~2.5 GB RAM).
==================================================================
```

---

### Command 1: `aq discover`

**Purpose**: Inspect host hardware capacity (CPU, RAM, OS), query live online or cached model catalogs, and list compatible models.

#### Syntax
```bash
aq discover [QUERY]
```

#### Arguments & Parameters
- `QUERY` *(Optional, String)*: Keyword filter to search models by name or publisher (e.g., `gemma`, `llama`, `qwen`, `phi`).

#### Examples
```bash
# Discover all compatible models matching system hardware
aq discover

# Filter discovery by keyword 'gemma'
aq discover gemma

# Filter discovery by keyword 'llama'
aq discover llama
```

#### Example Output
```text
Hardware Specs: OS=Windows 11 | RAM Total=15.52 GB (Available=4.61 GB) | CPU Cores=18
Recommended Limit: Parameter <= 5.2B (FP16)
Catalog Source   : Online (Live Hugging Face API)

Filter Query     : 'gemma'

Compatible Models:

 [COMPATIBLE]   google/gemma-2-2b-it                     (2.6B params | ~4.5 GB RAM)
                Google's lightweight 2.6B open LLM for efficient local inference.
```

---

### Command 2: `aq login`

**Purpose**: Store a Hugging Face User Access Token locally for downloading Gated Models requiring license authorization.

#### Syntax
```bash
aq login [TOKEN]
```

#### Arguments & Parameters
- `TOKEN` *(Optional, String)*: Your Hugging Face Access Token (`hf_xxxxxxxxxxxxxxxxxxxx`). If omitted, an interactive prompt will ask for token input with masked typing.

#### Examples
```bash
# Login by passing token as an argument
aq login hf_AbCdEfGhIjKlMnOpQrStUvWxYz

# Login via interactive prompt
aq login
```

#### Notes
Tokens are saved securely in [`config/runtime.yaml`](file:///d:/AQRuntime/config/runtime.yaml). Alternatively, you can set the `HF_TOKEN` environment variable.

---

### Command 4: `aq pull`

**Purpose**: Download a model from Hugging Face Hub and store it in local storage with pre-download file size estimation and interactive user confirmation.

#### Syntax
```bash
aq pull MODEL_ID [--token TOKEN] [--yes]
```

#### Arguments & Parameters
- `MODEL_ID` *(Required, String)*: Full Hugging Face repository name (e.g., `google/gemma-2-2b-it` or `Qwen/Qwen2.5-1.5B-Instruct`).
- `--token`, `-t` *(Optional, String)*: Hugging Face User Access Token for gated models.
- `--yes`, `-y` *(Optional, Flag)*: Bypass interactive download size confirmation prompt.

#### Pre-Download Size Warning & Confirmation
Sesaat sebelum mengunduh, AQRuntime menghitung total ukuran berkas repositori via Hugging Face Hub API dan menampilkan kotak peringatan:

```text
==================================================================
                   Model Download Warning                         
==================================================================
Repository ID   : google/gemma-2-2b-it
Estimated Size  : ~4.8 GB
Storage Path    : D:\AQRuntime\models\google-gemma-2-2b-it
Notice          : This operation uses your network connection.
==================================================================

Proceed with download? [y/N]: 
```

- Jika pengguna memilih `y` (Yes), unduhan dimulai.
- Jika pengguna memilih `n` (No), unduhan dibatalkan secara bersih tanpa membuang kuota jaringan.

#### Examples
```bash
# Pull an open-access model (with interactive confirmation)
aq pull Qwen/Qwen2.5-1.5B-Instruct

# Pull bypassing interactive confirmation (for automated scripts)
aq pull Qwen/Qwen2.5-1.5B-Instruct --yes

# Pull a gated model using saved token
aq pull meta-llama/Llama-3.2-1B-Instruct
```

#### Gated Model Guidance Output
If attempting to pull a gated model without license approval or token:
```text
[!] Model 'meta-llama/Llama-3.2-1B-Instruct' is a GATED model requiring license acceptance.

User Action Steps:
 1. Open in browser: https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
 2. Click 'Accept License / Request Access'
 3. Get your Access Token from: https://huggingface.co/settings/tokens
 4. Run: aq login <YOUR_TOKEN>
 5. Re-run: aq pull meta-llama/Llama-3.2-1B-Instruct
```

---

### Command 4: `aq list`

**Purpose**: List all locally installed models stored in the `models/` directory.

#### Syntax
```bash
aq list
```

#### Example Output
```text
Installed Models

- google-gemma-2-2b-it
- qwen-qwen2-5-1-5b-instruct
- tinyllama
```

---

### Command 5: `aq run`

**Purpose**: Load an installed model into memory and start an interactive multi-turn conversation session (REPL) with Short-Term and Long-Term Memory support.

#### Syntax
```bash
aq run MODEL_NAME [--memory | --no-memory] [--session SESSION_NAME]
```

#### Arguments & Parameters
- `MODEL_NAME` *(Required, String)*: Installed model folder name or short alias (e.g., `google-gemma-2-2b-it` or `gemma-2-2b`).
- `--memory` / `--no-memory` *(Optional, Flag)*: Enable persistent Long-Term Memory saving (default: `--memory`) or run in incognito/ephemeral mode (`--no-memory`).
- `--session`, `-s` *(Optional, String)*: Custom session memory name (e.g., `coding-python`).

#### Examples
```bash
# Run with persistent memory (default)
aq run google-gemma-2-2b-it

# Run in incognito/ephemeral mode (do not load or save memory)
aq run google-gemma-2-2b-it --no-memory

# Run with a custom named session
aq run google-gemma-2-2b-it --session coding-python
```

#### Memory Release & Cleanup Behavior
When the user types `exit` (or presses `Ctrl+C` / `Ctrl+D`):
1. **Explicit Model Unloading**: Active model weights, tokenizer, and conversation context are explicitly cleared via `engine.unload()`.
2. **Garbage Collection & Cache Flushing**: Python garbage collector (`gc.collect()`) is triggered, and PyTorch CUDA/VRAM caches are flushed (`torch.cuda.empty_cache()`).
3. **Process Memory Reclamation**: Operating system kernel immediately reclaims 100% of physical RAM and VRAM.

---

### Command 6: `aq memory`

**Purpose**: Manage saved conversation memory sessions (list, clear, export).

#### Syntax
```bash
aq memory list
aq memory clear SESSION_NAME
aq memory export SESSION_NAME [--output OUTPUT_FILE]
```

#### Examples
```bash
# List all saved memory sessions
aq memory list

# Clear a specific memory session
aq memory clear google-gemma-2-2b-it

# Export a memory session to a markdown document
aq memory export coding-python --output my_notes.md
```

---

### Command 7: `aq remove`

**Purpose**: Remove a locally installed model directory to free up disk space.

#### Syntax
```bash
aq remove MODEL_NAME
```

#### Arguments & Parameters
- `MODEL_NAME` *(Required, String)*: Installed model folder name or alias (e.g., `google-gemma-2-2b-it`).

#### Example Output
```bash
$ aq remove google-gemma-2-2b-it
Model removed.
```

---

### Command 8: `aq version`

**Purpose**: Display the current AQRuntime software version.

#### Syntax
```bash
aq version
```

#### Example Output
```text
AQRuntime
Version 0.5.0
```

---

## 3. Recommended Models for 16 GB RAM Hardware

| Publisher | Model Repository | Param Size | Est. RAM | Highlights |
|---|---|---|---|---|
| **Google** | `google/gemma-2-2b-it` | 2.6B | ~4.5 GB | Excellent reasoning & general knowledge |
| **Alibaba** | `Qwen/Qwen2.5-1.5B-Instruct` | 1.5B | ~3.2 GB | Outstanding coding & multilingual support |
| **Meta** | `meta-llama/Llama-3.2-1B-Instruct` *(Gated)* | 1.0B | ~2.4 GB | Ultra-lightweight & fast response |
| **Microsoft** | `microsoft/Phi-3.5-mini-instruct` | 3.8B | ~7.8 GB | High performance small language model |
| **Community** | `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | 1.1B | ~2.5 GB | Minimal resource consumption |

---

## 4. Maintenance & Governance Policy

> [!IMPORTANT]
> **Documentation Maintenance Rule**:
> This document (`docs/User_Guide.md` and [`docs/User_Manual.md`](file:///d:/AQRuntime/docs/User_Manual.md)) SHALL be updated in every software evolution cycle whenever new commands, command arguments, flags, or configuration parameters are introduced or modified.
