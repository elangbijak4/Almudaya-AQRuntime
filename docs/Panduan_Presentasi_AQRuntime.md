# 📊 Panduan Lengkap Presentasi & Pitch Deck: AQRuntime
**Oleh**: Almudaya Quantum Labs  
**Produk**: AQRuntime (Almudaya Quantum Runtime v2.4.0)  
**Dokumen Acuan Pembuatan Slide Presentasi**

> **Catatan Capabilitas Aktual v2.4.0 (setelah Patch 7)**  
> - **Voice STT**: UI memakai browser Speech Recognition; endpoint `POST /api/audio/transcribe` dan `/v1/audio/transcriptions` masih mengembalikan transkripsi **simulasi**, bukan Whisper nyata.  
> - **TTS Read Aloud**: HTML5 Web Speech Synthesis (zero cloud cost).  
> - **Vision**: Payload multimodal didukung, tetapi analisis gambar bersifat template/simulasi (tidak real vision model).  
> - **Telemetry `tok/s`**: estimasi throughput berbasis tokenizer bila tersedia, fallback jumlah kata/detik.  
> - **Offline**: mode lokal tetap bergantung model yang sudah terunduh; provider cloud (OpenAI/Hugging Face) bersifat opsional.

---

## 📑 Struktur Slide Presentasi (Slide-by-Slide Outline)

Panduan ini disusun dalam format **Slide Deck Terstruktur**, lengkap dengan:
- **Judul Slide**
- **Poin Kunci Visual (Bullet Points)**
- **Catatan Pembicara (Speaker Notes / Script)**
- **Petunjuk Visual / Tangkapan Layar yang Disarankan**

---

### 🎬 Slide 1: Judul & Identitas Startup
* **Judul Utama**: AQRuntime: Next-Generation Local AI Execution Engine
* **Sub-judul**: *Run Local AI Models with Privacy-First Design. Browser Voice UI, OpenAI-Compatible API, and Honest Capability Metadata.*
* **Penyaji / Organisasi**: **Almudaya Quantum Labs**
* **Elemen Visual**: Logo AQRuntime, badge status: `v2.4.0 Stable`, `Open Source MIT`, `Intel Core Ultra / Arc / CUDA Ready`.
* **Catatan Pembicara**:
  > *"Assalamu’alaikum Warahmatullahi Wabarakatuh dan selamat pagi/siang. Saya mempersembahkan AQRuntime—sebuah local AI runtime engine performa tinggi yang dibangun oleh startup kami, Almudaya Quantum Labs. AQRuntime memungkinkan siapa pun menjalankan model kecerdasan buatan mutakhir (bahasa, penglihatan, dan suara) secara mandiri di perangkat laptop atau PC mereka tanpa koneksi internet, tanpa biaya langganan cloud, dan dengan privasi data yang terjamin seratus persen."*

---

### 🚨 Slide 2: Latar Belakang Masalah (The Problem)
* **Judul**: Dilema AI Cloud & Tantangan Komputasi Lokal
* **Poin Masalah**:
  1. **Privasi & Kebocoran Data Rahasia**: Perusahaan, perbankan, dan instansi dilarang mengunggah dokumen sensitif ke server publik cloud (ChatGPT, cloud API).
  2. **Biaya Langganan & Ketergantungan Internet**: Biaya API cloud terus membengkak dan lumpuh total saat koneksi internet terputus di daerah 3T.
  3. **Hardware AI PC Perlu Utilisasi yang Nyata**: Laptop generasi baru sudah memiliki NPU, iGPU, GPU, dan CPU, tetapi akselerasinya bertambah baik hanya jika provider driver, model, dan jalur fallback sesuai dengan kapabilitas mesin.
  4. **Keterbatasan Antarmuka & Capability Honesty**: UI lokal sering minim fitur suara/file, dan klaim multimodal harus dibatasi sesuai implementasi nyata. AQRuntime menyediakan GUI Web, attachment, dan voice input browser, tetapi STT backend dan vision tetap level simulasi/experimental.
* **Catatan Pembicara**:
  > *"Saat ini ada benturan besar di industri: organisasi ingin menggunakan AI, tapi takut data internal bocor ke cloud. Di sisi lain, hardware PC modern sebenarnya sudah memiliki NPU dan GPU bawaan yang sangat bertenaga, tetapi belum ada engine lokal yang mudah dipakai dan mengoptimalkan seluruh hardware tersebut secara otomatis."*

