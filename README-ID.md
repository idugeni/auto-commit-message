# 🚀 Auto Commit Message

![Auto Commit Message Logo](https://opengraph.githubassets.com/856c5388bec324b86d5fb9acf0cc386418284ea1/idugeni/auto-commit-message)

Auto Commit Message adalah skrip otomatis yang membantu menghasilkan pesan commit Git yang terstruktur dengan AI (Google Gemini) berdasarkan perubahan dalam repository.

[![🔥 Git Commit Like a Pro! Use Gemini AI to Automate Perfect Messages! 🚀](https://img.youtube.com/vi/lbaSAhxPpWY/maxresdefault.jpg)](https://www.youtube.com/watch?v=lbaSAhxPpWY)

## 📂 Struktur Proyek

```sh
📦 auto-commit-message
├── main.py             # Skrip utama untuk menghasilkan pesan commit
├── requirements.txt    # Dependensi Python yang dibutuhkan
├── .gitignore          # Mengabaikan file yang tidak perlu
├── .env.local          # Menyimpan API key (akan dibuat otomatis jika belum ada)
├── README-ID.md        # Dokumentasi proyek ini (Indonesia)
├── README.md           # Dokumentasi proyek ini
├── LICENSE             # Lisensi proyek ini
├── CODE_OF_CONDUCT.md  # Panduan kode etik kontribusi
└── SECURITY.md         # Panduan keamanan dan pelaporan masalah
```

## 📜 Fitur Utama

✅ **Deteksi Perubahan Git**: Mengambil perubahan yang telah di-*stage* dalam repository.  
✅ **Generasi Commit Message AI**: Menggunakan Google Gemini AI untuk membuat pesan commit yang jelas dan sesuai standar konvensional.  
✅ **Validasi Repository**: Memastikan bahwa folder yang digunakan adalah repository Git yang valid.  
✅ **Pengaturan Global .env**: Menggunakan `.env.local` dari lokasi global `C:\Tools\auto-commit-message`.  
✅ **Shortcut Git Command**: Dapat digunakan dengan perintah `git acm`.  

## 📦 Instalasi

1️⃣ **Clone Repository dan Jalankan Setup**

   ```sh
   git clone https://github.com/idugeni/auto-commit-message.git
   ```

   ```sh
   cd auto-commit-message
   ```

Jalankan Skrip Pengaturan

   ```sh
   run.bat
   ```

   Perintah di atas akan menyalin semua file ke folder global `C:\Tools\auto-commit-message/`.

2️⃣ **Install Dependensi di Folder Global**

   ```sh
   pip install -r C:/Tools/auto-commit-message/requirements.txt
   ```

3️⃣ **Set API Key Google Gemini**

- Buat file `.env.local` di `C:\Tools\auto-commit-message` (jika belum ada).
- Tambahkan baris berikut ke dalam file tersebut:

     ```sh
     GEMINI_API_KEY=your_api_key_here
     ```

- Ganti `your_api_key_here` dengan API key dari Google Gemini.

4️⃣ **Buat Alias Git** (agar bisa menggunakan `git acm`)

   ```sh
   git config --global alias.acm '!C:/Users/%USERNAME%/AppData/Local/Programs/Python/Python313/python.exe C:/Tools/auto-commit-message/main.py'
   ```

   Perintah ini akan otomatis menggunakan Python dari direktori pengguna.

## 🚀 Cara Menggunakan

1️⃣ **Pastikan perubahan sudah di-*stage***

   ```sh
   git add .
   ```

   atau

   ```sh
   git add <file_yang_diubah>
   ```

   agar hasil lebih maksimal terhadap perubahan masing-masing file

2️⃣ **Jalankan perintah berikut untuk commit otomatis**

   ```sh
   git acm
   ```

   Skrip akan otomatis menghasilkan pesan commit dan melakukan commit 🎉

## 📌 Jenis Commit Message yang Didukung

Skrip ini menghasilkan pesan commit sesuai standar **Conventional Commits**:

- `build`: Perubahan yang memengaruhi sistem build atau dependensi eksternal.
- `ci`: Perubahan terkait dengan konfigurasi CI/CD.
- `chore`: Perubahan kecil yang tidak mempengaruhi kode sumber atau tes.
- `docs`: Perubahan yang hanya berkaitan dengan dokumentasi.
- `feat`: Penambahan fitur baru.
- `fix`: Perbaikan bug.
- `perf`: Peningkatan performa.
- `refactor`: Perubahan kode tanpa mengubah fungsionalitas.
- `revert`: Membatalkan perubahan sebelumnya.
- `style`: Perubahan yang tidak mempengaruhi kode (misalnya format atau whitespace).
- `test`: Penambahan atau perbaikan pengujian.
- `security`: Perbaikan atau peningkatan terkait keamanan.

## 📜 Lisensi

Proyek ini menggunakan lisensi **MIT**. Silakan gunakan dan modifikasi sesuai kebutuhan! 🚀💖

---

Dibuat dengan ❤️ untuk kemudahan kerja Git kamu! ✨ Jika ada masukan atau fitur yang ingin ditambahkan, jangan ragu untuk menghubungi saya! 😊
