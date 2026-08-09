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
    # Kita pastikan tabel Waifu tersedia menggunakan IF NOT EXISTS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Waifu (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nama VARCHAR(100) NOT NULL,
        umur INT,
        status VARCHAR(10),
        asal VARCHAR(20),
        Tb INT,
        Bb INT
    )
    ''')
    
    # (Opsional) Membuat tabel pengguna dan pesanan secara diam-diam agar materi 16-20 (JOIN) di bawah tetap berfungsi
    cursor.execute("DROP TABLE IF EXISTS pesanan")
    cursor.execute("DROP TABLE IF EXISTS pengguna")
    cursor.execute("CREATE TABLE pengguna (id INT AUTO_INCREMENT PRIMARY KEY, nama VARCHAR(100), umur INT, kota VARCHAR(100))")
    cursor.execute("CREATE TABLE pesanan (id_pesanan INT AUTO_INCREMENT PRIMARY KEY, pengguna_id INT, barang VARCHAR(100), jumlah INT)")
    
    print("✅ CREATE TABLE berhasil (Tabel 'Waifu' siap digunakan).")

    # ==========================================
    # 2. INSERT
    # ==========================================
    # Memasukkan data baru ke Waifu sebagai contoh agar bisa kita hapus/update nanti
    sql_waifu = "INSERT INTO Waifu (nama, umur, status, asal, Tb, Bb) VALUES (%s, %s, %s, %s, %s, %s)"
    new_waifus = [
        ('Miku', 16, 'Ilegal', 'Jepang', 158, 45)
    ]
    cursor.executemany(sql_waifu, new_waifus)
    
    # Insert data dummy ke tabel pengguna dan pesanan untuk materi 16-20
    cursor.executemany("INSERT INTO pengguna (nama, umur, kota) VALUES (%s, %s, %s)", [('Budi', 25, 'Jakarta'), ('Siti', 22, 'Bandung')])
    cursor.executemany("INSERT INTO pesanan (pengguna_id, barang, jumlah) VALUES (%s, %s, %s)", [(1, 'Laptop', 1)])
    
    conn.commit() # Menyimpan perubahan ke dalam database
    print("✅ INSERT berhasil (Data Waifu baru ditambahkan).\n")

    # ==========================================
    # 3. SELECT
    # ==========================================
    print("--- Hasil SELECT (Menampilkan Semua Data Waifu) ---")
    cursor.execute("SELECT * FROM Waifu")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 4. WHERE
    # ==========================================
    print("--- Hasil SELECT dengan WHERE (Hanya Waifu dengan status = 'Legal') ---")
    cursor.execute("SELECT * FROM Waifu WHERE status = 'Legal'")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 5. ORDER BY
    # ==========================================
    print("--- Hasil SELECT dengan ORDER BY (Mengurutkan Umur dari Termuda ke Tertua) ---")
    cursor.execute("SELECT * FROM Waifu ORDER BY umur ASC")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 6. LIMIT
    # ==========================================
    print("--- Hasil SELECT dengan LIMIT (Menampilkan 2 Data Teratas Saja) ---")
    cursor.execute("SELECT * FROM Waifu LIMIT 2")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 7. LIKE
    # ==========================================
    print("--- Hasil SELECT dengan LIKE (Menampilkan Nama yang Berawalan huruf 'H') ---")
    cursor.execute("SELECT * FROM Waifu WHERE nama LIKE 'H%'")
    for row in cursor.fetchall():
        print(row)
    print()

    print("--- Hasil SELECT dengan LIKE (Menampilkan Nama yang Berakhiran huruf 'a' -> %a) ---")
    cursor.execute("SELECT * FROM Waifu WHERE nama LIKE '%a'")
    for row in cursor.fetchall():
        print(row)
    print()

    print("--- Hasil SELECT dengan LIKE (Menampilkan Nama yang Mengandung huruf 'u' -> %u%) ---")
    cursor.execute("SELECT * FROM Waifu WHERE nama LIKE '%u%'")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 8. UPDATE
    # ==========================================
    print("--- Hasil UPDATE (Mengubah Umur Miku menjadi 17) ---")
    cursor.execute("UPDATE Waifu SET umur = 17 WHERE nama = 'Miku'")
    conn.commit()
    cursor.execute("SELECT * FROM Waifu WHERE nama = 'Miku'")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 9. DELETE
    # ==========================================
    print("--- Hasil DELETE (Menghapus Waifu bernama 'Miku') ---")
    cursor.execute("DELETE FROM Waifu WHERE nama = 'Miku'")
    conn.commit()
    cursor.execute("SELECT * FROM Waifu")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 10. DISTINCT
    # ==========================================
    print("--- Hasil SELECT DISTINCT (Menampilkan Asal secara unik/tanpa duplikat) ---")
    cursor.execute("SELECT DISTINCT asal FROM Waifu")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 11. ALIAS (AS)
    # ==========================================
    print("--- Hasil SELECT ALIAS (Mengganti nama kolom pada hasil Query) ---")
    cursor.execute("SELECT nama AS 'Nama Karakter', asal AS 'Daerah Asal' FROM Waifu")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 12. IN
    # ==========================================
    print("--- Hasil SELECT dengan IN (Mencari Waifu dari Liyue atau Inazuma) ---")
    cursor.execute("SELECT * FROM Waifu WHERE asal IN ('Liyue', 'Inazuma')")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 13. BETWEEN
    # ==========================================
    print("--- Hasil SELECT dengan BETWEEN (Mencari Waifu dengan Tinggi Badan 150 sampai 170) ---")
    cursor.execute("SELECT * FROM Waifu WHERE Tb BETWEEN 150 AND 170")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 14. IS NULL & IS NOT NULL
    # ==========================================
    print("--- Hasil SELECT dengan IS NOT NULL (Mencari Waifu yang asalnya tidak kosong) ---")
    cursor.execute("SELECT * FROM Waifu WHERE asal IS NOT NULL")
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 15. CASE
    # ==========================================
    print("--- Hasil SELECT dengan CASE (Mengkategorikan status legalitas berdasarkan umur) ---")
    cursor.execute('''
        SELECT nama, umur,
        CASE
            WHEN umur >= 18 THEN 'Sudah Legal'
            WHEN umur < 18 THEN 'Masih Ilegal'
            ELSE 'Tidak Diketahui'
        END AS KategoriUmur
        FROM Waifu
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

    # ==========================================
    # 18. UNION
    # ==========================================
    print("--- Hasil SELECT dengan UNION (Menggabungkan hasil dan menghilangkan duplikat) ---")
    # UNION: Menggabungkan hasil dari dua SELECT statement. Hasil yang duplikat akan dihilangkan.
    cursor.execute('''
        SELECT kota FROM pengguna WHERE umur > 25
        UNION
        SELECT kota FROM pengguna WHERE nama LIKE 'B%'
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 19. UNION ALL
    # ==========================================
    print("--- Hasil SELECT dengan UNION ALL (Menggabungkan hasil termasuk duplikat) ---")
    # UNION ALL: Sama seperti UNION, tetapi data yang duplikat tetap ditampilkan.
    cursor.execute('''
        SELECT kota FROM pengguna WHERE umur > 25
        UNION ALL
        SELECT kota FROM pengguna WHERE nama LIKE 'B%'
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 20. SELF JOIN
    # ==========================================
    print("--- Hasil SELECT dengan SELF JOIN ---")
    # SELF JOIN: Melakukan JOIN pada tabel yang sama. Berguna untuk membandingkan baris-baris dalam satu tabel.
    # Contoh: Menemukan pasangan pengguna yang tinggal di kota yang sama.
    cursor.execute('''
        SELECT A.nama AS Pengguna1, B.nama AS Pengguna2, A.kota
        FROM pengguna A, pengguna B
        WHERE A.id < B.id AND A.kota = B.kota
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 21. CROSS JOIN
    # ==========================================
    # Membuat tabel warna dan ukuran untuk contoh CROSS JOIN
    cursor.execute("DROP TABLE IF EXISTS warna")
    cursor.execute("DROP TABLE IF EXISTS ukuran")
    cursor.execute("CREATE TABLE warna (id INT AUTO_INCREMENT PRIMARY KEY, nama_warna VARCHAR(50))")
    cursor.execute("CREATE TABLE ukuran (id INT AUTO_INCREMENT PRIMARY KEY, nama_ukuran VARCHAR(50))")
    
    # Insert data ke tabel warna dan ukuran
    cursor.executemany("INSERT INTO warna (nama_warna) VALUES (%s)", [('Merah',), ('Biru',), ('Hitam',)])
    cursor.executemany("INSERT INTO ukuran (nama_ukuran) VALUES (%s)", [('S',), ('M',), ('L',)])
    conn.commit()

    print("--- Hasil SELECT dengan CROSS JOIN (Mengkombinasikan warna dan ukuran) ---")
    # CROSS JOIN: Menghasilkan Cartesian product, yaitu mengkombinasikan setiap baris dari tabel pertama dengan semua baris di tabel kedua.
    cursor.execute('''
        SELECT warna.nama_warna, ukuran.nama_ukuran
        FROM warna
        CROSS JOIN ukuran
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 22. GROUP BY & FUNGSI AGREGAT
    # ==========================================
    # Membuat tabel customer dan orders untuk contoh GROUP BY dan Agregat
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS customer")
    cursor.execute("CREATE TABLE customer (id INT AUTO_INCREMENT PRIMARY KEY, nama VARCHAR(100), negara VARCHAR(50))")
    cursor.execute("CREATE TABLE orders (id INT AUTO_INCREMENT PRIMARY KEY, customer_id INT, total_harga DECIMAL(10,2))")
    
    # Insert data ke tabel customer dan orders
    cursor.executemany("INSERT INTO customer (nama, negara) VALUES (%s, %s)", 
                       [('Andi', 'Indonesia'), ('Budi', 'Indonesia'), ('Charlie', 'Singapura'), ('David', 'Malaysia')])
    cursor.executemany("INSERT INTO orders (customer_id, total_harga) VALUES (%s, %s)", 
                       [(1, 50000), (1, 150000), (2, 200000), (3, 75000), (3, 125000), (3, 300000)])
    conn.commit()

    print("--- Hasil SELECT dengan GROUP BY dan FUNGSI AGREGAT ---")
    # FUNGSI AGREGAT: Menghitung nilai dari sekumpulan data (misal: SUM, COUNT, AVG, MAX, MIN).
    # GROUP BY: Mengelompokkan baris yang memiliki nilai yang sama ke dalam ringkasan baris.
    # Contoh: Menghitung total belanja dan jumlah pesanan per pelanggan.
    cursor.execute('''
        SELECT customer.nama, COUNT(orders.id) AS jumlah_pesanan, SUM(orders.total_harga) AS total_belanja
        FROM customer
        LEFT JOIN orders ON customer.id = orders.customer_id
        GROUP BY customer.id, customer.nama
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 23. HAVING
    # ==========================================
    print("--- Hasil SELECT dengan HAVING ---")
    # HAVING digunakan untuk memfilter hasil GROUP BY (karena WHERE tidak bisa menggunakan fungsi agregat)
    # Contoh: Menampilkan customer yang total belanjanya lebih dari 100.000
    cursor.execute('''
        SELECT customer.nama, SUM(orders.total_harga) AS total_belanja
        FROM customer
        JOIN orders ON customer.id = orders.customer_id
        GROUP BY customer.id, customer.nama
        HAVING total_belanja > 100000
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 24. SUBQUERY
    # ==========================================
    print("--- Hasil SELECT dengan SUBQUERY ---")
    # Subquery adalah query di dalam query.
    # Contoh: Menampilkan daftar order yang total harganya di atas rata-rata keseluruhan order
    cursor.execute('''
        SELECT customer.nama, orders.total_harga
        FROM customer
        JOIN orders ON customer.id = orders.customer_id
        WHERE orders.total_harga > (SELECT AVG(total_harga) FROM orders)
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 25. IN (Subquery)
    # ==========================================
    print("--- Hasil SELECT dengan IN (Subquery) ---")
    # Contoh: Menampilkan customer yang pernah melakukan order
    cursor.execute('''
        SELECT * FROM customer 
        WHERE id IN (SELECT customer_id FROM orders)
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 26. EXISTS
    # ==========================================
    print("--- Hasil SELECT dengan EXISTS ---")
    # EXISTS digunakan untuk memeriksa apakah sebuah subquery mengembalikan setidaknya satu baris.
    # Contoh: Menampilkan customer yang pernah melakukan order
    cursor.execute('''
        SELECT * FROM customer c
        WHERE EXISTS (
            SELECT 1 FROM orders o WHERE o.customer_id = c.id
        )
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 27. URUTAN EKSEKUSI SQL
    # ==========================================
    print("--- URUTAN EKSEKUSI SQL ---")
    print("""Urutan eksekusi SQL oleh sistem database:
FROM
↓
JOIN
↓
WHERE
↓
GROUP BY
↓
Agregasi (COUNT/SUM/...)
↓
HAVING
↓
SELECT
↓
ORDER BY
↓
LIMIT""")
    print()

except pymysql.Error as e:
    print(f"Terjadi error pada MariaDB: {e}")

finally:
    # Menutup koneksi database sangat penting agar memori tidak bocor
    if 'conn' in locals() and conn.open:
        cursor.close()
        conn.close()