---

### 💡 Slide 3: Solusi Kami (The Solution)
* **Judul**: AQRuntime — AI Lokal Cepat, Mandiri, dan Multimodal
* **Pilar Solusi**:
  * **Local-First & Privacy-First**: Bobot model dan data percakapan dapat berjalan di RAM dan disk lokal. mode offline tergantung model yang sudah terpasang; provider cloud bersifat opsional dan dapat mengirim prompt ke cloud.
  * **Akselerasi Majemuk Cerdas**: Mendukung rantai fallback hardware otomatis: *Intel NPU ➔ Intel Arc iGPU ➔ DirectML ➔ CUDA ➔ CPU*.
  * **Multimodal Input Terintegrasi**: Mendukung input visual Base64, voice input via browser (Speech Recognition), dan TTS Web Speech. STT backend dan analisis vision tetap honest/simulated, bukan model nyata.
  * **Dua Antarmuka Terpadu**: Tersedia dalam bentuk **Web Control Center GUI (Browser)** yang modern dan **CLI Command** yang lengkap bagi developer.
* **Catatan Pembicara**:
  > *"AQRuntime hadir sebagai jembatan. Kami memberikan kebebasan komputasi AI penuh di tangan pengguna. Anda bisa membawa laptop ke pelosok tanpa sinyal, dan asisten AI Anda tetap berpikir cepat, mendengar suara Anda, melihat gambar Anda, dan menjaga dokumen Anda tetap aman di perangkat Anda sendiri."*

---

### 🌌 Slide 4: Visi Saintifik & Almudaya Quantum Labs
* **Judul**: Visi Jauh: Menuju Konvergensi AI, Blockchain & Sirkuit Kuantum
* **Poin Kunci**:
  * **Asal Nama AQRuntime**: *Almudaya Quantum Runtime*.
  * **Filosofi Kuantum**: Kata "Quantum" merepresentasikan roadmap jangka panjang riset Almudaya Quantum Labs: **menempatkan kecerdasan AI, keandalan desentralisasi Blockchain (PQC), dan komputasi sirkuit kuantum dalam satu ekosistem terpadu**.
  * **Metodologi Rekayasa Perangkat Lunak**:
    * Dimulai dengan graf dokumentasi terstruktur (**Waterfall Documentation Baselines** dari v0.1 hingga v2.4).
    * Berevolusi dengan iterasi berulang yang teruji secara empiris mengikuti **Spiral Model** untuk memitigasi risiko hardware driver dan integrasi multimodal.
* **Catatan Pembicara**:
  > *"Nama AQRuntime bukan sekadar nama produk, melainkan visi ilmiah Almudaya Quantum Labs. Kami percaya masa depan komputasi akan mempertemukan AI cerdas, keamanan kriptografi pasca-kuantum di blockchain, serta percepatan sirkuit kuantum. Pengembangan engine ini dimulai secara ketat dengan metodologi Waterfall baseline dokumen, lalu berevolusi secara tangguh melalui Spiral Model dengan puluhan rangkaian automated test."*

---

### ⚡ Slide 5: Arsitektur Hardware & Rantai Akselerasi (Hardware Fallback Chain)
* **Judul**: Heterogeneous Hardware Priority Fallback Chain
* **Diagram Alur (Priority Chain)**:
  ```text
  [Input User] 
       │
       ▼
  [Intel NPU via OpenVINO] ──(Jika tersedia)──► Eksekusi Hemat Daya (Ultra-Efficient)
       │ (Jika tidak ada)
  [Intel Arc iGPU] ──────────(Jika tersedia)──► Akselerasi Grafis Tinggi
       │ (Jika tidak ada)
  [DirectML (DirectX 12)] ───(Jika tersedia)──► Kompatibilitas Windows GPU Universal
       │ (Jika tidak ada)
  [NVIDIA CUDA] ─────────────(Jika tersedia)──► GPU Discrete Eksternal
       │ (Jika tidak ada)
  [Multi-Core CPU] ──────────(Default)────────► Komputasi Thread CPU Teroptimasi
  ```
