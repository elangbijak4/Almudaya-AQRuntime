# AQRuntime2 User Guide

This guide describes AQRuntime2 version **2.4.0** as implemented in this checkout. Windows examples use PowerShell and Python 3.12. Performance and supported models depend on the contents of `models/` and the computer's hardware.

## 1. Set up Python 3.12

Open PowerShell in the project root:

```powershell
cd D:\AQRuntime2
```

Check the existing virtual environment:

```powershell
.\.venv\Scripts\python.exe --version
```

If it does not exist, create it with Python 3.12:

```powershell
py -3.12 -m venv .venv
```

If `.venv` points to another Python version or cannot run, create a new environment and keep the old one in place:

```powershell
py -3.12 -m venv .venv312
.\.venv312\Scripts\python.exe -m pip install -e .
```

For a working `.venv`, install the project in editable mode and verify the version:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe --version
```

The expected version for this setup is `Python 3.12.x`. Calling the executable through `.venv\Scripts\python.exe` makes AQRuntime use that environment even if other Python versions are installed.

Optionally activate the virtual environment so you can call `aq` directly:

```powershell
.\.venv\Scripts\Activate.ps1
```

If you do not activate it, run commands through `python -m aq` after the editable install, or use the executable path under `.venv\Scripts`.

## 2. Start the application

Start the Control Center:

```powershell
.\.venv\Scripts\python.exe -m aq ui
```

Open [http://127.0.0.1:8000/ui](http://127.0.0.1:8000/ui). Keep the terminal open while using the application. Press `Ctrl+C` in that terminal to stop the server.

If port 8000 is already in use:

```powershell
.\.venv\Scripts\python.exe -m aq ui --port 8765
```

Then open `http://127.0.0.1:8765/ui`. To run the API without opening a browser:

```powershell
.\.venv\Scripts\python.exe -m aq serve --host 127.0.0.1 --port 8000
```

Use `127.0.0.1` for local access. Binding to `0.0.0.0` makes the server reachable from the network.

## 3. Use the Control Center

### Chat & Infer

1. Select an installed text model under **Active Model**.
2. Enter a prompt and press **Send** or Enter.
3. Adjust **Max Output Tokens** to limit response length. Higher values can increase generation time and memory use.
4. **New Chat** clears the selected model's session after confirmation.
5. **Export (.md)** downloads the visible conversation as a Markdown file.
6. The microphone button uses the browser's Web Speech API when available.
7. **Read Aloud** uses the browser's text-to-speech feature.

> **Known UI limitation:** the hardware runtime and persona/system-prompt controls are displayed, but the current UI chat request does not pass the runtime selection as the backend's `provider` parameter or send the system prompt. Do not rely on these controls to select the inference backend or change model instructions.

### Model Hub

- Search the catalog or use the GGUF, NVIDIA, Vision, and Audio filters.
- The catalog is fetched online when possible; while offline, AQRuntime can use its cached catalog.
- Check download size and hardware suitability before downloading. Downloads require an internet connection and enough disk space.
- For gated models, accept the model license on Hugging Face and save a token with `aq login` or the Settings page. Do not share your token.

### Installed

Shows models stored locally in `models/`. Removing a model deletes its weights directory from disk.

### Hardware Doctor

Displays hardware information AQRuntime can read. Compatibility estimates do not guarantee a model will run quickly or fit in available memory.

### Settings

Manage Hugging Face tokens and recorded conversation sessions. A token is only needed for models that require authentication or license approval.

## 4. CLI commands

Run these commands from the project root with the virtual environment activated, or prefix them with `python -m aq`.

| Command | Purpose |
| --- | --- |
| `aq help` | Show CLI help. |
| `aq version` | Show the AQRuntime version. |
| `aq doctor` | Check basic hardware capacity. |
| `aq runtime list` | Show available runtime providers. |
| `aq runtime info cpu` | Show CPU provider details. Replace `cpu` with the provider to inspect. |
| `aq list` | List locally installed models. |
| `aq discover gemma` | Search the catalog by keyword. Without a keyword, show catalog recommendations. |
| `aq pull bartowski/gemma-2-2b-it-GGUF` | Download that Hugging Face repository. AQRuntime asks you to confirm the estimated size. |
| `aq run bartowski-gemma-2-2b-it-gguf` | Start an interactive chat with an installed model. Type `exit` to quit. |
| `aq memory list` | List saved memory sessions. |
| `aq memory clear SESSION_NAME` | Clear a session's memory. Check the session name first. |
| `aq memory export SESSION_NAME` | Export a session to Markdown. |
| `aq remove MODEL_NAME` | Delete model weights from disk. |

