import pymysql

# ==========================================
# MATERI MARIADB MENGGUNAKAN PYTHON
# (Membutuhkan modul pymysql: pip install pymysql)
# ==========================================

# 1. Koneksi ke Database MariaDB
# Menggunakan database 'BelajarMariaDb' yang telah Anda buat sebelumnya.
try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",      # Default password root di Termux adalah kosong
        database="BelajarMariaDb"
    )
    cursor = conn.cursor()
    print("✅ Berhasil terkoneksi ke MariaDB!\n")

    # ==========================================
    # 1. CREATE TABLE
    # ==========================================
    # Menghapus tabel terlebih dahulu (jika ada) agar bisa di-run berulang kali tanpa error
    cursor.execute("DROP TABLE IF EXISTS pengguna")
    
    # Membuat tabel baru
    cursor.execute('''
    CREATE TABLE pengguna (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nama VARCHAR(100) NOT NULL,
        umur INT,
        kota VARCHAR(100)
    )
    ''')
    print("✅ CREATE TABLE berhasil (Tabel 'pengguna' siap digunakan).")

    # ==========================================
    # 2. INSERT
    # ==========================================
    # Memasukkan banyak data sekaligus ke tabel
    sql = "INSERT INTO pengguna (nama, umur, kota) VALUES (%s, %s, %s)"
    users = [
        ('Budi', 25, 'Jakarta'),
        ('Siti', 22, 'Bandung'),
        ('Andi', 30, 'Surabaya'),
        ('Ayu', 28, 'Jakarta'),
        ('Bima', 20, 'Bali')
    ]
    cursor.executemany(sql, users)
    conn.commit() # Menyimpan perubahan ke dalam database
    print(f"✅ INSERT berhasil ({cursor.rowcount} baris data ditambahkan).\n")

    # ==========================================
    # 3. SELECT
    # ==========================================
    print("--- Hasil SELECT (Menampilkan Semua Data) ---")
    cursor.execute("SELECT * FROM pengguna")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 4. WHERE
    # ==========================================
    print("--- Hasil SELECT dengan WHERE (Hanya Data dengan Kota = 'Jakarta') ---")
    cursor.execute("SELECT * FROM pengguna WHERE kota = 'Jakarta'")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 5. ORDER BY
    # ==========================================
    print("--- Hasil SELECT dengan ORDER BY (Mengurutkan Umur dari Termuda ke Tertua) ---")
    cursor.execute("SELECT * FROM pengguna ORDER BY umur ASC")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 6. LIMIT
    # ==========================================
    print("--- Hasil SELECT dengan LIMIT (Menampilkan 2 Data Teratas Saja) ---")
    cursor.execute("SELECT * FROM pengguna LIMIT 2")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 7. LIKE
    # ==========================================
    print("--- Hasil SELECT dengan LIKE (Menampilkan Nama yang Berawalan huruf 'A') ---")
    cursor.execute("SELECT * FROM pengguna WHERE nama LIKE 'A%'")
    for row in cursor.fetchall():
        print(row)
    print()

except pymysql.Error as e:
    print(f"Terjadi error pada MariaDB: {e}")

finally:
    # Menutup koneksi database sangat penting agar memori tidak bocor
    if 'conn' in locals() and conn.open:
        cursor.close()
        conn.close()