* **Kelebihan**: Pengguna tidak perlu pusing menyetel konfigurasi driver yang rumit—AQRuntime mendeteksi dan memilih jalur tercepat secara otomatis.
* **Catatan Pembicara**:
  > *"Inilah inti keunggulan teknis AQRuntime: Priority Fallback Chain. Saat dijalankan di laptop AI modern seperti Intel Core Ultra, ia langsung memanfaatkan NPU untuk efisiensi daya. Jika tidak ada, ia otomatis beralih ke Arc GPU, lalu DirectML, CUDA, hingga CPU. Tidak ada kegagalan crash karena salah driver."*

---

### 🎙️ Slide 6: Fitur Unggulan 1 — Voice Audio & Multimodal Vision
* **Judul**: Bukan Sekadar Chatbot Teks: Suara & Penglihatan Bawaan
* **Fitur Voice Engine (`🎙️` & `🔊`)**:
  * **Speech-to-Text (STT)**: Tombol rekam mikrofon memakai browser Speech Recognition; endpoint backend `/api/audio/transcribe` dan `/v1/audio/transcriptions` tersedia, tetapi respons STT sekarang berstatus `simulated`, bukan Whisper nyata.
  * **Text-to-Speech (TTS)**: Tombol *Read Aloud* memakai HTML5 Web Speech Synthesis di browser; ini bukan model suara lokal, dan latensi tergantung browser/device.
  * **Katalog Model Suara**: Model transkripsi suara lokal terdedikasi (misal *OpenAI Whisper-Tiny* ~390 MB).
* **Fitur Vision Engine (`🖼️`)**:
  * **Live Thumbnail Preview Canvas**: Unggah file gambar (`.png`, `.jpg`, `.webp`) langsung di jendela chat.
  * **Payload Multimodal Base64**: Pesan image OpenAI-style diekstrak dan diteruskan, tetapi analisis visual bersifat simulasi; request image ditolak jika model bukan kelas vision. Integrasi vision model nyata masih roadmap.
* **Catatan Pembicara**:
  > *"Di AQRuntime, interaksi menjadi alami layaknya berbicara dengan rekan kerja. Anda bisa menekan tombol mic dan berbicara langsung, mendengarkan balasan AI dibacakan dengan suara alami, serta mengunggah gambar arsitektur atau foto untuk dianalisis secara instan di kanvas multimodal."*

---

### 📎 Slide 7: Fitur Unggulan 2 — Pembaca Dokumen, Kontrol Token & Telemetri
* **Judul**: Produktivitas Kantor Tanpa Batas & Kendali Penuh Pengguna
* **Tiga Fitur Kunci**:
  1. **Document & Code Attachment Reader (`📎`)**:
     * Unggah berkas `.py`, `.txt`, `.json`, `.md`, `.csv`.
     * Dilengkapi **Binary Guard** untuk mencegah crash memori jika pengguna tidak sengaja mengunggah file biner (Word/Zip) dan proteksi batas 4.500 karakter.
  2. **Dynamic Max Output Tokens Slider (`64` - `8.192` Token)**:
     * Pengguna bebas memilih: jawaban singkat cepat (128 token) atau draf dokumen/naskah laporan panjang (hingga 8.192 token).
  3. **Real-time Performance Telemetry**:
     * Setiap jawaban AI memunculkan lencana kinerja langsung (estimasi), termasuk throughput, latency, dan jumlah token. Nilai `tok/s` memakai tokenizer bila tersedia atau fallback jumlah kata/detik. Estimasi RAM/quantisasi model bergantung implementasi runtime.
* **Catatan Pembicara**:
  > *"Bagi pekerja profesional, dua fitur ini sangat krusial: kemampuan melampirkan berkas dokumen atau script kode dengan perlindungan anti-crash, serta slider Max Tokens yang fleksibel. Jika pengguna butuh artikel panjang, tinggal geser slider ke 4096 atau 8192 token. Kecepatan kata per detik (tok/s) juga ditampilkan transparan di setiap gelembung chat."*

---

