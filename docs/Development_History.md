# AQRuntime Development History

This document records the full chronological history of development iteration cycles, baseline milestones, and features added to AQRuntime from inception to the latest release.

---

## 📜 Version History Log

### 🚀 PoC v2.4 (Release 2.4.0) - GitHub Final Release Edition
- **Explicit `aq help` CLI Command**: Added dedicated CLI command `@app.command(name="help")` printing formatted manual table of all subcommands (`aq run`, `aq pull`, `aq list`, `aq doctor`, `aq discover`, `aq login`, `aq runtime`, `aq memory`, `aq remove`, `aq version`) and flag descriptions.
- **Dynamic Max Output Tokens Control (`max_tokens`)**: Configurable generation length from `64` up to `8192` tokens via `--max-tokens` CLI option, REST API `/v1/chat/completions`, and Web GUI slider in Tab 1 & Tab 5 for long-form document generation.
- **Quantization Precision Level Badges (`Q4_K_M`, `Q5_K_M`, `Q8_0`, `FP16`)**: Tagged and displayed GGUF quantization levels explicitly in `aq list` CLI and Web UI Model Hub / Installed cards.
- **100% Offline Mode Verification**: Guaranteed full offline execution without internet dependencies.

---

### 🎙️ PoC v2.3 (Release 2.3.0) - Voice Audio & Speech Engine
- **Audio Processor (`src/aqruntime/model/audio.py`)**: Audio validation & speech-to-text processing for speech audio payloads.
- **REST API Transcribe Endpoint (`POST /api/audio/transcribe`)**: Ingests audio files (`.mp3`, `.wav`, `.m4a`, `.ogg`) or microphone audio buffers and returns transcribed speech text.
- **Web UI Voice Input (`🎙️`)**: Live Microphone Recorder Button with active recording status (`🔴 Recording...`).
- **Text-to-Speech Output (`🔊 Read Aloud`)**: Speaker button on assistant chat bubbles leveraging HTML5 Web Speech Synthesis API (`window.speechSynthesis`) to speak AI answers in natural human voice.
- **Audio Model Discovery Catalog (`aq discover audio`)**: Dedicated CLI filter and Web UI Model Hub filter button (**`🎙️ Audio Models`**) for speech models (`openai/whisper-tiny`, `openai/whisper-base`, `Qwen2-Audio`).

---

### 👁️ PoC v2.2 (Release 2.2.0) - Multimodal Vision & Image Analysis Engine
- **Vision Processor (`src/aqruntime/model/vision.py`)**: Multimodal Vision Engine supporting Base64 data URLs (`data:image/png;base64,...`) and visual prompt extraction.
- **Multimodal Web UI Image Input (`🖼️`)**: Live Image Preview Thumbnail Canvas with 1-click remove button and image thumbnail rendering in chat history.
- **Vision Discovery Catalog (`aq discover vision`)**: Dedicated CLI filter and Web UI Model Hub filter button (**`👁️ Vision Models`**) for curated visual LLMs (`moondream2`, `PaliGemma`, `Qwen2-VL`).
- **OpenAI-Compatible Multimodal REST API**: Ingests multimodal `content` arrays in `/v1/chat/completions`.

---

### 🌟 PoC v2.1 (Release 2.1.0) - GitHub Release Edition
- **Speed & Performance Monitor Telemetry**: Measures generation start/end duration (`perf_counter()`), calculating `tokens_per_second` and first-token `latency_seconds`. Rendered as live performance badge (`⚡ 18.5 tok/s • 0.42s latency`) under model chat bubbles.
- **Document & Code Reader File Attachment (`📎`)**: Allows attaching local text/code files (`.py`, `.txt`, `.json`, `.md`, `.log`, `.csv`) directly into chat prompts via HTML5 `FileReader`.
- **Persona Preset Library**: Quick-select System Prompt gallery in Tab 1 sidebar (Default Assistant, Python Expert, Indonesian Translator, Technical Editor, Science Scholar).
- **1-Click Chat Exporter (`📥 Export Chat (.md)`)**: Button in Tab 1 header to export active conversation history to a formatted Markdown file for sharing or saving.

---

### ⚡ PoC v2.0 (Release 2.0.0) - Heterogeneous Hardware Engine & Pluggable Provider Architecture
- **Pluggable Execution Provider Engine (`src/aqruntime/runtime/providers/`)**: Modular provider system supporting `cpu`, `intel_openvino` (Intel NPU & Intel Arc iGPU), `directml`, `cuda`, `onnx`, `cloud_openai`, and `cloud_huggingface`.
- **Automatic Priority Fallback Chain**: Intelligent runtime selection engine (`Intel NPU` -> `Intel Arc` -> `OpenVINO` -> `DirectML` -> `CUDA` -> `CPU` -> `Cloud`).
- **New CLI Diagnostics Commands**:
  - `aq runtime list`: Lists all available/installed runtimes with status badges (`✓` and `✗`).
  - `aq runtime info <provider>`: Displays detailed status, driver version, and supported task capabilities (LLM, Embedding, Vision).
- **Web Control Center GUI Integration**: Execution Runtime Selector dropdown added to Tab 1 (Chat & Infer) and Tab 5 (Settings).
- **REST API Endpoint**: Added `GET /api/runtimes` for active provider discovery.

---

