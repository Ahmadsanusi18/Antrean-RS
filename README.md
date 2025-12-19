# 🏥 Sistem Antrian Puskesmas Digital (Flask)

Sistem Antrian Puskesmas Digital adalah aplikasi berbasis web menggunakan **Python (Flask)** untuk mengelola antrian pasien secara real-time, dilengkapi dengan **display layar antrian**, **suara pemanggilan otomatis**, serta **manajemen poli** oleh admin.


## ✨ Fitur Utama

### 👥 Pasien
- Ambil nomor antrian
- Pilih poli layanan
- Cetak struk antrian

### 🖥️ Display Antrian
- Menampilkan nomor yang sedang dipanggil
- Menampilkan antrian berikutnya
- Auto update data tanpa reload halaman
- Suara pemanggilan antrian (Text-to-Speech Bahasa Indonesia)
- Jam & tanggal real-time

### 👨‍💼 Admin
- Panggil antrian
- Panggil ulang (recall)
- Tandai antrian selesai
- Manajemen Poli:
  - Tambah poli
  - Edit nama poli (popup modal)
  - Hapus poli

---

## 🧱 Teknologi yang Digunakan

| Teknologi | Keterangan |
|---------|------------|
| Python | Bahasa pemrograman utama |
| Flask | Web framework |
| SQLite | Database |
| HTML | Template |
| Tailwind CSS | UI Styling |
| JavaScript | Interaksi & Fetch API |
| Web Speech API | Suara pemanggilan antrian |

## ⚙️ Instalasi & Menjalankan Aplikasi

### 1️⃣ Clone / Download Project
   
    git clone https://github.com/Ahmadsanusi18/Antrean-RS.git
    cd Antrean-RS
   
### 2️⃣ Aktifkan Virtual Environment
    
    python -m venv venv
    source venv/bin/activate   # Linux / Mac
    venv\Scripts\activate 
    
### 3️⃣ Install Dependency
   
    pip install flask
    
### 4️⃣ Jalankan Aplikasi
    
    python app.py
   
### 🔊 Fitur Suara Antrian

- Bahasa Indonesia (id-ID)
- Suara hanya diputar saat:
    Admin menekan tombol Panggil
    Nomor berubah (tidak berulang)
    Aman untuk Chrome & Edge

### 🧠 Catatan Pengembangan
- Nomor antrian reset harian
- Nomor bersifat global lintas poli
- Display tidak reload halaman (AJAX / Fetch)
- Footer & layout tetap stabil (tidak refresh)

### 👨‍💻 Developer

Dikembangkan oleh Ahmad Sanusi ig: @a.saan_
Project pembelajaran & implementasi sistem antrian digital berbasis Python Flask.