### 🖥️ Slide 8: Tur Antarmuka — AQRuntime Control Center (5 Tab GUI)
* **Judul**: Web Control Center GUI yang Elegan & Intuitif
* **Penjelasan 5 Tab Utama**:
  * **Tab 1 — Chat & Infer**: Ruang percakapan utama, pemilihan model, slider token, tombol mic/gambar/lampiran, galeri persona preset, dan tombol ekspor Markdown (`.md`).
  * **Tab 2 — Installed Models**: Manajer penyimpanan model lokal, informasi ukuran gigabyte, dan label kuantisasi (`[GGUF Q4_K_M]`).
  * **Tab 3 — Model Hub**: Katalog online terintegrasi ke Hugging Face dengan tombol filter instan (GGUF 4-Bit, NVIDIA, Vision, Audio) dan unduh 1-Click Pull.
  * **Tab 4 — Memory Manager**: Pengatur memori jangka panjang percakapan (bisa salin memori antar model dan ekspor log).
  * **Tab 5 — Settings & Diagnostics**: Audit kesehatan sistem hardware laptop secara real-time dan pengaturan token Hugging Face.
* **Catatan Pembicara**:
  > *"Kami mendesain antarmuka AQRuntime dengan gaya Dark Glassmorphism modern. Pengguna tidak perlu menghafal baris perintah—cukup buka antarmuka Web Control Center, semua fungsi dari unduh model, seting hardware, chat suara, hingga ekspor chat ada dalam 5 tab yang rapi."*

---

### 💻 Slide 9: Pengalaman Pengembang (Developer CLI Suite)
* **Judul**: Developer-Friendly: CLI Suite yang Ringkas & Bertenaga
* **Daftar Perintah Esensial**:
  ```bash
  # 1. Bantuan lengkap seluruh perintah dan parameter
  aq help

  # 2. Audit hardware & kesiapan sistem
  aq doctor

  # 3. Rekomendasi model cerdas sesuai RAM laptop
  aq discover gguf       # Model hemat 4-bit
  aq discover audio      # Model suara

  # 4. Unduh model otomatis di latar belakang
  aq pull bartowski/gemma-2-2b-it-GGUF

  # 5. Eksekusi chat interaktif via terminal dengan batas token custom
  aq run bartowski/gemma-2-2b-it-GGUF --max-tokens 2048

  # 6. Jalankan Web Control Center atau REST API Server (OpenAI Compatible)
  aq ui                  # Buka Web Dashboard di browser
  aq serve               # Jalankan REST API server port 8000
  ```
* **Catatan Pembicara**:
  > *"Bagi kalangan insinyur dan developer, AQRuntime menyediakan CLI yang bersih. Perintah `aq help` dan `aq doctor` mempermudah onboarding. Ditambah lagi, perintah `aq serve` otomatis menyediakan REST API yang kompatibel dengan format standar OpenAI, sehingga bisa dihubungkan ke aplikasi luar apa pun."*

---

### 📊 Slide 10: Matriks Komparasi (AQRuntime vs. Ollama vs. LM Studio)
* **Judul**: Posisi Kompetitif: Mengapa AQRuntime Lebih Unggul?

| Fitur / Kemampuan | ⚡ AQRuntime | 🦙 Ollama | 🖥️ LM Studio |
|---|:---:|:---:|:---:|
| **Akselerasi Intel NPU (OpenVINO)** | **✅ Native & Otomatis** | ❌ Terbatas/Eksperimental | ❌ Belum Optimal |
| **Hardware Priority Chain (NPU➔GPU➔CPU)** | **✅ Otomatis Smart Fallback** | ⚠️ Statis GPU/CPU | ⚠️ Slider GPU manual |
| **Voice Engine (Mic STT + Read Aloud TTS)** | **✅ Terintegrasi Penuh** | ❌ Tidak Ada | ❌ Tidak Ada |
| **Multimodal Vision Canvas (`🖼️`)** | **✅ Live Preview & Base64** | ⚠️ CLI / Basic API | ✅ Ada GUI |
| **Document Reader + Binary Guard (`📎`)** | **✅ Terintegrasi Aman** | ❌ Salin manual | ⚠️ Drag-drop dasar |
| **Pengatur Panjang Token (`max_tokens`)** | **✅ Slider GUI & CLI Flag** | ⚠️ Parameter CLI | ✅ Sidebar Settings |
| **Telemetri Kecepatan Real-time (`tok/s`)** | **✅ Badge Langsung di Chat** | ⚠️ Log Terminal | ⚠️ Statistik Minimal |
| **Lisensi Kode Sumber** | **✅ 100% MIT Open Source** | ✅ MIT Open Source | ❌ Proprietary (Tertutup) |

