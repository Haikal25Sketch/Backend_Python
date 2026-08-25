import psycopg2
from psycopg2 import pool
import os

# ==============================================================================
# MATERI DASAR POSTGRESQL MENGGUNAKAN PYTHON (PSYCOPG2)
# ==============================================================================
#
# File ini berisi materi pembelajaran dasar penggunaan PostgreSQL dengan Python.
# Setiap bagian akan menjelaskan:
# 1. Apa itu (pengertian)
# 2. Apa fungsinya (kegunaan)
# 3. Contoh kode 
# 4. Kemungkinan output yang dihasilkan
# ==============================================================================

print("=== BELAJAR DASAR POSTGRESQL DENGAN PYTHON ===\n")

# Konfigurasi Database (Sesuaikan dengan kredensial Anda)
DB_CONFIG = {
    "dbname": "postgres",
    "user": "u0_a317",
    "password": "password",
    "host": "127.0.0.1",
    "port": "5432"
}


# ------------------------------------------------------------------------------
# 1. KONEKSI DASAR & EKSEKUSI QUERY
# ------------------------------------------------------------------------------
# APA ITU: 
# Ini adalah cara paling dasar untuk terhubung ke database PostgreSQL menggunakan
# modul psycopg2.connect().
#
# FUNGSI:
# Menginisialisasi komunikasi antara aplikasi Python kita dan server database PostgreSQL
# agar bisa mengeksekusi query SQL dan mengambil hasilnya menggunakan kursor (cursor).
#
# KEMUNGKINAN OUTPUT (Jika Berhasil):
# Output: Berhasil terhubung. Versi Database: PostgreSQL 14.x...

print("--- 1. KONEKSI DASAR ---")
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print(f"Output: Berhasil terhubung. Versi Database: {db_version[0]}\n")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Output Error: {e}\n")


# ------------------------------------------------------------------------------
# 2. CONNECTION POOLING
# ------------------------------------------------------------------------------
# APA ITU:
# Connection pool (kolam koneksi) adalah teknik membuat beberapa koneksi database
# yang disimpan (di-cache) di memori agar tetap terbuka dan siap dipakai kapan saja.
#
# FUNGSI:
# Daripada membuat koneksi baru setiap kali ada request (yang mana ini lambat dan 
# boros memori), aplikasi cukup meminjam koneksi yang sudah terbuka dari pool.
# Sangat efisien dan wajib dipakai untuk aplikasi dengan trafik (user) yang banyak.
#
# KEMUNGKINAN OUTPUT (Jika Berhasil):
# Output: Tanggal hari ini dari DB: 2026-08-24
# Output: Semua koneksi di pool ditutup.

print("--- 2. CONNECTION POOLING ---")
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **DB_CONFIG)
    if connection_pool:
        conn = connection_pool.getconn()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_date;")
            print(f"Output: Tanggal hari ini dari DB: {cursor.fetchone()[0]}")
            cursor.close()
            connection_pool.putconn(conn)
        
        connection_pool.closeall()
        print("Output: Semua koneksi di pool ditutup.\n")
except Exception as e:
    print(f"Output Error: {e}\n")


# ------------------------------------------------------------------------------
# 3. GET POSTGRESQL PROCESS ID (PID)
# ------------------------------------------------------------------------------
# APA ITU:
# PID (Process ID) adalah nomor identitas unik yang diberikan oleh sistem operasi
# (server database) untuk sebuah proses/sesi koneksi yang sedang berjalan.
#
# FUNGSI:
# Berfungsi mengetahui identitas (PID) dari backend PostgreSQL yang sedang 
# melayani koneksi kita saat ini. Sangat berguna untuk administrasi server,
# misalnya jika ada query yang "nyangkut" lama (stuck), kita bisa mematikan (kill)
# query tersebut menggunakan PID ini.
#
# KEMUNGKINAN OUTPUT (Jika Berhasil):
# Output: PostgreSQL Backend Process ID: 15432

print("--- 3. MENDAPATKAN POSTGRES PROCESS ID (PID) ---")
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("SELECT pg_backend_pid();")
    backend_pid = cursor.fetchone()[0]
    print(f"Output: PostgreSQL Backend Process ID: {backend_pid}\n")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Output Error: {e}\n")


