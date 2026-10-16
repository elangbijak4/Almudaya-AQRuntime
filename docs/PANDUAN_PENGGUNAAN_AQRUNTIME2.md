# Panduan Penggunaan AQRuntime2

Panduan ini merujuk pada source AQRuntime2 versi **2.4.0** yang ada di checkout ini. Contoh Windows menggunakan PowerShell dan Python 3.12. Kinerja dan model yang dapat dijalankan bergantung pada isi folder `models/` dan perangkat komputer.

## 1. Menyiapkan Python 3.12

Buka PowerShell di akar proyek:

```powershell
cd D:\AQRuntime2
```

Periksa virtualenv yang sudah ada:

```powershell
.\.venv\Scripts\python.exe --version
```

Jika belum ada, buat virtualenv dengan Python 3.12:

```powershell
py -3.12 -m venv .venv
```

Jika `.venv` menunjuk ke versi Python lain atau tidak dapat dijalankan, buat environment baru agar yang lama tetap tersimpan:

```powershell
py -3.12 -m venv .venv312
.\.venv312\Scripts\python.exe -m pip install -e .
```

Untuk `.venv` yang valid, pasang proyek dalam mode editable dan pastikan versinya:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe --version
```

Versi yang diharapkan adalah `Python 3.12.x`. Menjalankan executable melalui `.venv\Scripts\python.exe` memastikan AQRuntime memakai interpreter environment tersebut walaupun versi Python lain juga terpasang.

Opsional, aktifkan virtualenv agar perintah `aq` dapat dipanggil langsung:

```powershell
.\.venv\Scripts\Activate.ps1
```

Jika tidak mengaktifkannya, jalankan perintah melalui `python -m aq` setelah instalasi editable, atau gunakan path executable `.venv\Scripts\python.exe`.

## 2. Menjalankan aplikasi

Jalankan Control Center:

```powershell
.\.venv\Scripts\python.exe -m aq ui
```

Buka [http://127.0.0.1:8000/ui](http://127.0.0.1:8000/ui). Biarkan terminal tetap terbuka selama aplikasi digunakan. Tekan `Ctrl+C` di terminal untuk menghentikan server.

Jika port 8000 sudah dipakai:

```powershell
.\.venv\Scripts\python.exe -m aq ui --port 8765
```

Lalu buka `http://127.0.0.1:8765/ui`. Untuk menjalankan API tanpa membuka browser:

```powershell
.\.venv\Scripts\python.exe -m aq serve --host 127.0.0.1 --port 8000
```

Gunakan `127.0.0.1` untuk akses lokal. `0.0.0.0` membuat server dapat dijangkau dari jaringan.

## 3. Menggunakan Control Center

### Chat & Infer

1. Pilih model teks terpasang pada **Active Model**.
2. Tulis pesan dan tekan **Send** atau Enter.
3. Atur **Max Output Tokens** untuk membatasi panjang jawaban. Nilai yang lebih besar dapat menambah waktu generasi dan penggunaan memori.
4. **New Chat** membersihkan sesi model yang dipilih setelah konfirmasi.
5. **Export (.md)** mengunduh tampilan percakapan sebagai Markdown.
6. Tombol mikrofon menggunakan Web Speech API browser jika tersedia.
7. **Read Aloud** memakai text-to-speech browser.

> **Batasan UI yang diketahui:** pilihan hardware runtime dan persona/system prompt tampil di halaman, tetapi permintaan chat UI saat ini tidak meneruskan pilihan runtime sebagai parameter `provider` atau system prompt ke backend. Jangan mengandalkan kontrol tersebut untuk memilih backend atau mengubah instruksi model.

### Model Hub

- Cari model lewat kolom pencarian atau filter GGUF, NVIDIA, Vision, dan Audio.
- Katalog diambil dari internet jika tersedia; saat luring, aplikasi dapat memakai katalog cache.
- Periksa ukuran unduhan dan kecocokan perangkat sebelum mengunduh. Proses download memerlukan internet dan ruang disk.
- Untuk model gated, terima lisensinya di Hugging Face dan simpan token dengan `aq login` atau halaman Settings. Jangan bagikan token.

