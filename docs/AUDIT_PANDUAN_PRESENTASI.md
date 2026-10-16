# Audit Klaim Panduan Presentasi AQRuntime

File yang diaudit:
`docs/Panduan_Presentasi_AQRuntime.md`

Status:
- ✅ **Terverifikasi**
- ⚠️ **Sebagian / Berlebihan**
- ❌ **Tidak sesuai implementasi saat ini**

## Ringkasan

Sebagian besar klaim pada panduan presentasi **valid di level arsitektur/backend**,
terutama akselerasi hardware, CLI, dan OpenAI-compatible REST API.
Namun ada beberapa klaim multimodal dan telemetry yang **terlalu kuat** dibanding
implementasi actual.

## Audit Slide-by-Slide (Klaim Utama)

| Slide | Klaim | Status | Bukti / Catatan |
|---|---|---|---|
| 1 | AQRuntime v2.4.0, Open Source | ✅ | `pyproject.toml` version `2.4.0`; repo open source |
| 1 | Intel NPU / Arc / CUDA Ready | ✅ | `ProviderManager` dan providers OpenVINO/DirectML/CUDA/CPU |
| 2 | Privasi data ke cloud cloud API | ✅ | Mode lokal tersedia; *catatan*: provider cloud OpenAI/Hugging Face juga tersedia |
| 2 | NPU sudah didukung native | ⚠️ | Provider Intel OpenVINO priority `10`; dukungan aktual tergantung hardware/driver/model |
| 2 | Kebanyakan runtime lokal hanya CLI | ⚠️ | AQRuntime punya GUI Web, tetapi klaim kompetitor perlu data eksternal |
| 3 | 100% offline & zero data leak | ⚠️ | Benar jika hanya model lokal; cloud providers opsional dapat mengirim data ke cloud |
| 3 | Akselerasi majemuk cerdas auto fallback | ✅ | `resolve_provider()` melakukan fallback chain |
| 3 | Multimodal lengkap (suara/gambar) | ⚠️ | STT/TTS dan audio API ada, tetapi STT backend masih simulasi dan vision tidak real |
| 3 | GUI Web modern dua antarmuka | ✅ | `aq ui`, `aq serve`, `src/aqruntime/server/ui/index.html` |
| 5 | Chain NPU → Arc → DirectML → CUDA → CPU | ⚠️ | Implementasi prioritas: OpenVINO (10), DirectML (15), CUDA (20), ONNX (25), CPU (30). Arc ada di OpenVINO provider |
| 6 | STT via `POST /api/audio/transcribe` | ✅ | Endpoint ada dan sekarang juga `/v1/audio/transcriptions` multipart |
| 6 | STT lokal via Whisper | ❌ | `AudioProcessor.transcribe_audio_payload` mengembalikan teks simulasi, bukan transkripsi nyata |
| 6 | TTS HTML5 Web Speech zero latency | ✅ | `src/aqruntime/server/ui/index.html` memakai `speechSynthesis` |
| 6 | Vision Canvas + OpenAI Base64 | ⚠️ | Payload multimodal diekstrak, tetapi analisis vision hanya `describe_image_simulated`; patch 5 menolak non-vision model |
| 7 | Document Reader + Binary Guard + 4500 char | ✅ | UI memakai `MAX_ATTACHMENT_CHARS = 4500` |
| 7 | Dynamic max tokens 64–8192 | ✅ | Inference engine clamp `1..8192` |
| 7 | Real-time telemetry tok/s | ⚠️ | Inference memperkirakan `tokens_per_second` dari jumlah kata, bukan tokenizer token nyata |
| 7 | Telemetry latency/RAM/quantisasi | ⚠️ | Partial; telemetri kinerja dasar ada, RAM/quant detail tidak jelas di UI |
| 8 | 5 tab GUI dan fitur catalog | ⚠️ | Docs detail; perlu verifikasi visual manual UI |
| 9 | CLI commands `aq help`, `aq doctor`, dll. | ✅ | `opencode`? AQRuntime CLI `aq` memiliki command sesuai README/codebase |
| 9 | OpenAI-compatible REST API | ✅ | Didukung dan diperkuat patch streaming/tool/audio |
| 10 | AQRuntime unggul vs Ollama/LM Studio | ⚠️ | Perlu bukti benchmark eksternal; tabel adalah marketing claim |
| 11 | Live demo 3 menit offline | ⚠️ | Speech Recognition browser memerlukan dukungan browser, model lokal tetap harus terpasang |
| 12 | Cloud Run hybrid future | ⚠️ | Roadmap, bukan fitur v2.4 saat ini |
| 12 | PQC/quantum roadmap | ⚠️ | Visi masa depan, bukan implementasi saat ini |

