import sqlite3

# MATERI SQLITE3 (Berdasarkan syntax yang sama dengan MariaDB/MySQL)
# Modul sqlite3 adalah bawaan Python untuk database SQL ringan.

# Membuat koneksi ke database. Jika file tidak ada, otomatis akan dibuat.
conn = sqlite3.connect('belajar.db')

# Membuat cursor untuk mengeksekusi perintah SQL
cursor = conn.cursor()

# ==========================================
# 1. CREATE TABLE
# Membuat tabel baru bernama 'pengguna'
# ==========================================
cursor.execute('''
CREATE TABLE IF NOT EXISTS pengguna (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    umur INTEGER,
    kota TEXT
)
''')
print("✅ CREATE TABLE berhasil (Tabel 'pengguna' siap digunakan).")

# ==========================================
# 2. INSERT
# Menambahkan data ke dalam tabel
# ==========================================
# Kita bersihkan data lama dulu agar tidak dobel saat file dijalankan ulang
cursor.execute("DELETE FROM pengguna") 

# Data yang akan dimasukkan
users = [
    ('Budi', 25, 'Jakarta'),
    ('Siti', 22, 'Bandung'),
    ('Andi', 30, 'Surabaya'),
    ('Ayu', 28, 'Jakarta'),
    ('Bima', 20, 'Bali')
]
cursor.executemany("INSERT INTO pengguna (nama, umur, kota) VALUES (?, ?, ?)", users)
conn.commit() # Menyimpan perubahan ke database
print("✅ INSERT berhasil (5 data ditambahkan).\n")


# ==========================================
# 3. SELECT
# Mengambil/menampilkan semua data dari tabel
# ==========================================
print("--- Hasil SELECT (Semua Data) ---")
cursor.execute("SELECT * FROM pengguna")
for row in cursor.fetchall():
    print(row)
print()


# ==========================================
# 4. WHERE
# Menampilkan data dengan kondisi tertentu (contoh: kota = 'Jakarta')
# ==========================================
print("--- Hasil SELECT dengan WHERE (Hanya Kota Jakarta) ---")
cursor.execute("SELECT * FROM pengguna WHERE kota = 'Jakarta'")
for row in cursor.fetchall():
    print(row)
print()


# ==========================================
# 5. ORDER BY
# Mengurutkan data (contoh: berdasarkan umur dari termuda ke tertua / ASC)
# ==========================================
print("--- Hasil SELECT dengan ORDER BY (Umur Termuda ke Tertua) ---")
cursor.execute("SELECT * FROM pengguna ORDER BY umur ASC")
for row in cursor.fetchall():
    print(row)
print()


# ==========================================
# 6. LIMIT
# Membatasi jumlah data yang ditampilkan (contoh: Tampilkan 2 baris saja)
# ==========================================
print("--- Hasil SELECT dengan LIMIT (Hanya 2 data pertama) ---")
cursor.execute("SELECT * FROM pengguna LIMIT 2")
for row in cursor.fetchall():
    print(row)
print()


# ==========================================
# 7. LIKE
# Mencari data dengan pola (pattern). Contoh: nama berawalan huruf 'A'
# ==========================================
print("--- Hasil SELECT dengan LIKE (Nama berawalan huruf 'A') ---")
cursor.execute("SELECT * FROM pengguna WHERE nama LIKE 'A%'")
for row in cursor.fetchall():
    print(row)
print()

# Menutup koneksi database (Penting dilakukan di akhir)
conn.close()
