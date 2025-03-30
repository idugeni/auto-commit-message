# Auto Commit Message

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-brightgreen.svg)](https://conventionalcommits.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

<p align="center">
  <img src="https://opengraph.githubassets.com/856c5388bec324b86d5fb9acf0cc386418284ea1/idugeni/auto-commit-message" alt="Auto Commit Message" width="600">
</p>

<p align="center">
  <strong>Automated Conventional Commit Message Generation Powered by Google Gemini AI</strong>
</p>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#key-features">Key Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#commit-types">Commit Types</a> •
  <a href="#configuration">Configuration</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

---

## Overview

<p align="center">
  <a href="https://www.youtube.com/watch?v=lbaSAhxPpWY">
    <img src="https://img.youtube.com/vi/lbaSAhxPpWY/maxresdefault.jpg" alt="Git Commit Like a Pro! Use Gemini AI to Automate Perfect Messages!" width="600">
  </a>
</p>

Auto Commit Message adalah alat canggih yang dirancang untuk meningkatkan alur kerja Git Anda melalui pembuatan pesan commit yang didukung oleh AI. Dengan memanfaatkan model bahasa canggih Google Gemini, aplikasi ini menganalisis perubahan repositori untuk menghasilkan pesan commit yang tepat dan terstandarisasi sesuai dengan praktik terbaik.

Alat ini menjembatani kesenjangan antara pengembangan cepat dan dokumentasi yang komprehensif dengan memastikan setiap pesan commit mempertahankan standar profesional terlepas dari kompleksitas proyek atau ukuran tim.

## Key Features

- **Analisis Perubahan Cerdas**: Secara otomatis mendeteksi dan menginterpretasikan perubahan yang di-stage dalam repositori Git Anda
- **Pesan Berbasis AI**: Menggunakan API Google Gemini untuk menghasilkan pesan commit yang akurat secara kontekstual
- **Kepatuhan Conventional Commit**: Memastikan semua pesan yang dihasilkan mematuhi spesifikasi Conventional Commits
- **Validasi Repositori**: Memverifikasi direktori kerja adalah repositori Git yang valid sebelum eksekusi
- **Konfigurasi Terpusat**: Mempertahankan pengaturan global untuk penggunaan yang konsisten di berbagai proyek
- **Integrasi Perintah Git**: Terintegrasi dengan mulus dengan Git melalui alias kustom untuk alur kerja yang lancar
- **Penanganan Error**: Deteksi dan pelaporan error yang kuat dengan panduan yang jelas untuk penyelesaian
- **Dukungan Lintas Platform**: Kompatibel dengan lingkungan Windows dengan rencana ekspansi ke macOS dan Linux

## Installation

### Prerequisites

- Python 3.7 atau lebih tinggi
- Git versi 2.20 atau lebih tinggi
- Google Gemini API key

### Langkah-langkah Instalasi

1. **Verifikasi Instalasi Python**

   ```sh
   python --version
   ```

   *Jika tidak tersedia, unduh dan instal dari [python.org](https://www.python.org/)*

2. **Clone Repository**

   ```sh
   git clone https://github.com/idugeni/auto-commit-message.git
   cd auto-commit-message
   ```

3. **Jalankan Script Setup**

   ```sh
   setup.bat
   ```

   Ini akan membuat struktur direktori yang diperlukan di `C:\Tools\auto-commit-message\` dan menyalin file yang dibutuhkan.

4. **Instal Dependencies**

   ```sh
   pip install -r requirements.txt
   ```

   *jalankan perintah di folder `C:\Tools\auto-commit-message\`*

   atau

   ```bash
   pip install google-generativeai
   pip install python-dotenv
   ```

5. **Konfigurasi Akses API**

   Buat `.env.local` di `C:\Tools\auto-commit-message\` dengan API key Google Gemini Anda:

   ```sh
   GEMINI_API_KEY=your_api_key_here
   ```

6. **Konfigurasi Git Alias**

   Dokumen ini menyediakan instruksi tentang cara mengkonfigurasi alias Git untuk script `auto-commit-message`. Dua opsi disediakan: satu untuk semua pengguna (sistem-wide) dan satu untuk pengguna tertentu.

   - ***Alias Sistem-Wide (Semua Pengguna)***

   Konfigurasi ini berlaku untuk semua pengguna pada sistem. Memerlukan hak administrator.

   ```sh
   git config --system alias.acm '!C:/Program Files/Python313/python.exe C:/Tools/auto-commit-message/main.py' --replace-all
   ```

   *Catatan: Ini mengasumsikan Python diinstal di lokasi sistem-wide `(misalnya, C:/Program Files/Python313)`. Sesuaikan path Python jika diperlukan.*

   - ***Alias Pengguna-Spesifik***

   Konfigurasi ini hanya berlaku untuk pengguna saat ini.

   ```sh
   git config --global alias.acm '!C:/Users/%USERNAME%/AppData/Local/Programs/Python/Python313/python.exe C:/Tools/auto-commit-message/main.py' --replace-all
   ```

   *Catatan: Ini menggunakan path instalasi Python spesifik pengguna. Variabel lingkungan `%USERNAME%` akan diperluas ke nama pengguna saat ini. Sesuaikan path Python sesuai dengan instalasi Anda jika diperlukan*

   <details>
     <summary>Troubleshooting</summary>

     Jika Anda mengalami masalah dalam membuat alias Git, opsi `--replace-all` memastikan bahwa setiap alias yang ada dengan nama yang sama akan ditimpa. Jika masalah berlanjut, konsultasikan sumber daya eksternal berikut untuk bantuan lebih lanjut:

     - [How to Set Up Git Aliases](https://dev.to/jsdevspace/how-to-set-up-git-aliases-1hge)

     - [Git Basics - Git Aliases](https://git-scm.com/book/ms/v2/Git-Basics-Git-Aliases)
   </details>

## Usage

### Alur Kerja Standar

1. **Stage Perubahan Anda**

   ```sh
   git add .
   ```

   Atau stage perubahan secara selektif untuk pesan commit yang lebih tepat:

   ```sh
   git add <path/to/modified/files>
   ```

2. **Generate dan Eksekusi Commit**

   ```sh
   git acm
   ```

   Alat ini akan:
   - Menganalisis perubahan yang di-stage
   - Menghasilkan pesan commit terstruktur
   - Mengeksekusi operasi commit

### Opsi Lanjutan

- **Review Sebelum Commit**: Sistem akan menampilkan pesan commit yang dihasilkan dan meminta konfirmasi
- **Tipe Commit Kustom**: Alat ini mengenali semua tipe commit konvensional standar (lihat [Tipe Commit](#commit-types))

## Commit Types

Auto Commit Message mengikuti [spesifikasi Conventional Commits](https://www.conventionalcommits.org/), mendukung tipe commit berikut:

| Tipe | Deskripsi |
|------|------------|
| `build` | Perubahan yang mempengaruhi sistem build atau dependensi eksternal |
| `ci` | Perubahan pada file dan script konfigurasi CI |
| `chore` | Tugas pemeliharaan rutin dan perubahan kecil |
| `docs` | Perubahan hanya pada dokumentasi |
| `feat` | Pengenalan fitur baru |
| `fix` | Perbaikan bug |
| `perf` | Peningkatan performa |
| `refactor` | Perubahan kode yang tidak memperbaiki bug atau menambah fitur |
| `revert` | Membatalkan commit sebelumnya |
| `style` | Perubahan yang tidak mempengaruhi fungsionalitas kode (pemformatan, dll.) |
| `test` | Menambah atau memperbaiki test |
| `security` | Peningkatan atau perbaikan terkait keamanan |

## Configuration

### Konfigurasi Global

Sistem menggunakan file konfigurasi terpusat di `C:\Tools\auto-commit-message\.env.local` yang berisi parameter berikut:

- `GEMINI_API_KEY`: Kunci autentikasi API Google Gemini Anda

### Parameter Model

Pengguna tingkat lanjut dapat memodifikasi parameter berikut di `main.py`:

- `temperature`: Mengontrol kreativitas output (0.0 - 1.0)
- `top_p`: Mengontrol keragaman output (0.0 - 1.0)
- `top_k`: Membatasi pilihan token berikutnya
- `max_output_tokens`: Panjang maksimum output yang dihasilkan

## Architecture

Auto Commit Message dibangun dengan arsitektur modular yang terdiri dari komponen utama berikut:

- **GitCommitManager**: Menangani operasi Git dan manajemen repositori
- **AIModelManager**: Mengintegrasikan dengan API Google Gemini untuk generasi pesan
- **EnvironmentManager**: Mengelola konfigurasi dan variabel lingkungan
- **LoggerSetup**: Menyediakan logging terstruktur untuk debugging

## Contributing

Kontribusi sangat diterima! Jika Anda ingin berkontribusi:

1. Fork repositori
2. Buat branch fitur (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan Anda (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buka Pull Request

Pastikan untuk membaca [CONTRIBUTING.md](CONTRIBUTING.md) untuk detail lebih lanjut tentang proses kontribusi kami.

## License

Didistribusikan di bawah Lisensi MIT. Lihat [LICENSE](LICENSE) untuk informasi lebih lanjut.

## Support

Jika Anda menyukai proyek ini, pertimbangkan untuk:
- ⭐ Memberikan bintang di GitHub
- 🐛 Melaporkan bug yang Anda temukan
- 💡 Mengusulkan fitur baru
- 🔀 Membuat pull request untuk perbaikan atau peningkatan

---

<p align="center">Made with ❤️ by <a href="https://github.com/idugeni">idugeni</a></p>