## Klaim Teknis yang Perlu Diperhatikan Saat Presentasi

### 1. Speech-to-Text belum nyata
Slide dan README menyatakan STT lokal via Whisper. Namun implementasi saat ini:
- `/api/audio/transcribe` mengembalikan teks simulasi.
- `/v1/audio/transcriptions` multipart juga mengembalikan teks simulasi.
- Browser juga memakai `SpeechRecognition`, tetapi ini bukan Whisper lokal actual inference.

**Rekomendasi**:
- Sebutkan STT sebagai "simulated / browser-assisted" bila demo tidak memakai Whisper asli.
- Jangan klaim transkripsi nyata sampai `AudioProcessor.transcribe_audio_payload` diganti model Whisper actual.

### 2. Vision belum nyata
Slide menyatakan analisis gambar dengan Vision Canvas. Namun:
- `VisionProcessor.describe_image_simulated` menghasilkan teks template.
- Patch terbaru menolak request image untuk model non-vision.

**Rekomendasi**:
- Sebutkan sebagai *experimental vision capability* / *simulated analysis*.
- Jangan klaim model benar-benar "melihat" gambar.

### 3. Telemetry tok/s adalah estimasi
`InferenceEngine.generate` memperkirakan:

```text
est_tokens = len(response.split())
```

Jadi `tokens_per_second` adalah estimasi kata/detik, bukan tokenizer token nyata.

**Rekomendasi**:
- Sebutkan "rough throughput estimate" jika ditanya teknis.
- Jangan klaim token accounting exact.

### 4. Hardware fallback
Urutan slide:
```text
NPU -> Arc -> DirectML -> CUDA -> CPU
```

Urutan implementasi prioritas:
```text
Intel OpenVINO (10) -> DirectML (15) -> CUDA (20) -> ONNX (25) -> CPU (30)
```

**Catatan**:
Intel OpenVINO menangani NPU/Arc, jadi secara penggunaan tetap wajar.
Untuk presentasi akademis/teknis, sebut arsitektur provider prioritas, bukan narasi hardware terlalu literal.

### 5. OpenAI Compatibility Setelah Patch
Klaim `aq serve` kompatibel OpenAI sekarang **lebih kuat dan benar** karena:
- streaming SSE,
- multi-turn messages,
- generic tool calling,
- audio multipart OpenAI-style,
- error response OpenAI-style.

Ini dapat dipertahankan dalam presentasi.

## Kesimpulan Audit

### Klaim yang aman dipresentasikan
- Hardware priority fallback
- GUI + CLI
- OpenAI-compatible REST API
- Streaming / full messages / generic tools (setelah patch)
- Dokumen binary guard 4500 char
- Max tokens 64–8192
- Web Speech TTS
- Vocabulary/model catalog GGUF Q4/Q5

### Klaim yang harus dilunakkan
- STT lokal via Whisper (masih simulasi)
- Vision real analysis
- Token telemetry exact (`tok/s` nyata)
- 100% offline pada semua mode (karena ada cloud providers opsional)
- "Native Mic STT" jika diartikan Whisper lokal actual

### Klaim future (roadmap, bukan fitur jadi)
- Cloud Run hybrid
- PQC/blockchain/quantum circuit integration

## Rekomendasi untuk Slide Deck

1. Ganti "Voice STT via Whisper" menjadi:
   > "Voice input via browser SpeechRecognition, with simulated local audio endpoint."
2. Ganti "Vision Model Analysis" menjadi:
   > "Experimental multimodal payload support."
3. Ganti telemetri menjadi:
   > "Estimated generation throughput (tok/s approximate)."
4. Tegaskan OpenCode/OpenAI compatibility sebagai nilai kuat modern.
5. Jelaskan cloud providers sebagai opsional, bukan default offline.