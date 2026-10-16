# Strategi Bungkus AQRuntime untuk AI Builder Cup

Dokumen ini menjelaskan bagaimana **AQRuntime v2.4.0** dapat diadaptasi
 agar sesuai dengan persyaratan AI Builder Cup.

## Ringkasan Persyaratan Peserta

Berdasarkan email undangan:
- Memilih salah satu problem statement.
- Tim 2–4 anggota.
- Submission harus **functional solution**, bukan ide/slide-only.
- Semua model AI (Gemini) atau agentic platform (Agent Platform / Antigravity / AI Studio).
- Deploy di Google Cloud Platform via **Cloud Run** atau **Firebase**.
- Deadline: **18 October 2026**.

## Mapping AQRuntime ke Persyaratan

### 1. Problem Statement yang paling cocok
**BFSI — intelligent risk, fraud, and financial experiences**

Alasan:
- AQRuntime sangat cocok untuk **privacy-first financial document analysis**.
- Mode local-first berguna untuk data sensitif (KYC, dokumen nasabah, laporan kredit).
- Agent loop + tool calling bisa dipakai untuk audit dokumen.
- REST API OpenAI-compatible memudahkan integrasi.

Solusi yang diajukan:
> **AQRuntime Secure Financial Analyst** — on-device AI engine untuk analisis dokumen keuangan sensitif, dengan fallback cloud Google Gemini untuk workload kompleks dan deployment di GCP.

### 2. Google AI Requirement
AQRuntime saat ini sangat berfokus pada model lokal dan belum memakai Google AI.

Agar memenuhi syarat, tambahkan salah satu:
- **Gemini 2.5 Flash / 2.5 Pro** via Google AI Studio / Vertex AI
- **Agent Platform / Antigravity / AI Studio** sebagai agentic layer
- atau gunakan Gemini sebagai:
  - cloud fallback
  - summarization engine
  - policy-compliance checker
  - final answer verifier

Rekomendasi desain:
- Model lokal AQRuntime menangani data sensitif.
- Google Gemini menangani:
  - analisis kompleks,
  - summary,
  - cross-check,
  - export report.

### 3. Arsitektur yang Disarankan

```text
Client (Browser / OpenCode / API)
        |
        v
AQRuntime Local Engine  ---- (offline / privacy-first)
        |
        |---> Local GGUF / HF models (sensitive data)
        |
        '---> Google Cloud Gateway (Cloud Run)
                    |
                    '---> Gemini API / Vertex AI
```

Mode:
- `privacy_mode = local`: dokumen sensitif tidak keluar.
- `cloud_mode = gemini`: fallback ke Gemini bila workload kompleks.
- AQRuntime mengirim ringkasan anonim / context aman, bukan dokumen mentah.

### 4. Minimum Viable Submission

Agar lolos submission, minimal fitur demo:
1. Upload dokumen keuangan.
2. Chat dengan dokumen secara lokal via AQRuntime.
3. Ringkasan risk/fraud risk dari dokumen.
4. Satu call ke Google Gemini untuk:
   - executive summary,
   - compliance checklist,
   - risk scoring explanation.
5. Deploy gateway ke Cloud Run.
6. Dokumen (README, demo video, deployment URL).

### 5. Mapping Fitur Existing AQRuntime ke Submission

| Fitur AQRuntime | Nilai untuk hackathon |
|---|---|
| Local LLM chat | Privacy-first financial analysis |
| Streaming SSE | Fast analyst response |
| Document attachment | Dokumen kredit / laporan |
| Generic tool calling | Audit workflow / ekstraksi field |
| OpenAI-compatible API | Integrasi enterprise mudah |
| Web Control Center | Demo tanpa terminal |
| Warm cache | Inference berulang stabil |

### 6. GAP Saat Ini vs Persyaratan Hackathon

| Persyaratan | Status AQRuntime |
|---|---|
| Google AI / agentic platform | Belum ada |
| Deploy Cloud Run/Firebase | Belum ada |
| Submission functional | Sebagian (lokal) |
| Tim 2–4 | TBD |
| Problem statement | Perlu pilih (disarankan BFSI) |
| Credits / mentorship | Didukung panitia |

### 7. Langkah Implementasi yang Disarankan

#### Minggu 1
- Pilih BFSI
- Form tim 2–4
- Jawab use case: "Private financial document analyst"

#### Minggu 2
- Tambah Gemini integration:
  - env `GEMINI_API_KEY`
  - provider `cloud_gemini`
  - endpoint `/api/gemini/executive-summary`
- Buat report dari hasil chat lokal
- Buat package deploy

#### Minggu 3
- Deploy Cloud Run
- Uji demo
- Rekam video submission
- Lengkapi dokumentasi

### 8. Deployment Plan (Cloud Run)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD python -m aq serve --host 0.0.0.0 --port 8080
```

Commands cloud:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/aqruntime-cup
gcloud run deploy aqruntime-cup \
  --image gcr.io/PROJECT_ID/aqruntime-cup \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=YOUR_KEY
```

Catatan:
- Cloud Run memakai port 8080.
- Firebase opsional, tetapi Cloud Run lebih cocok.
- Local model bisa tetap dieksekusi di demo laptop via AQRuntime.

### 9. Perbaikan Fitur Agar "Benar-benar sesuai klaim"

Sebelum submit, pastikan:
- Klaim STT disebut "simulated/local endpoint" bila Whisper actual belum diimplementasi.
- Klaim Vision disebut "experimental simulated".
- Telemetry disebut "estimated throughput".
- GCP + Google AI integration aktif.
- Demo tidak menyatakan model cloud jika tidak dipakai.

### 10. Roadmap AI Builder Cup

- **Hari 1-2**: pilih domain BFSI, bentuk tim
- **Hari 3-5**: integrasi Gemini + demo workflow
- **Hari 6-7**: deploy Cloud Run
- **Hari 8**: video demo + README + arsitektur
- **Deadline Oct 18, 2026**: submit final

### 11. Kesimpulan

AQRuntime bisa menjadi backbone submission:
- privacy-first local AI,
- telemetri dan stream,
- attachment reader,
- proxy/gateway GCP,
- optional OpenCode integration for developer workflow.

Agar sesuai hackathon, kunci utamanya:
- gunakan Google AI (Gemini) secara nyata,
- deploy di Google Cloud,
- presentasikan jujur mana fitur siap dan mana roadmap.