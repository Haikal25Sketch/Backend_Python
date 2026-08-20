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
    cursor.execute('''CREATE TABLE customer (id INT AUTO_INCREMENT PRIMARY KEY, nama VARCHAR(100),umur INT ,kota VARCHAR(50))''')
    cursor.execute('''CREATE TABLE orders (id INT AUTO_INCREMENT PRIMARY KEY, customer_id INT, total_harga DECIMAL(10,2))''')
    
    # Insert data ke tabel customer dan orders
    cursor.executemany("INSERT INTO customer (nama, umur,kota) VALUES (%s, %s,%s)", 
                       [('HuTao',15, 'Liyue'), ('Yaemiko',43, 'Inazuma'), ('Chitlali',25, 'Natlan'), ('Sagiri',12, 'Jepang'), ('Furina',17,'Fontaine'), ('Rara',17,'Indonesia')])
    cursor.executemany("INSERT INTO orders (customer_id, total_harga) VALUES (%s, %s)",     [(1, 10000), (2, 15000), (2, 13400), (4, 17600), (3, 100000), (3, 15000), (6,12500), (2,17800), (2,17800) ])
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
    # 27. ANY
    # ==========================================
    print("--- Hasil SELECT dengan ANY ---")
    # ANY membandingkan nilai dengan salah satu nilai yang dihasilkan oleh subquery.
    # Mengembalikan TRUE jika ada setidaknya satu perbandingan yang benar.
    # Contoh: Menampilkan Waifu yang umurnya lebih besar dari *salah satu* Waifu asal Jepang
    cursor.execute('''
        SELECT nama, umur, asal 
        FROM Waifu 
        WHERE umur > ANY (SELECT umur FROM Waifu WHERE asal = 'Jepang')
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 28. ALL
    # ==========================================
    print("--- Hasil SELECT dengan ALL ---")
    # ALL membandingkan nilai dengan semua nilai yang dihasilkan oleh subquery.
    # Mengembalikan TRUE hanya jika semua perbandingan benar.
    # Contoh: Menampilkan Waifu yang tinggi badannya (Tb) lebih besar dari *semua* Waifu asal Liyue
    cursor.execute('''
        SELECT nama, Tb, asal 
        FROM Waifu 
        WHERE Tb > ALL (SELECT Tb FROM Waifu WHERE asal = 'Liyue')
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 29. URUTAN EKSEKUSI SQL
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

    # ==========================================
    # 30. DERIVED TABLE
    # ==========================================
    # Derived Table (tabel turunan) adalah tabel sementara yang dihasilkan oleh subquery
    # di dalam klausa FROM. Kita memperlakukan hasil subquery tersebut seolah-olah itu
    # adalah tabel fisik sungguhan. Syarat wajibnya, setiap derived table harus diberi ALIAS.
    
    print("--- Hasil SELECT dengan DERIVED TABLE (Contoh 1) ---")
    cursor.execute("SELECT * FROM(SELECT C.nama AS Nama,SUM(O.total_harga) AS Total_Belanja FROM customer AS C JOIN orders AS O ON O.customer_id = C.id GROUP BY C.nama,C.id) AS X;")
    for row in cursor.fetchall():
        print(row)
    print()

    print("--- Hasil SELECT dengan DERIVED TABLE (Contoh 2) ---")
    cursor.execute("SELECT * FROM(SELECT C.nama AS Nama,SUM(O.total_harga) AS Total_Belanja FROM customer AS C JOIN orders AS O ON O.customer_id = C.id GROUP BY C.nama,C.id) AS X WHERE X.Total_Belanja >(SELECT AVG(Rata_rata.Total_Belanja) FROM(SELECT SUM(total_harga) AS Total_Belanja FROM orders GROUP BY customer_id) AS Rata_rata);")
    for row in cursor.fetchall():
        print(row)
    print()

    print("--- Hasil SELECT dengan DERIVED TABLE (Contoh 3) ---")
    # Contoh 3: Menampilkan nama pelanggan dan jumlah pesanannya, tetapi hanya untuk
    # pelanggan yang jumlah pesanannya lebih dari 1. Kita jadikan hasil perhitungan
    # COUNT() sebagai Derived Table dengan alias 'T'.
    cursor.execute('''
        SELECT T.nama, T.jumlah_order 
        FROM (
            SELECT c.nama, COUNT(o.id) as jumlah_order 
            FROM customer c 
            JOIN orders o ON c.id = o.customer_id 
            GROUP BY c.id, c.nama
        ) AS T 
        WHERE T.jumlah_order > 1
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    print("--- Hasil SELECT dengan DERIVED TABLE di dalam JOIN (Contoh 4) ---")
    # Contoh 4: Menggunakan Derived Table secara langsung di dalam klausa JOIN.
    # Kita menggabungkan tabel customer utama dengan sebuah Derived Table (alias 'TotalOrder')
    # yang menghitung jumlah total belanja per customer dari tabel orders.
    cursor.execute('''
        SELECT c.nama, c.kota, TotalOrder.total_belanja
        FROM customer c
        JOIN (
            SELECT customer_id, SUM(total_harga) AS total_belanja
            FROM orders
            GROUP BY customer_id
        ) AS TotalOrder ON c.id = TotalOrder.customer_id
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 31. CTE (Common Table Expression)
    # ==========================================
    # CTE (Common Table Expression) pada dasarnya mirip dengan Derived Table, tetapi
    # didefinisikan menggunakan klausa WITH di awal statement query. 
    # CTE lebih mudah dibaca, rapi, dan bisa dipanggil berkali-kali di dalam query yang sama.
    
    print("--- Hasil SELECT dengan CTE (Contoh 1) ---")
    # Contoh 1: Sesuai referensi, menggunakan CTE untuk mencari customer yang total
    # belanjanya di atas rata-rata semua customer.
    cursor.execute('''
        WITH Total_customer AS(SELECT C.id AS Id,C.nama AS Nama_Customer,SUM(O.total_harga) AS Total_Belanja FROM customer AS C JOIN orders AS O ON O.customer_id = C.id GROUP BY C.id,C.nama) SELECT * FROM Total_customer WHERE Total_Belanja > (SELECT AVG(Total_Belanja) FROM Total_customer);
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    print("--- Hasil SELECT dengan CTE (Contoh 2) ---")
    # Contoh 2: Menggunakan CTE untuk mencari rata-rata frekuensi/jumlah transaksi dari seluruh pelanggan.
    # (Bukan dari sisi nominal, melainkan jumlah aktivitas order-nya).
    cursor.execute('''
        WITH Transaksi_Per_Customer AS (
            SELECT customer_id, COUNT(id) AS jumlah_transaksi
            FROM orders
            GROUP BY customer_id
        )
        SELECT AVG(jumlah_transaksi) AS Rata_rata_transaksi
        FROM Transaksi_Per_Customer;
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 32. WINDOW FUNCTION
    # ==========================================
    # Window Function melakukan kalkulasi pada sekumpulan baris (disebut "window")
    # yang memiliki keterkaitan dengan baris saat ini. Berbeda dengan GROUP BY yang
    # menggabungkan baris ke dalam satu ringkasan, Window Function tetap
    # mempertahankan baris aslinya dan hanya menambahkan kolom hasil kalkulasi.
    
    print("--- Hasil WINDOW FUNCTION: OVER() ---")
    # OVER(): Berfungsi untuk mendefinisikan "window". Jika argumen OVER() dibiarkan
    # kosong, maka window akan mencakup semua baris yang dikembalikan oleh query.
    cursor.execute('''
        SELECT id, customer_id, total_harga,
               SUM(total_harga) OVER() AS total_keseluruhan
        FROM orders;
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    print("--- Hasil WINDOW FUNCTION: PARTITION BY ---")
    # PARTITION BY: Membagi window (seluruh data) menjadi kelompok-kelompok yang lebih
    # kecil berdasarkan nilai pada kolom tertentu. Kalkulasi (seperti SUM) akan
    # berjalan secara independen untuk tiap partisi.
    cursor.execute('''
        SELECT id, customer_id, total_harga,
               SUM(total_harga) OVER(PARTITION BY customer_id) AS total_per_customer
        FROM orders;
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    print("--- Hasil WINDOW FUNCTION: ROW_NUMBER() ---")
    # ROW_NUMBER(): Memberikan urutan/nomor baris secara sekuensial pada tiap baris di 
    # dalam partisi (atau semua data jika tidak ada partisi), tanpa memedulikan apakah nilainya kembar atau tidak.
    cursor.execute('''
        SELECT id, customer_id, total_harga,
               ROW_NUMBER() OVER(ORDER BY total_harga DESC) AS urutan
        FROM orders;
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    print("--- Hasil WINDOW FUNCTION: RANK() ---")
    # RANK(): Memberikan peringkat. Jika ada nilai yang sama, mereka akan mendapat
    # peringkat yang sama. Namun, urutan (peringkat) berikutnya akan dilompati
    # sesuai jumlah data yang kembar (contoh: 1, 2, 2, 4).
    

    cursor.execute('''
        SELECT id, customer_id, total_harga,
               RANK() OVER(ORDER BY total_harga DESC) AS peringkat
        FROM orders;
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    print("--- Hasil WINDOW FUNCTION: DENSE_RANK() ---")
    # DENSE_RANK(): Sama dengan RANK (memberi peringkat sama pada nilai kembar),
    # akan tetapi urutan/peringkat berikutnya TIDAK DILOMPATI (contoh: 1, 2, 2, 3).
    cursor.execute('''
        SELECT id, customer_id, total_harga,
               DENSE_RANK() OVER(ORDER BY total_harga DESC) AS peringkat_padat
        FROM orders;
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    print("--- GABUNGAN: ROW_NUMBER vs RANK vs DENSE_RANK ---")
    # Tabel komparasi untuk melihat jelas perbedaan perhitungan ketiganya
    # secara bersamaan saat dihadapkan pada nilai (total_harga) yang kembar.
    cursor.execute('''
        SELECT id, customer_id, total_harga,
               ROW_NUMBER() OVER(ORDER BY total_harga DESC) AS row_num,
               RANK() OVER(ORDER BY total_harga DESC) AS rnk,
               DENSE_RANK() OVER(ORDER BY total_harga DESC) AS dense_rnk
        FROM orders;
    ''')
    for row in cursor.fetchall():
        print(row)
    print()

    # ==========================================
    # 33. VIEW
    # ==========================================
    print("--- Hasil SELECT dari VIEW ---")
    # Sesuai permintaan, kita tidak akan mengutak-atik (CREATE/ALTER/DROP) VIEW yang sudah ada.
    # Silakan ubah variabel 'nama_view_anda' di bawah sesuai dengan nama VIEW yang ada di database MariaDB Anda.
    nama_view = "total_customer" # <-- GANTI DENGAN NAMA VIEW MILIK ANDA
    try:
        cursor.execute(f"SELECT * FROM {nama_view}")
        for row in cursor.fetchall():
            print(row)
    except pymysql.Error as err:
        print(f"Catatan: Gagal memanggil view '{nama_view}'. Ganti dengan nama view Anda yang benar. Error: {err}")
    print()

    # ==========================================
    # 34. INDEX
    # ==========================================
    print("--- Membuat dan Menggunakan INDEX ---")
    # INDEX berfungsi untuk mempercepat proses pencarian data (query SELECT).
    # Contoh: Kita akan membuat index pada kolom 'nama' di tabel 'customer'.
    try:
        cursor.execute("DROP INDEX idx_customer_nama ON customer") # Dihapus dulu agar tidak error jika dijalankan ulang
    except:
        pass

    cursor.execute("CREATE INDEX idx_customer_nama ON customer(nama)")
    print("✅ Berhasil membuat INDEX 'idx_customer_nama' pada kolom 'nama' di tabel 'customer'.")
    print()

    # ==========================================
    # 35. EXPLAIN
    # ==========================================
    print("--- Hasil EXPLAIN (Menganalisa Query) ---")
    # EXPLAIN digunakan untuk melihat cara MariaDB mengeksekusi suatu query (Execution Plan).
    # Sangat berguna untuk mengecek apakah query kita sudah optimal dan menggunakan INDEX.
    cursor.execute("EXPLAIN SELECT * FROM customer WHERE nama = 'HuTao'")
    
    # Menampilkan nama-nama kolom dari hasil EXPLAIN agar lebih mudah dibaca
    kolom_explain = [desc[0] for desc in cursor.description]
    print(" | ".join(kolom_explain))
    
    for row in cursor.fetchall():
        print(" | ".join(str(val) for val in row))
    print()

    # ==========================================
    # 36. SHOW CREATE TABLE
    # ==========================================
    print("--- Hasil SHOW CREATE TABLE ---")
    # Digunakan untuk melihat perintah SQL persis (DDL) yang digunakan saat membuat tabel.
    cursor.execute("SHOW CREATE TABLE Waifu")
    for row in cursor.fetchall():
        print(f"Tabel: {row[0]}")
        print(f"Query Create:\n{row[1]}")
    print()

    # ==========================================
    # 37. SHOW CREATE VIEW & DROP VIEW
    # ==========================================
    print("--- Membuat View Dummy sementara untuk materi SHOW CREATE VIEW & DROP VIEW ---")
    # Kita membuat view baru HANYA SEBAGAI CONTOH agar tidak mengganggu view Anda yang sudah ada.
    cursor.execute("CREATE OR REPLACE VIEW view_contoh_dummy AS SELECT nama, umur FROM Waifu")
    print("✅ Berhasil membuat view 'view_contoh_dummy'.")
    print()

    print("--- Hasil SHOW CREATE VIEW ---")
    # Digunakan untuk melihat perintah SQL yang membentuk sebuah view.
    cursor.execute("SHOW CREATE VIEW view_contoh_dummy")
    for row in cursor.fetchall():
        print(f"View: {row[0]}")
        print(f"Query Create:\n{row[1]}")
    print()

    print("--- Hasil DROP VIEW ---")
    # Digunakan untuk menghapus sebuah view dari database.
    cursor.execute("DROP VIEW IF EXISTS view_contoh_dummy")
    print("✅ Berhasil menghapus view 'view_contoh_dummy'.")
    print()

    # ==========================================
    # 38. TRANSAKSI (TRANSACTION)
    # ==========================================
    print("--- 38. TRANSAKSI ---")
    # Membuat tabel dummy khusus untuk contoh transaksi agar tidak mengubah database asli Anda
    cursor.execute("DROP TABLE IF EXISTS akun_bank")
    cursor.execute("CREATE TABLE akun_bank (id INT AUTO_INCREMENT PRIMARY KEY, nama VARCHAR(50), saldo DECIMAL(10,2))")
    # Insert data awal
    cursor.executemany("INSERT INTO akun_bank (nama, saldo) VALUES (%s, %s)", [('Andi', 5000), ('Budi', 3000)])
    conn.commit() # Simpan data awal

    print("Data awal akun_bank:")
    cursor.execute("SELECT * FROM akun_bank")
    for row in cursor.fetchall(): print(row)
    print()

    # BEGIN / START TRANSACTION dan COMMIT
    print("--- BEGIN / START TRANSACTION & COMMIT ---")
    cursor.execute("START TRANSACTION") # atau bisa menggunakan conn.begin()
    cursor.execute("UPDATE akun_bank SET saldo = saldo - 1000 WHERE nama = 'Andi'")
    cursor.execute("UPDATE akun_bank SET saldo = saldo + 1000 WHERE nama = 'Budi'")
    conn.commit() # Menyimpan perubahan secara permanen
    print("✅ Transaksi transfer Andi ke Budi berhasil di-COMMIT.")
    
    cursor.execute("SELECT * FROM akun_bank")
    for row in cursor.fetchall(): print(row)
    print()

    # ROLLBACK
    print("--- ROLLBACK ---")
    cursor.execute("START TRANSACTION")
    cursor.execute("UPDATE akun_bank SET saldo = 0 WHERE nama = 'Andi'")
    print("Membatalkan perubahan dengan ROLLBACK...")
    conn.rollback() # Membatalkan semua perubahan sejak START TRANSACTION
    
    cursor.execute("SELECT * FROM akun_bank")
    for row in cursor.fetchall(): print(row)
    print()

    # SAVEPOINT dan ROLLBACK TO SAVEPOINT
    print("--- SAVEPOINT & ROLLBACK TO SAVEPOINT ---")
    cursor.execute("START TRANSACTION")
    cursor.execute("UPDATE akun_bank SET saldo = 10000 WHERE nama = 'Andi'")
    cursor.execute("SAVEPOINT sp1") # Membuat titik simpan
    
    cursor.execute("UPDATE akun_bank SET saldo = 20000 WHERE nama = 'Budi'")
    print("Perubahan dilakukan pada Andi dan Budi. Melakukan ROLLBACK ke sp1 (hanya membatalkan perubahan Budi)...")
    cursor.execute("ROLLBACK TO sp1") # Kembali ke sp1
    conn.commit() # Simpan perubahan Andi (Budi dibatalkan)

    cursor.execute("SELECT * FROM akun_bank")
    for row in cursor.fetchall(): print(row)
    print()

    # TRANSACTION + ERROR HANDLING
    print("--- TRANSACTION + ERROR HANDLING ---")
    try:
        cursor.execute("START TRANSACTION")
        cursor.execute("UPDATE akun_bank SET saldo = saldo - 500 WHERE nama = 'Andi'")
        # Simulasi error: table yang tidak ada
        cursor.execute("UPDATE akun_bank_SALAH SET saldo = 0 WHERE nama = 'Budi'")
        conn.commit()
    except pymysql.Error as e:
        print(f"Terjadi error saat transaksi (Disimulasikan): {e}")
        print("Melakukan ROLLBACK otomatis karena error...")
        conn.rollback()
    
    cursor.execute("SELECT * FROM akun_bank")
    for row in cursor.fetchall(): print(row)
    print()

    # AUTOCOMMIT
    print("--- AUTOCOMMIT ---")
    # Secara default, Python (pymysql) mematikan autocommit (autocommit = False).
    # Jika kita mengaktifkannya, setiap statement SQL akan otomatis di-commit tanpa perlu conn.commit().
    cursor.execute("SET autocommit = 1") # Mengaktifkan autocommit
    cursor.execute("UPDATE akun_bank SET saldo = 8888 WHERE nama = 'Andi'")
    print("✅ Perubahan otomatis tersimpan karena AUTOCOMMIT aktif.")
    
    cursor.execute("SELECT * FROM akun_bank")
    for row in cursor.fetchall(): print(row)
    print()
    
    cursor.execute("SET autocommit = 0") # Mengembalikan ke default (autocommit mati)

    # ISOLATION LEVEL
    print("--- ISOLATION LEVEL (Koneksi/Session, Uncommitted changes, REPEATABLE READ) ---")
    # Konsep Koneksi/Session: Setiap koneksi (seperti 'conn' ini) memiliki session sendiri.
    # Perubahan (Uncommitted changes) dalam satu session yang belum di-COMMIT tidak akan terlihat oleh session lain (tergantung Isolation Level).
    
    # Menampilkan level isolasi saat ini
    try:
        cursor.execute("SELECT @@transaction_isolation")
        current_iso = cursor.fetchone()[0]
        print(f"Isolation Level Saat Ini: {current_iso}")
    except pymysql.Error:
        # Jika @@transaction_isolation tidak ditemukan (misal di MySQL lama menggunakan @@tx_isolation)
        cursor.execute("SELECT @@tx_isolation")
        current_iso = cursor.fetchone()[0]
        print(f"Isolation Level Saat Ini: {current_iso}")

    # Mengubah level ke REPEATABLE READ (Level Default InnoDB di MariaDB)
    # REPEATABLE READ: Memastikan bahwa jika kita membaca data yang sama berulang kali dalam satu transaksi,
    # kita akan selalu mendapatkan hasil yang sama, meskipun ada transaksi lain yang mengubah data tersebut.
    cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ")
    print("✅ Level isolasi untuk session ini diubah ke REPEATABLE READ.")

    print("Penjelasan Konsep:")
    print("- Konsep Session: Transaksi terjadi dalam lingkup session. Jika ada 2 terminal (koneksi) yang menjalankan SQL bersamaan, masing-masing adalah session yang berbeda.")
    print("- Uncommitted Changes: Jika Session A melakukan UPDATE tapi belum COMMIT, Session B tidak bisa melihat perubahan tersebut.")
    print("- REPEATABLE READ: Setelah Session A menjalankan SELECT pertama dalam transaksi, semua SELECT berikutnya dalam transaksi yang sama akan melihat versi data yang sama persis dengan SELECT pertama (tidak terpengaruh COMMIT dari Session B).")
    print()

    print("--- 4 TINGKATAN ISOLATION LEVEL ---")
    print("READ UNCOMMITTED")
    print("→ Dirty Read")
    print()
    print("READ COMMITTED")
    print("→ Dirty Read dicegah")
    print("→ Non-repeatable Read bisa terjadi")
    print("→ Phantom Read bisa terjadi")
    print()
    print("REPEATABLE READ")
    print("→ Dirty Read dicegah")
    print("→ Non-repeatable Read dicegah")
    print("→ snapshot konsisten")
    print()
    print("SERIALIZABLE")
    print("→ isolation paling ketat")
    print("→ concurrency lebih dibatasi")
    print("→ locking/blocking bisa terjadi")
    print()

    # Membersihkan tabel dummy transaksi agar tidak mengotori database
    cursor.execute("DROP TABLE IF EXISTS akun_bank")

except pymysql.Error as e:
    print(f"Terjadi error pada MariaDB: {e}")

finally:
    # Menutup koneksi database sangat penting agar memori tidak bocor
    if 'conn' in locals() and conn.open:
        cursor.close()
        conn.close()
