# AQRuntime Pitch Deck (English)
### Almudaya Quantum Labs

Version: `v2.4.0`  
Target: Investors, hackathon judges, technical partners  
Tone: Honest engineering narrative, demo-first

---

## Slide 1 - Title
**AQRuntime: Local AI Execution Engine for Privacy-First Teams**

- Subtitle: Run local AI models on your own machine with browser voice, file attachment, and an OpenAI-compatible API.
- Organization: Almudaya Quantum Labs
- Key badges:
  - PoC v2.4.0
  - Open Source
  - Intel NPU / Intel Arc / DirectML / CUDA / CPU
  - OpenCode-compatible backend

Speaker note:
> "AQRuntime is an Almudaya Quantum Labs engine that lets teams use AI locally, while remaining transparent about which features are production-ready and which are experimental."

---

## Slide 2 - Problem
**Cloud AI is powerful, but local teams still face real trade-offs**

- Privacy concerns when sensitive documents are sent to public APIs.
- Cost and connectivity dependency for cloud inference.
- New laptops often have unused NPU/iGPU acceleration.
- Many local runtimes are CLI-only or have narrow multimodal workflows.
- True local models still need good hardware-aware routing.

Speaker note:
> "The goal is simple: usable AI on the edge without overselling simulated features as fully trained multimodal capabilities."

---

## Slide 3 - Solution
**AQRuntime provides a practical local AI control center**

- 100% local-first when using already downloaded models
- Intelligent hardware fallback chain
- Web Control Center + CLI + REST API
- GGUF / PyTorch local model loading
- Document attachment with safe truncation
- OpenAI-compatible endpoint for external apps (including OpenCode)

Honest capability status:
- Text chat: ready
- Streaming: ready
- Generic tool calling: ready
- Document attachment: ready
- Audio multipart API: OpenAI-style endpoint available, backend currently simulated
- Vision: payload extraction only, simulated analysis
- Voice STT: browser SpeechRecognition; backend audio endpoint simulated
- TTS: browser Web Speech Synthesis

---

## Slide 4 - Scientific Vision
**Almudaya Quantum Runtime: where AI runtime meets long-term vision**

- Name combines:
  - Almudaya
  - Quantum Runtime vision
- Long-term direction:
  - AI
  - decentralization / post-quantum cryptography aspirations
  - quantum computing convergence
- Engineering methodology:
  - structured documentation baselines (Waterfall)
  - iterative hardware/multimodal evolution (Spiral model)
  - automated acceptance testing

Speaker note:
> "The word Quantum represents a roadmap, not a claim that quantum hardware is used today."

---

## Slide 5 - Hardware Acceleration
**Heterogeneous Hardware Priority Fallback Chain**

```text
Input User
  |
  v
Intel OpenVINO (NPU / Arc) -> DirectML -> CUDA -> ONNX -> CPU fallback
```

- Priority values:
  - Intel OpenVINO: `10`
  - DirectML: `15`
  - CUDA: `20`
  - ONNX: `25`
  - CPU: `30`
- Cloud providers (OpenAI, Hugging Face) remain optional and may transmit data.
- Accurate note: server and driver availability determines the actual provider.

---

## Slide 6 - Voice & Multimodal Experience
**Multimodal UI without overselling backend AI vision**

- Voice input:
  - Browser microphone UI button
  - Browser `SpeechRecognition`
  - local audio endpoint `/api/audio/transcribe`
  - OpenAI-style `/v1/audio/transcriptions`
  - backend currently returns simulated STT
- Voice output:
  - `Read Aloud` uses browser `SpeechSynthesis`
  - no external TTS cost
- Vision:
  - image payload is extracted in OpenAI-style format
  - image analysis is currently simulated
  - image requests are rejected for non-vision model classification
- Honest version for judges:
  - "Voice input UI + simulated backend STT"
  - "Experimental vision payload support"

---

## Slide 7 - Productivity Features
**Built for real office and developer workflows**

- Document / code attachment reader (`.py`, `.txt`, `.json`, `.md`, `.csv`)
- Binary Guard prevents accidental binary loading
- Safe 4,500 character truncation
- Dynamic max tokens from `64` to `8192`
- Adjustable temperature / top-p where API-compatible
- Real-time telemetry:
  - throughput is estimated
  - latency shown per generation
  - no exact tokenizer-token telemetry for GGUF fallback

Speaker note:
> "Performance telemetry is an engineering aid, not an exact tokenizer benchmark."

---

## Slide 8 - Control Center GUI
**Five-tab Web Control Center**

1. Chat & Infer
   - model selector
   - token slider
   - file attachment
   - persona presets
   - markdown export
2. Installed Models
   - local model list
   - quantization tags
   - size information
3. Model Hub
   - catalog discovery
   - filters (GGUF, NVIDIA, Vision, Audio)
   - 1-click download workflow
