# AQRuntime Demo Runbook - AI Builder Cup

## 1. Preflight

```powershell
cd "D:\AQRuntime2"
.\.venv\Scripts\python.exe aq.py doctor
.\.venv\Scripts\python.exe aq.py list
.\.venv\Scripts\python.exe aq.py runtime list
```

Expected:
- Hardware diagnostic returns `Status: [PASS]`.
- `tinyllama` and `bartowski-gemma-2-2b-it-gguf` are installed.
- CPU provider is available.

## 2. CLI Demo

### TinyLlama

```powershell
"Hello AQRuntime`nexit" | .\.venv\Scripts\python.exe aq.py run tinyllama --max-tokens 64 --no-memory
```

### Gemma 2B (GGUF)

```powershell
"Give me one short productivity tip`nexit" | .\.venv\Scripts\python.exe aq.py run bartowski-gemma-2-2b-it-gguf --provider cpu --max-tokens 64 --no-memory
```

Show:
- Local-only model loading.
- Provider selection with fallback.
- GGUF quantized inference.

## 3. API + Web UI Demo

Start the server:

```powershell
.\.venv\Scripts\python.exe aq.py serve --host 127.0.0.1 --port 8000
```

Open:
- `http://127.0.0.1:8000/ui`

Test health:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```

Test chat:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1/chat/completions" `
  -Method POST -ContentType "application/json" `
  -Body '{"model":"tinyllama","messages":[{"role":"user","content":"Hello from AQRuntime API"}],"max_tokens":64}'
```

Test multimodal simulation:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1/chat/completions" `
  -Method POST -ContentType "application/json" `
  -Body '{"model":"bartowski-gemma-2-2b-it-gguf","messages":[{"role":"user","content":[{"type":"text","text":"Describe this image"},{"type":"image_url","image_url":{"url":"data:image/png;base64,AA=="}}]}],"max_tokens":64}'
```

Memory demo:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/memory/copy" -Method POST -ContentType "application/json" `
  -Body '{"source":"tinyllama","target":"demo_session"}'
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/memory/session?name=demo_session"
```

## 4. Key Hackathon Talking Points

- Runs locally, offline-first.
- Supports GGUF quantized models for low-RAM laptops.
- OpenAI-compatible `/v1/chat/completions` endpoint.
- Built-in hardware discovery and compatibility matrix.
- Safeguards against gated-model failures with actionable error messages.
- Memory sessions and export for conversation persistence.
- Security hardening: sanitized storage/memory paths and array-bound provider fallback.

## 5. Troubleshooting

- `sentencepiece` or `tiktoken` missing:
  ```powershell
  .\.venv\Scripts\python.exe -m pip install sentencepiece tiktoken
  ```

- Model response is too slow:
  - Use `tinyllama` or a smaller GGUF quantization.
  - Use `--max-tokens 64`.

- Gemma GGUF warning `n_ctx_per_seq < n_ctx_train`:
  - Safe warning; context is capped to 2048.
  - Use a faster quantization such as `IQ4_XS` or `Q4_K_M`.