### Installed

Menampilkan model dalam folder lokal `models/`. Menghapus model akan menghapus folder bobotnya dari disk.

### Hardware Doctor

Menampilkan informasi perangkat yang dapat dibaca aplikasi. Perkiraan kompatibilitas bukan jaminan model akan berjalan cepat atau muat di memori.

### Settings

> Mengelola token Hugging Face dan sesi memori. Token hanya diperlukan untuk model yang meminta autentikasi atau persetujuan lisensi.

## 4. Perintah CLI

Jalankan dari akar proyek dengan virtualenv aktif, atau awali perintah dengan `python -m aq`.

| Perintah | Fungsi |
| --- | --- |
| `aq help` | Ringkasan bantuan CLI. |
| `aq version` | Versi AQRuntime. |
| `aq doctor` | Pemeriksaan kapasitas perangkat. |
| `aq runtime list` | Status provider yang tersedia. |
| `aq runtime info cpu` | Informasi provider CPU. Ganti `cpu` dengan provider yang ingin diperiksa. |
| `aq list` | Model yang terpasang lokal. |
| `aq discover gemma` | Mencari katalog dengan kata kunci. Tanpa kata kunci, menampilkan rekomendasi katalog. |
| `aq pull bartowski/gemma-2-2b-it-GGUF` | Mengunduh repositori Hugging Face tersebut. Perintah meminta konfirmasi ukuran. |
| `aq run bartowski-gemma-2-2b-it-gguf` | Chat interaktif dengan model terpasang. Ketik `exit` untuk keluar. |
| `aq memory list` | Melihat sesi memori tersimpan. |
| `aq memory clear NAMA_SESI` | Menghapus memori sesi. Periksa nama sesi terlebih dahulu. |
| `aq memory export NAMA_SESI` | Mengekspor sesi ke Markdown. |
| `aq remove NAMA_MODEL` | Menghapus bobot model dari disk. |

Nama untuk `aq pull` adalah ID repositori Hugging Face; `aq run` dan API memakai nama model lokal yang ditampilkan oleh `aq list`.

Contoh chat CLI tanpa menyimpan memori:

```powershell
aq run bartowski-gemma-2-2b-it-gguf --no-memory --max-tokens 256
```

## 5. API lokal kompatibel OpenAI

Jalankan server:

```powershell
aq serve --host 127.0.0.1 --port 8000
```

| Method | Path | Keterangan |
| --- | --- | --- |
| `GET` | `/health` | Status server dan versi. |
| `GET` | `/v1/models` | Daftar model chat lokal. |
| `GET` | `/api/models/capabilities` | Daftar model dan kapabilitas yang dilaporkan. |
| `GET` | `/api/runtimes` | Status provider runtime. |
| `GET` | `/api/doctor` | Informasi diagnosis perangkat. |
| `POST` | `/v1/chat/completions` | Chat teks atau streaming SSE. |
| `POST` | `/v1/audio/transcriptions` | Unggah audio bergaya OpenAI; hasil saat ini simulasi. |

Contoh request dari PowerShell:

```powershell
$body = @{
  model = 'bartowski-gemma-2-2b-it-gguf'
  messages = @(@{ role = 'user'; content = 'Jelaskan tensor secara singkat.' })
  max_tokens = 128
} | ConvertTo-Json -Depth 8

Invoke-RestMethod `
  -Uri 'http://127.0.0.1:8000/v1/chat/completions' `
  -Method Post `
  -ContentType 'application/json' `
  -Body $body
```

Contoh body JSON:

```json
{
  "model": "bartowski-gemma-2-2b-it-gguf",
  "messages": [{"role": "user", "content": "Halo, jawab singkat."}],
  "max_tokens": 128,
  "stream": false
}
```