4. Memory Manager
   - session listing and export
5. Settings & Diagnostics
   - hardware audit
   - Hugging Face token management

---

## Slide 9 - Developer CLI Suite
**Readable, practical, local-first CLI**

```bash
# Full help
aq help
# hardware audit
aq doctor
# discover models by category
aq discover gguf
aq discover audio
# download model
aq pull bartowski/gemma-2-2b-it-GGUF
# interactive chat
aq run bartowski/gemma-2-2b-it-GGUF --max-tokens 2048
# Web GUI / REST API
aq ui
aq serve
```

Key value:
- Native CLI onboarding
- Transparent telemetry
- OpenAI-compatible local server

---

## Slide 10 - Competitive Comparison

| Capability | AQRuntime | Ollama | LM Studio |
|---|---|---|---|
| Intel NPU via OpenVINO | Native priority path | Limited / experimental | Limited |
| Hardware fallback chain | Automatic provider priority | Mostly static GPU/CPU | Manual slider |
| Voice browser input/output | Browser voice input + TTS | No native voice | No native voice |
| Multimodal payload | Base64 extraction; analysis simulated | Basic image API | GUI preview |
| Document attachment + binary guard | Integrated binary guard + 4,500 truncation | Manual copy | Basic drag-drop |
| Max tokens slider | GUI + CLI | CLI flag | Settings sidebar |
| Runtime telemetry | Estimated tok/s + latency | Terminal summary | Minimal header stats |
| License | MIT Open Source | MIT Open Source | Proprietary |

---

## Slide 11 - Live Demo Script (3 Minutes)
**Recommended honest demo flow**

1. Minute 1 - Local server
   - Run `aq serve`
   - Show health endpoint and model list
   - Show OpenCode model selector with `aqruntime/*`
2. Minute 2 - Chat + streaming
   - Ask a short question
   - Show SSE streaming
   - Show telemetry badge
3. Minute 3 - Productivity + audio
   - Attach a text file
   - Show binary guard / token limit
   - Call OpenAI-style audio transcription endpoint
   - Clearly state STT is simulated backend

Demo note:
> "Do not claim the backend performs real Whisper transcription or real image understanding unless that model integration is enabled."

---

## Slide 12 - OpenCode Integration
**AQRuntime works as a custom OpenCode provider**

- Config file:
  - Windows: `%USERPROFILE%\.config\opencode\opencode.jsonc`
- Provider:
  - package: `@opencode/ai/providers/openai-compatible`
  - base URL: `http://127.0.0.1:8000/v1`
- Model examples:
  - `aqruntime/bartowski-gemma-2-2b-it-gguf`
  - `aqruntime/meta-llama-llama-3-2-1b-instruct`
  - `aqruntime/tinyllama`
- Fallback remains:
  - `opencode/cat-jam-free`
  - other built-in `opencode/*`
- Tested integration:
  - `opencode reload`
  - `opencode models`
  - MCP list (no servers configured)
  - agent loop with built-in free model
  - AQRuntime direct non-stream and stream SSE

---

## Slide 13 - Roadmap
**From capable local runtime to competitive edge platform**

Current v2.4:
- LLM text chat
- streaming
- generic tool calling
- warm model cache
- configurable context
- OpenAI-compatible server
- simulated audio / experimental vision endpoint

Next milestones:
1. Real STT using Whisper-style local backend
2. Real image analysis using a small multimodal model
3. Exact tokenizer-based telemetry for GGUF
4. Native scheduler and richer capability advertisement
5. Hybrid enterprise sync / cloud Run (future)
6. Policy, auth, and production observability

Long-term vision:
- post-quantum cryptography
- decentralization
- quantum circuit convergence

---

## Slide 14 - Conclusion
**AQRuntime is honest local AI engineering**

- Strong edge-local text runtime
- OpenCode-compatible
- useful productivity features
- clear capability boundaries
- roadmap for real multimodal expansion

Key message:
> " AQRuntime delivers practical local AI today, while separating production-ready text features from experimental audio and vision capabilities."

---

## Capability Audit Summary

| Capability | Status | Slide Use |
|---|---|---|
| Text LLM chat | Ready | Say directly |
| Streaming SSE | Ready | Say directly |
| OpenAI-compatible API | Ready | Say directly |
| Generic tool calling | Ready | Say with "generic adapter" |
| Document attachment | Ready | Say directly |
| Telemetry throughput | Estimated | Say "estimated tok/s" |
| Voice STT | Experimental / browser-assisted | Softened language |
| TTS Read Aloud | Browser speech | Say as browser feature |
| Vision analysis | Simulated | Do not claim real vision |
| Offline | Local dependency + installed models | Say "local-first" |
| Cloud providers | Optional | Do not claim zero cloud risk in every mode |