* **Catatan Pembicara**:
  > *"Bisa kita lihat pada tabel komparasi ini: Ollama sangat bagus di CLI tetapi minim fitur multimodal dan dukungan NPU-nya terbatas. LM Studio memiliki antarmuka yang bagus namun sifatnya closed-source dan tidak memiliki fitur voice. AQRuntime menggabungkan keterbukaan open-source, efisiensi NPU PC lokal, dan kelengkapan multimodal dalam satu paket."*

---

### 🎯 Slide 11: Panduan Skenario Demo Langsung (Live Demo Script - 3 Menit)
* **Judul**: Skenario Live Demo Produk (3-Minute Winning Demo)
* **Langkah Demonstrasi**:
  1. **Menit 01:00 — Membuka Control Center**:
     * Jalankan `aq ui` di terminal.
     * Tunjukkan browser membuka dashboard `http://127.0.0.1:8000/ui`.
     * Tunjukkan Tab 5 (Settings/Doctor) yang mendeteksi NPU/CPU dan RAM secara akurat.
  2. **Menit 02:00 — Interaksi Multimodal & Dokumen**:
     * Masuk ke Tab 1 (Chat & Infer).
     * Klik tombol mikrofon (`🎙️`), ucapkan pertanyaan singkat dalam bahasa Indonesia.
     * Tunjukkan AI menjawab cepat dengan badge telemetri (`⚡ tok/s`).
     * Klik tombol `🔊 Read Aloud` untuk memperdengarkan suara jawaban AI.
     * Lampirkan file teks kecil (`📎`) dan minta AI membuat rangkuman.
  3. **Menit 03:00 — Fleksibilitas Model Hub & Ekspor**:
     * Buka Tab 3 (Model Hub) untuk memperlihatkan katalog 1-Click Pull GGUF dan Whisper Audio.
     * Kembali ke Tab 1 dan klik `📥 Export Chat (.md)` untuk mengunduh hasil kerja.
* **Catatan Pembicara**:
  > *"Dalam demo 3 menit ini, juri atau audiens langsung menyaksikan sendiri: engine berjalan mulus tanpa koneksi internet sama sekali, merespons suara, membaca file, dan menghasilkan teks berkecepatan tinggi."*

---

### 🚀 Slide 12: Kesimpulan & Rencana Masa Depan (Roadmap)
* **Judul**: Roadmap Menuju Masa Depan & Penutup
* **Tahapan Roadmap**:
  * **Fase Saat Ini (v2.4.0)**: Engine AI lokal stabil (LLM, Vision, Voice, NPU Acceleration, GGUF 4-bit, REST API).
  * **Fase Berikutnya (Cloud Run Hybrid)**: Kemampuan hybrid edge-to-cloud untuk sinkronisasi model enterprise dengan Google Cloud Run.
  * **Visi Almudaya Quantum Labs**: Integrasi enkripsi audit pasca-kuantum (PQC) dan komputasi sirkuit kuantum untuk verifikasi integritas model.
* **Call to Action**:
  * Repositori GitHub: `https://github.com/elangbijak4/Almudaya-AQRuntime`
  * Kontak Tim: **Almudaya Quantum Labs**
* **Catatan Pembicara**:
  > *"AQRuntime adalah bukti bahwa teknologi AI tercanggih dapat dirasakan secara demokratis, aman, dan berdaulat di perangkat masing-masing pengguna. Terima kasih atas perhatian bapak/ibu sekalian. Kami membuka sesi tanya jawab."*

---

## 💡 Tips Tambahan untuk Desain Slide:
1. **Pilihan Tema Warna Slide**: Gunakan latar belakang gelap (*Deep Dark Blue / Space Black* `#0A0F1D`) dipadukan dengan aksen teks *Cyan Neon* (`#00F2FE`) dan *Purple Violet* (`#A855F7`) agar mencerminkan kesan AI modern dan nuansa "Quantum".
2. **Penggunaan Gambar**: Masukkan tangkapan layar asli aplikasi dari folder `docs/image/hero-screenshot.png` dan `docs/image/feature-screenshot.png` pada Slide 6, 7, dan 8.
3. **Simulasi Demo Offline**: Sebelum naik panggung presentasi, matikan Wi-Fi laptop untuk membuktikan secara spektakuler kepada audiens bahwa aplikasi ini 100% berjalan tanpa koneksi internet.