Untuk percakapan beberapa putaran, kirim seluruh riwayat `messages` (system, user, dan assistant) pada setiap request. Setel `"stream": true` untuk menerima Server-Sent Events.

## 6. Lokasi data

- `models/`: bobot model lokal.
- `config/runtime.yaml`: versi, lokasi model/log, panjang konteks, dan jumlah cache model. Jangan menyalin token rahasia ke dokumen atau repositori publik.
- `logs/`: log aplikasi.
- `memory/`: sesi percakapan persisten.
- `AQRUNTIME_HOME`: environment variable opsional untuk mengarahkan aplikasi ke root data proyek lain yang sesuai.

## 7. Batas fitur yang sudah diketahui

- **Chat teks lokal:** telah diuji pada Gemma GGUF melalui API lokal. Model tetap dapat memberikan jawaban faktual yang salah; verifikasi informasi penting.
- **Format dan kecepatan:** GGUF dapat dijalankan lewat `llama.cpp`; model non-GGUF memakai Transformers/PyTorch. Waktu muat, ukuran bobot, backend, panjang konteks, CPU/GPU, dan RAM memengaruhi kinerja. Model lebih kecil tidak selalu lebih cepat bila backend atau waktu pemuatannya berbeda.
- **GPU:** provider yang tidak tersedia dapat dilewati dan runtime beralih ke CPU. `WinError 4551` menunjukkan Windows Application Control memblokir file; mengganti versi Python saja belum tentu menyelesaikannya.
- **Gambar/Vision:** lampiran gambar diterima, tetapi analisis vision pada implementasi saat ini adalah simulasi, bukan inferensi vision nyata.
- **Transkripsi audio:** endpoint mengembalikan transkripsi simulasi, bukan hasil Whisper nyata. Tombol mikrofon UI menggunakan kemampuan browser.
- **Read Aloud:** suara dibuat oleh browser, bukan model TTS AQRuntime.
- **Lampiran berkas:** gunakan teks polos seperti `.txt`, `.md`, `.py`, `.json`, `.csv`, `.log`, `.c`, `.cpp`, dan `.h`. Ubah dokumen biner ke teks atau Markdown terlebih dahulu.
- **Privasi:** inferensi GGUF lokal berjalan di komputer. Pencarian dan download Model Hub memakai jaringan. Perilaku pemrosesan mikrofon bergantung pada browser.

## 8. Pemecahan masalah

### Memastikan virtualenv memakai Python 3.12

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip --version
```

Path pip semestinya berada di `D:\AQRuntime2\.venv\Lib\site-packages` jika memakai `.venv` proyek.

### Port 8000 sudah dipakai

Jalankan `aq ui --port 8765`, lalu buka `http://127.0.0.1:8765/ui`.

### Model gagal dimuat atau lambat

Periksa ID model lewat `aq list`, ruang disk, RAM, dan status provider lewat `aq runtime list`. Coba model GGUF lebih kecil atau turunkan `n_ctx` di `config/runtime.yaml`. Respons pertama dapat mencakup waktu pemuatan model.

### Error PyTorch/CUDA

Periksa `aq runtime list`. CUDA yang tidak tersedia dapat berarti GPU/driver tidak ditemukan atau DLL PyTorch gagal dimuat. Jika pesan menyebut Application Control/WinError 4551, periksa log Windows CodeIntegrity; menghapus Python 3.15 bukan langkah diagnosis pertama.

### Model gated gagal diunduh

Pastikan lisensi telah diterima di Hugging Face, lalu jalankan `aq login` dan masukkan token secara interaktif. Hindari menaruh token langsung di riwayat shell.

## 9. Pemeriksaan awal

```powershell
aq version
aq doctor
aq runtime list
aq list
```

Setelah server berjalan, periksa `http://127.0.0.1:8000/health` dan `http://127.0.0.1:8000/v1/models`.