### 🚀 PoC v1.6 (Release 1.6.0) - GATED Diagnostics, Download Toasts & NVIDIA Catalog
- **GATED Model & Friendly Error Diagnostics**: Detects `GatedRepoError` or missing model errors and outputs clear, step-by-step Indonesian guidance in chat (`aq login <token>`).
- **Download Terminal & GUI Hint**: Explicit prompt informing user that download progress is active both in the Web GUI progress bar and in the Command Line / Terminal window.
- **Completion Toast & Auto-Switch to Chat**: Displays a toast notification upon 100% download completion, automatically selects the new model as active, and switches directly to Tab 1 (Chat & Infer).
- **NVIDIA Open Models Discovery Catalog**: Added `aq discover nvidia` CLI support and dedicated **"💚 NVIDIA Open Models"** filter in the Web Control Center Model Hub tab (`nvidia/Nemotron`, `nvidia/Minitron`, `nvidia/NV-Embed`).
- **Development History Document (`docs/Development_History.md`)**: Living history tracking file updated in every evolution cycle.

---

### 🔀 PoC v1.5 (Release 1.5.0) - Cross-Model Memory Continuity & Session Control
- **"➕ New Chat" Button**: Added 1-click fresh conversation session reset button next to model selection dropdown.
- **Model Switch Modal**: Interactive dialog prompting user upon model change to choose between **"🔀 Transfer Topik Saat Ini ke Model Baru"** (`POST /api/memory/copy`) vs **"✨ Mulai Percakapan Baru"**.
- **Auto-Sync Chat History**: Automatically fetches and renders saved session messages when switching active models (`GET /api/memory/session`).

---

### ⚙️ PoC v1.4 (Release 1.4.0) - GGUF Dual Inference Routing Engine Fix
- **`ctransformers` & `llama-cpp-python` Dual Engine Integration**: Integrated prebuilt Windows wheels for native GGUF 4-bit model execution.
- **GGUF Dual Inference Routing (`_generate_gguf`)**: Routed text completion calls for GGUF models directly, eliminating PyTorch tokenizer runtime errors.

---

### 🛡️ PoC v1.3 (Release 1.3.0) - Sleep Prevention & OS Power Lock Engine
- **Windows Win32 OS Power Lock (`PowerLockManager`)**: Prevents host OS sleep/hibernate during active background model downloads using `SetThreadExecutionState`.
- **HTML5 Screen Wake Lock API**: Prevents screen/browser sleep during downloads.
- **Live Status Badge**: Visual indicator (`🛡️ Sleep Lock Active`) displayed during active downloads.

---

### 🔍 PoC v1.2 (Release 1.2.0) - Smart Download Inspection, Resume Modal & Reset Engine
- **Smart Download Inspection (`POST /api/pull/inspect`)**: Checks disk cache for installed byte size vs total repository size.
- **100% Installed Alert**: Prevents redundant downloads when model is already fully installed.
- **Interactive Resume Modal**: Displays visual progress bar of cached bytes for partial downloads with two user options: **"▶️ Lanjutkan Pengunduhan (Resume)"** vs **"🔄 Reset & Unduh dari Awal"** (`POST /api/pull/reset`).

---

### ⚡ PoC v1.1 (Release 1.1.0) - Async Background Model Download Engine
- **Daemon Thread Download Worker (`start_background_pull`)**: Non-blocking background thread download manager preventing Windows HTTP socket timeouts (`WinError 10053`).
- **Polling Endpoint (`GET /api/pull/status`)**: Returns HTTP 202 and live progress polling status.

---

### 🖥️ PoC v1.0 (Release 1.0.0) - Desktop Control Center Web GUI
- **5-Tab Desktop Control Center GUI (`aq ui`)**: Visual tabs for Chat & Infer, Model Hub, Installed Models, Hardware Doctor, and Settings.
- **Auto-Scrolling Chat Window**: Fixed conversation window scrolling behavior.

---

### 🧠 PoC v0.9 - GGUF 4-Bit Quantization Engine
- **GGUF Model Loader (`GGUFModelLoader`)**: Detects and loads `.gguf` weight files for low-RAM execution.
- **GGUF Hardware Threshold Calculation**: Extended `max_safe_param_size_gguf()` for low-RAM systems.

---

### 🌐 PoC v0.8 - Integrated Web UI Dashboard
- Single-command Web UI launch (`aq ui`) serving embedded single-page dashboard at `http://127.0.0.1:8000/ui`.

---

### 🔌 PoC v0.7 - Local HTTP REST API Server
- OpenAI-compatible REST API endpoints (`/v1/chat/completions`, `/v1/models`, `/health`).
- Custom System Prompt override support (`--system`).

---

### 🩺 PoC v0.6 - Pre-Installation Hardware Diagnostic
- Pre-install hardware diagnostic command (`aq doctor`).
- Pre-download file size estimation and interactive prompt (`aq pull --yes`).

---

### 💾 PoC v0.5 - Short-Term & Long-Term Memory System
- Sliding window short-term context management and JSON file long-term memory persistence (`aq memory`).

---

### 🔑 PoC v0.4 - Gated Model Detection & Token Authentication
- Hugging Face token login and authentication persistence (`aq login <token>`).

---

### 🔍 PoC v0.3 - Hardware-Aware Model Discovery
- Hardware detection (`HardwareDetector`) and discovery catalog search (`aq discover`).

---

### 📦 PoC v0.2 - Multi-Model Storage Isolation
- Collision-free storage structure (`StorageManager`) and model removal (`aq remove`).

---

### 🌱 PoC v0.1 - Proof of Concept
- Core CLI runtime engine (`aq pull`, `aq list`, `aq run`, `aq version`).
