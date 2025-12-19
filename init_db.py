# ========================================
# Author    : Ahmad Sanusi
# Instagram : @a.saan_
# ========================================

import sqlite3

# Koneksi database
conn = sqlite3.connect('database.db')
cur = conn.cursor()

# ===================== TABEL POLI / LAYANAN =====================
cur.execute("""
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL UNIQUE
)
""")

# ===================== TABEL ANTRIAN =====================
cur.execute("""
CREATE TABLE IF NOT EXISTS queues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nomor INTEGER,
    service_id INTEGER,
    status TEXT,
    waktu_ambil TEXT,
    waktu_panggil TEXT,
    waktu_selesai TEXT,
    FOREIGN KEY (service_id) REFERENCES services(id)
)
""")

# ===================== DATA POLI AWAL =====================
# Daftar poli awal (bisa ditambah tanpa menghapus database lama)
new_polis = [
    "Poli Umum",
    "Poli Gigi",
    "Poli Anak",
    "Poli Kandungan",
    "Poli Mata",
    "Poli Dalam",
    "Poli Kulit",
    "Poli THT",
    "Poli Bedah",
    "Poli Saraf",
    "Poli Jantung",
    "Poli Orthopedi",
    "Poli Urologi",
    "Poli Rehabilitasi",
    "Poli Psikiatri",
    "Poli Gizi"
  # poli baru
]

for poli in new_polis:
    # Cek apakah poli sudah ada
    cur.execute("SELECT COUNT(*) FROM services WHERE nama=?", (poli,))
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO services (nama) VALUES (?)", (poli,))

conn.commit()
conn.close()

print("Database berhasil dibuat atau diperbarui, poli baru ditambahkan jika ada.")