Use a Hugging Face repository ID with `aq pull`. For `aq run` and the API, use the local model name shown by `aq list`.

Example CLI session without saved memory:

```powershell
aq run bartowski-gemma-2-2b-it-gguf --no-memory --max-tokens 256
```

## 5. OpenAI-compatible local API

Start the server:

```powershell
aq serve --host 127.0.0.1 --port 8000
```

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Server status and version. |
| `GET` | `/v1/models` | Locally installed chat models. |
| `GET` | `/api/models/capabilities` | Models and their reported capabilities. |
| `GET` | `/api/runtimes` | Runtime provider status. |
| `GET` | `/api/doctor` | Hardware diagnostic information. |
| `POST` | `/v1/chat/completions` | Text chat or SSE streaming. |
| `POST` | `/v1/audio/transcriptions` | OpenAI-style audio upload; transcription is currently simulated. |

PowerShell request example:

```powershell
$body = @{
  model = 'bartowski-gemma-2-2b-it-gguf'
  messages = @(@{ role = 'user'; content = 'Briefly explain tensors.' })
  max_tokens = 128
} | ConvertTo-Json -Depth 8

Invoke-RestMethod `
  -Uri 'http://127.0.0.1:8000/v1/chat/completions' `
  -Method Post `
  -ContentType 'application/json' `
  -Body $body
```

JSON request body example:

```json
{
  "model": "bartowski-gemma-2-2b-it-gguf",
  "messages": [{"role": "user", "content": "Hello, answer briefly."}],
  "max_tokens": 128,
  "stream": false
}
```

For a multi-turn conversation, include the complete `messages` history (system, user, and assistant) in every request. Set `"stream": true` to receive Server-Sent Events.

## 6. Data locations

- `models/`: local model weights.
- `config/runtime.yaml`: version, model/log locations, context length, and model-cache limit. Do not copy secret tokens into documents or public repositories.
- `logs/`: application logs.
- `memory/`: persistent conversation sessions.
- `AQRUNTIME_HOME`: optional environment variable for pointing the application to another compatible project data root.

## 7. Known feature limitations

- **Local text chat:** tested with a local Gemma GGUF model through the API. Models can still produce incorrect factual answers; verify important information.
- **Model format and speed:** GGUF models can use `llama.cpp`; non-GGUF models use Transformers/PyTorch. Load time, weight size, backend, context length, CPU/GPU, and RAM all affect performance. A smaller model is not always faster if its backend or load time differs.
- **GPU:** unavailable providers may be skipped and runtime can fall back to CPU. `WinError 4551` indicates Windows Application Control blocked a file; changing Python versions alone may not resolve it.
- **Images/Vision:** image attachments are accepted, but current image analysis is simulated rather than real vision inference.
- **Audio transcription:** the endpoint returns simulated transcription, not real Whisper output. The UI microphone uses browser capabilities.
- **Read Aloud:** audio is generated by the browser, not an AQRuntime TTS model.
- **File attachments:** use plain-text files such as `.txt`, `.md`, `.py`, `.json`, `.csv`, `.log`, `.c`, `.cpp`, and `.h`. Convert binary documents to text or Markdown first.
- **Privacy:** local GGUF inference runs on the computer. Model Hub search and downloads use the network. Microphone processing depends on the browser.

## 8. Troubleshooting

### Confirm the virtual environment uses Python 3.12

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip --version
```

If you use the project `.venv`, the pip path should be under `D:\AQRuntime2\.venv\Lib\site-packages`.

### Port 8000 is already in use

Run `aq ui --port 8765`, then open `http://127.0.0.1:8765/ui`.

### A model fails to load or is slow

Check the model ID with `aq list`, available disk space and RAM, and provider status with `aq runtime list`. Try a smaller GGUF model or lower `n_ctx` in `config/runtime.yaml`. The first response can include model loading time.

### PyTorch/CUDA errors

Check `aq runtime list`. CUDA may be unavailable because a GPU/driver was not detected or PyTorch DLLs failed to load. If the error mentions Application Control/WinError 4551, check the Windows CodeIntegrity log; uninstalling Python 3.15 is not the first diagnostic step.

### A gated model fails to download

Make sure you accepted the license on Hugging Face, then run `aq login` and enter your token interactively. Avoid placing the token directly in shell history.

## 9. Initial checks

```powershell
aq version
aq doctor
aq runtime list
aq list
```

After starting the server, check `http://127.0.0.1:8000/health` and `http://127.0.0.1:8000/v1/models`.
