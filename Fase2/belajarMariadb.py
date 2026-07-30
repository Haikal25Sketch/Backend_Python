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
    cursor.execute("DROP TABLE IF EXISTS pesanan")
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
    cursor.execute('''
    CREATE TABLE pesanan (
        id_pesanan INT AUTO_INCREMENT PRIMARY KEY,
        pengguna_id INT,
        barang VARCHAR(100),
        jumlah INT
    )
    ''')
    print("✅ CREATE TABLE berhasil (Tabel 'pengguna' dan 'pesanan' siap digunakan).")

    # ==========================================
    # 2. INSERT
    # ==========================================
    # Memasukkan banyak data sekaligus ke tabel
    sql_pengguna = "INSERT INTO pengguna (nama, umur, kota) VALUES (%s, %s, %s)"
    users = [
        ('Budi', 25, 'Jakarta'),
        ('Siti', 22, 'Bandung'),
        ('Andi', 30, 'Surabaya'),
        ('Ayu', 28, 'Jakarta'),
        ('Bima', 20, 'Bali'),
        ('Coki', 24, 'Medan')
    ]
    cursor.executemany(sql_pengguna, users)
    
    sql_pesanan = "INSERT INTO pesanan (pengguna_id, barang, jumlah) VALUES (%s, %s, %s)"
    orders = [
        (1, 'Laptop', 1),
        (1, 'Mouse', 2),
        (2, 'Keyboard', 1),
        (3, 'Monitor', 1),
        (10, 'Flashdisk', 3)
    ]
    cursor.executemany(sql_pesanan, orders)
    
    conn.commit() # Menyimpan perubahan ke dalam database
    print("✅ INSERT berhasil (Data pengguna dan pesanan ditambahkan).\n")

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

    print("--- Hasil SELECT dengan LIKE (Menampilkan Nama yang Berakhiran huruf 'a' -> %a) ---")
    cursor.execute("SELECT * FROM pengguna WHERE nama LIKE '%a'")
    for row in cursor.fetchall():
        print(row)
    print()

    print("--- Hasil SELECT dengan LIKE (Menampilkan Nama yang Mengandung huruf 'a' -> %a%) ---")
    cursor.execute("SELECT * FROM pengguna WHERE nama LIKE '%a%'")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 8. UPDATE
    # ==========================================
    print("--- Hasil UPDATE (Mengubah Kota Budi menjadi 'Tangerang') ---")
    cursor.execute("UPDATE pengguna SET kota = 'Tangerang' WHERE nama = 'Budi'")
    conn.commit()
    cursor.execute("SELECT * FROM pengguna WHERE nama = 'Budi'")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 9. DELETE
    # ==========================================
    print("--- Hasil DELETE (Menghapus pengguna bernama 'Bima') ---")
    cursor.execute("DELETE FROM pengguna WHERE nama = 'Bima'")
    conn.commit()
    cursor.execute("SELECT * FROM pengguna")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 10. DISTINCT
    # ==========================================
    print("--- Hasil SELECT DISTINCT (Menampilkan Kota secara unik/tanpa duplikat) ---")
    cursor.execute("SELECT DISTINCT kota FROM pengguna")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 11. ALIAS (AS)
    # ==========================================
    print("--- Hasil SELECT ALIAS (Mengganti nama kolom pada hasil Query) ---")
    cursor.execute("SELECT nama AS 'Nama Lengkap', kota AS 'Domisili' FROM pengguna")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 12. IN
    # ==========================================
    print("--- Hasil SELECT dengan IN (Mencari pengguna di Jakarta atau Bandung) ---")
    cursor.execute("SELECT * FROM pengguna WHERE kota IN ('Jakarta', 'Bandung')")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 13. BETWEEN
    # ==========================================
    print("--- Hasil SELECT dengan BETWEEN (Mencari pengguna dengan umur 20 sampai 25) ---")
    cursor.execute("SELECT * FROM pengguna WHERE umur BETWEEN 20 AND 25")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 14. IS NULL & IS NOT NULL
    # ==========================================
    print("--- Hasil SELECT dengan IS NOT NULL (Mencari pengguna yang kotanya tidak kosong) ---")
    # Catatan: Untuk IS NULL, Anda perlu data yang bernilai NULL agar hasil kueri tidak kosong.
    cursor.execute("SELECT * FROM pengguna WHERE kota IS NOT NULL")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 15. CASE
    # ==========================================
    print("--- Hasil SELECT dengan CASE (Mengkategorikan umur pengguna) ---")
    cursor.execute('''
        SELECT nama, umur,
        CASE
            WHEN umur < 25 THEN 'Muda'
            WHEN umur BETWEEN 25 AND 30 THEN 'Dewasa'
            ELSE 'Lainnya'
        END AS KategoriUmur
        FROM pengguna
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 16. LEFT JOIN
    # ==========================================
    print("--- Hasil SELECT dengan LEFT JOIN (Menampilkan semua pengguna dan pesanannya, jika ada) ---")
    # LEFT JOIN: Mengambil semua baris dari tabel kiri (pengguna), dan baris yang cocok dari tabel kanan (pesanan).
    # Jika tidak ada pesanan, nilai kolom pesanan akan menjadi NULL.
    cursor.execute('''
        SELECT pengguna.nama, pesanan.barang, pesanan.jumlah
        FROM pengguna
        LEFT JOIN pesanan ON pengguna.id = pesanan.pengguna_id
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 17. RIGHT JOIN
    # ==========================================
    print("--- Hasil SELECT dengan RIGHT JOIN (Menampilkan semua pesanan dan nama penggunanya, jika ada) ---")
    # RIGHT JOIN: Mengambil semua baris dari tabel kanan (pesanan), dan baris yang cocok dari tabel kiri (pengguna).
    # Jika id pengguna di pesanan tidak ditemukan di tabel pengguna, nilainya akan menjadi NULL.
    cursor.execute('''
        SELECT pengguna.nama, pesanan.barang, pesanan.jumlah
        FROM pengguna
        RIGHT JOIN pesanan ON pengguna.id = pesanan.pengguna_id
    ''')
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