# ------------------------------------------------------------------------------
# 4. TRANSAKSI (COMMIT & ROLLBACK)
# ------------------------------------------------------------------------------
# APA ITU:
# Transaksi adalah fitur di mana serangkaian operasi database (seperti Insert, 
# Update, Delete yang beruntun) dikelompokkan menjadi satu kesatuan tugas.
# 
# FUNGSI:
# Menjaga konsistensi data (ACID). 
# - COMMIT: Jika semua kode berhasil dieksekusi, barulah perubahan data disimpan
#   secara permanen.
# - ROLLBACK: Jika terjadi error atau kegagalan di tengah-tengah jalan, seluruh 
#   perubahan yang sudah terjadi akan dibatalkan, jadi data tidak "setengah-setengah".
#
# KEMUNGKINAN OUTPUT:
# Output (Jika Sukses) : Transaksi berhasil di-commit!
# Output (Jika Gagal)  : Terjadi error, transaksi dibatalkan (Rollback). Error: ...

print("--- 4. TRANSAKSI (COMMIT & ROLLBACK) ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Simulasi membuat tabel dan memasukkan data
    cursor.execute("CREATE TABLE IF NOT EXISTS contoh_transaksi (id SERIAL PRIMARY KEY, nama VARCHAR(50));")
    cursor.execute("INSERT INTO contoh_transaksi (nama) VALUES ('Test User');")
    
    # Jika sampai sini berhasil, simpan
    conn.commit()
    print("Output: Transaksi berhasil di-commit!")
    
    # Cleanup (opsional, agar database bersih lagi)
    cursor.execute("DROP TABLE contoh_transaksi;")
    conn.commit()
    
    cursor.close()
except Exception as e:
    if conn:
        conn.rollback() # Batalkan perubahan jika ada error!
    print(f"Output: Terjadi error, transaksi dibatalkan (Rollback). Error: {e}")
finally:
    if conn:
        conn.close()
print() # Beri spasi bari baru


# ------------------------------------------------------------------------------
# 5. ERROR HANDLING SPESIFIK POSTGRESQL (PSYCOPG2)
# ------------------------------------------------------------------------------
# APA ITU:
# Mekanisme menangkap jenis-jenis error yang sangat spesifik dan berkaitan 
# langsung dengan masalah database.
#
# FUNGSI:
# Membantu kita mengetahui akar masalah dengan presisi. Misalnya, apakah masalahnya 
# karena kredensial password salah, server down (OperationalError), atau murni karena
# penulisan sintaks SQL (query) yang salah (ProgrammingError).
#
# KEMUNGKINAN OUTPUT:
# Output: Programming Error: relation "tabel_yang_tidak_pernah_ada" does not exist

print("--- 5. ERROR HANDLING SPESIFIK POSTGRESQL ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Query ini akan SANGAT SENGAJA DIBUAT ERROR karena memanggil tabel gaib
    cursor.execute("SELECT * FROM tabel_yang_tidak_pernah_ada;")
    
except psycopg2.OperationalError as e:
    print(f"Output: Operational Error (Masalah koneksi/server): {e}")
except psycopg2.ProgrammingError as e:
    print(f"Output: Programming Error (Masalah query SQL salah): {e}")
except psycopg2.Error as e:
    print(f"Output: Error Database lainnya: {e}")
except Exception as e:
    print(f"Output: Error umum: {e}")
finally:
    if conn:
        conn.rollback()
        conn.close()
print() # Beri spasi baris baru


# ------------------------------------------------------------------------------
# 6. CURRENT DATABASE, USER & SCHEMA
# ------------------------------------------------------------------------------
# APA ITU:
# current_database(), current_user, current_schema() adalah fungsi built-in 
# (bawaan) yang disediakan langsung oleh database PostgreSQL.
#
# FUNGSI:
# Digunakan untuk mendapatkan informasi konteks (environment) dari sesi saat ini:
# - current_database(): Kita sedang terhubung ke database yang mana?
# - current_user: Kita login/terhubung menggunakan akun user apa?
# - current_schema(): Kita sedang ada di lingkup schema mana? (Default biasanya 'public')
# 
# Sangat berguna ketika kita butuh membuat log audit, membatasi akses hak cipta 
# tabel, atau saat aplikasi bekerja dengan banyak database/schema sekaligus secara dinamis.
#
# KEMUNGKINAN OUTPUT (Jika Berhasil):
# Output:
# Database saat ini : postgres
# User saat ini     : postgres
# Schema saat ini   : public

print("--- 6. CURRENT DATABASE, USER & SCHEMA ---")
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("SELECT current_database(), current_user, current_schema();")
    current_info = cursor.fetchone()
    
    print("Output:")
    print(f"Database saat ini : {current_info[0]}")
    print(f"User saat ini     : {current_info[1]}")
    print(f"Schema saat ini   : {current_info[2]}\n")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Output Error: {e}\n")


# ------------------------------------------------------------------------------
# 7. SCHEMA, "$user", DAN SEARCH_PATH
# ------------------------------------------------------------------------------
# APA ITU:
# - SCHEMA: Seperti folder atau direktori di dalam database untuk mengelompokkan tabel.
#   Secara default, PostgreSQL menaruh tabel di schema bernama 'public'.
# - "$user": Adalah variabel spesial di search_path. Jika ada schema yang namanya
#   persis sama dengan nama user (role) yang sedang login, PostgreSQL akan
#   memprioritaskan schema tersebut (karena "$user" biasanya elemen pertama di search_path).
# - SEARCH_PATH: Daftar urutan schema yang akan dicari oleh PostgreSQL ketika
#   kita menjalankan query (misal: SELECT * FROM customer) tanpa menyebutkan nama 
#   schemanya (seperti public.customer).
#
# FUNGSI:
# - search_path membuat kita tidak perlu repot mengetik nama schema berulang kali.
#   Sistem akan otomatis mengecek tabel pada schema pertama yang ada di search_path.
# - Jika kita menjalankan `SET search_path TO myschema;`, maka setiap query tanpa
#   menyebutkan schema akan merujuk ke tabel di dalam `myschema`.
#
# KEMUNGKINAN OUTPUT (Jika Berhasil):
# Output: Search Path saat ini: "$user", public
# Output: Berhasil membuat schema contoh_schema
# Output: Berhasil mengubah search_path menjadi contoh_schema
# Output: Schema saat ini (setelah diubah): contoh_schema

print("--- 7. SCHEMA, \"$user\", DAN SEARCH_PATH ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Melihat search_path default
    cursor.execute("SHOW search_path;")
    current_search_path = cursor.fetchone()[0]
    print(f"Output: Search Path saat ini: {current_search_path}")
    
    # Penjelasan "$user"
    print("Penjelasan:")
    print("Jika user kamu adalah 'postgres', dan ada schema bernama 'postgres',")
    print("maka query tanpa schema akan mencari ke schema 'postgres' terlebih dahulu.")
    print("Itu karena \"$user\" di search_path merujuk ke nama user yang sedang aktif.\n")
    
    # Mengubah search_path
    cursor.execute("CREATE SCHEMA IF NOT EXISTS contoh_schema;")
    print("Output: Berhasil membuat schema contoh_schema")
    
    cursor.execute("SET search_path TO contoh_schema;")
    print("Output: Berhasil mengubah search_path menjadi contoh_schema")
    
    cursor.execute("SELECT current_schema();")
    new_schema = cursor.fetchone()[0]
    print(f"Output: Schema saat ini (setelah diubah): {new_schema}\n")
    
    # Cleanup (kembalikan seperti semula untuk latihan)
    cursor.execute("SET search_path TO DEFAULT;")
    cursor.execute("DROP SCHEMA IF EXISTS contoh_schema CASCADE;")
    conn.commit()
    
    cursor.close()
except Exception as e:
    if conn:
        conn.rollback()
    print(f"Output Error: {e}\n")
finally:
    if conn:
        conn.close()


# ------------------------------------------------------------------------------
# 8. ROLE & USER, OWNERSHIP, DAN PRIVILEGES
# ------------------------------------------------------------------------------
# APA ITU:
# - ROLE & USER: Di PostgreSQL, Role dan User pada dasarnya adalah hal yang sama.
#   User hanyalah Role yang diberikan atribut LOGIN sehingga bisa masuk ke database. 
#   Role juga bisa digunakan sebagai "Group" untuk mengelompokkan role lain.
# - SCHEMA OWNERSHIP & TABLE OWNERSHIP: Setiap objek di PostgreSQL (database, schema, 
#   tabel, view, fungsi, dll) memiliki pemilik (Owner). Biasanya, siapa yang membuat
#   objek, otomatis menjadi owner-nya. Owner memiliki hak mutlak atas objeknya, 
#   termasuk hak untuk menghapus (DROP) atau memberi izin (GRANT) kepada role lain.
# - OWNERSHIP vs PRIVILEGES: 
#   > Ownership: Kepemilikan (hanya ada satu owner atau grup role owner). Owner 
#     punya kontrol penuh (ALTER, DROP, GRANT).
#   > Privileges: Hak akses parsial (misal: hanya boleh SELECT, INSERT, atau UPDATE) 
#     yang diberikan (di-GRANT) kepada user yang BUKAN owner. User yang hanya punya
#     privilege SELECT tidak akan bisa menghapus (DROP) tabel tersebut.
#
# FUNGSI:
# - Memastikan keamanan data dengan memberikan hak akses secukupnya (Principle of
#   Least Privilege).
# - Melacak pemilik objek menggunakan query sistem, misalnya melalui view `pg_tables`.
#
# KEMUNGKINAN OUTPUT (Jika Berhasil):
# Output: Berhasil membuat role/user baru 'contoh_user'
# Output: Schema 'contoh_schema_baru' berhasil dibuat dengan owner 'contoh_user'
# Output: Tabel 'test_schema' dibuat dan kepemilikannya diubah ke 'contoh_user'
# Output: Cek pg_tables -> Schema: public, Tabel: test_schema, Owner: contoh_user

print("--- 8. ROLE & USER, OWNERSHIP, DAN PRIVILEGES ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 1. Role & User
    cursor.execute("DROP ROLE IF EXISTS contoh_user;")
    cursor.execute("CREATE ROLE contoh_user WITH LOGIN PASSWORD 'rahasia';")
    print("Output: Berhasil membuat role/user baru 'contoh_user'")
    
    # 2. Schema Ownership
    cursor.execute("DROP SCHEMA IF EXISTS contoh_schema_baru CASCADE;")
    cursor.execute("CREATE SCHEMA contoh_schema_baru AUTHORIZATION contoh_user;")
    print("Output: Schema 'contoh_schema_baru' berhasil dibuat dengan owner 'contoh_user'")
    
    # 3. Table Ownership
    cursor.execute("DROP TABLE IF EXISTS test_schema;")
    cursor.execute("CREATE TABLE test_schema (id INT);")
    
    # Mengubah owner tabel (Table Ownership)
    cursor.execute("ALTER TABLE test_schema OWNER TO contoh_user;")
    print("Output: Tabel 'test_schema' dibuat dan kepemilikannya diubah ke 'contoh_user'")
    
    # 4. Mengecek Table Ownership menggunakan pg_tables (Sesuai Permintaan)
    query_cek_owner = """
        SELECT schemaname, tablename, tableowner 
        FROM pg_tables 
        WHERE tablename = 'test_schema';
    """
    cursor.execute(query_cek_owner)
    hasil_cek = cursor.fetchone()
    if hasil_cek:
        print(f"Output: Cek pg_tables -> Schema: {hasil_cek[0]}, Tabel: {hasil_cek[1]}, Owner: {hasil_cek[2]}")
    
    # 5. Cleanup
    cursor.execute("DROP TABLE IF EXISTS test_schema;")
    cursor.execute("DROP SCHEMA IF EXISTS contoh_schema_baru CASCADE;")
    cursor.execute("DROP ROLE IF EXISTS contoh_user;")
    conn.commit()
    print("Output: Cleanup berhasil (objek-objek latihan telah dihapus)\n")
    
    cursor.close()
except Exception as e:
    if conn:
        conn.rollback()
    print(f"Output Error: {e}\n")
finally:
    if conn:
        conn.close()
