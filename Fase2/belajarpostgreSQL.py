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
    cursor.execute("CREATE TABLE IF NOT EXISTS tabel_latihan_transaksi_dummy_99 (id SERIAL PRIMARY KEY, nama VARCHAR(50));")
    cursor.execute("INSERT INTO tabel_latihan_transaksi_dummy_99 (nama) VALUES ('Test User');")
    
    # Jika sampai sini berhasil, simpan
    conn.commit()
    print("Output: Transaksi berhasil di-commit!")
    
    # Cleanup (opsional, agar database bersih lagi)
    cursor.execute("DROP TABLE tabel_latihan_transaksi_dummy_99;")
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
# Output: Programming Error: relation "tabel_pasti_gaib_123" does not exist

print("--- 5. ERROR HANDLING SPESIFIK POSTGRESQL ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Query ini akan SANGAT SENGAJA DIBUAT ERROR karena memanggil tabel gaib
    cursor.execute("SELECT * FROM tabel_pasti_gaib_123;")
    
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
# Output: Berhasil membuat schema skema_contoh_88
# Output: Berhasil mengubah search_path menjadi skema_contoh_88
# Output: Schema saat ini (setelah diubah): skema_contoh_88

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
    cursor.execute("CREATE SCHEMA IF NOT EXISTS skema_contoh_88;")
    print("Output: Berhasil membuat schema skema_contoh_88")
    
    cursor.execute("SET search_path TO skema_contoh_88;")
    print("Output: Berhasil mengubah search_path menjadi skema_contoh_88")
    
    cursor.execute("SELECT current_schema();")
    new_schema = cursor.fetchone()[0]
    print(f"Output: Schema saat ini (setelah diubah): {new_schema}\n")
    
    # Cleanup (kembalikan seperti semula untuk latihan)
    cursor.execute("SET search_path TO DEFAULT;")
    cursor.execute("DROP SCHEMA IF EXISTS skema_contoh_88 CASCADE;")
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
# Output: Berhasil membuat role/user baru 'user_latihan_99'
# Output: Schema 'skema_baru_latihan_99' berhasil dibuat dengan owner 'user_latihan_99'
# Output: Tabel 'tabel_uji_kepemilikan_88' dibuat dan kepemilikannya diubah ke 'user_latihan_99'
# Output: Cek pg_tables -> Schema: public, Tabel: tabel_uji_kepemilikan_88, Owner: user_latihan_99

print("--- 8. ROLE & USER, OWNERSHIP, DAN PRIVILEGES ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 1. Role & User
    cursor.execute("DROP ROLE IF EXISTS user_latihan_99;")
    cursor.execute("CREATE ROLE user_latihan_99 WITH LOGIN PASSWORD 'rahasia';")
    print("Output: Berhasil membuat role/user baru 'user_latihan_99'")
    
    # 2. Schema Ownership
    cursor.execute("DROP SCHEMA IF EXISTS skema_baru_latihan_99 CASCADE;")
    cursor.execute("CREATE SCHEMA skema_baru_latihan_99 AUTHORIZATION user_latihan_99;")
    print("Output: Schema 'skema_baru_latihan_99' berhasil dibuat dengan owner 'user_latihan_99'")
    
    # 3. Table Ownership
    cursor.execute("DROP TABLE IF EXISTS tabel_uji_kepemilikan_88;")
    cursor.execute("CREATE TABLE tabel_uji_kepemilikan_88 (id INT);")
    
    # Mengubah owner tabel (Table Ownership)
    cursor.execute("ALTER TABLE tabel_uji_kepemilikan_88 OWNER TO user_latihan_99;")
    print("Output: Tabel 'tabel_uji_kepemilikan_88' dibuat dan kepemilikannya diubah ke 'user_latihan_99'")
    
    # 4. Mengecek Table Ownership menggunakan pg_tables (Sesuai Permintaan)
    query_cek_owner = """
        SELECT schemaname, tablename, tableowner 
        FROM pg_tables 
        WHERE tablename = 'tabel_uji_kepemilikan_88';
    """
    cursor.execute(query_cek_owner)
    hasil_cek = cursor.fetchone()
    if hasil_cek:
        print(f"Output: Cek pg_tables -> Schema: {hasil_cek[0]}, Tabel: {hasil_cek[1]}, Owner: {hasil_cek[2]}")
    
    # 5. Cleanup
    cursor.execute("DROP TABLE IF EXISTS tabel_uji_kepemilikan_88;")
    cursor.execute("DROP SCHEMA IF EXISTS skema_baru_latihan_99 CASCADE;")
    cursor.execute("DROP ROLE IF EXISTS user_latihan_99;")
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


# ------------------------------------------------------------------------------
# 9. GRANT, REVOKE, ACL, DAN META-COMMANDS PSQL (\dp, \du, \dn+, \dt)
# ------------------------------------------------------------------------------
# APA ITU:
# - GRANT: Perintah SQL untuk memberikan hak akses (privilege) kepada suatu Role/User.
# - REVOKE: Perintah SQL untuk mencabut hak akses dari suatu Role/User.
# - ACL (Access Control List): Daftar kontrol akses di PostgreSQL. Formatnya
#   seperti 'owner=arwdDxt/owner, user_baca_99=r/owner' (a=insert, r=select, w=update, d=delete).
#
# META-COMMANDS PSQL (Digunakan di terminal/cli 'psql', BUKAN dari Python):
# - \dt  : Menampilkan daftar tabel di database saat ini.
# - \du  : Menampilkan daftar role / user beserta atributnya.
# - \dp  : Menampilkan daftar hak akses (privileges / ACL) pada tabel, view, dll.
# - \dn+ : Menampilkan daftar schema beserta hak aksesnya dan penjelasan.
#
# FUNGSI:
# Digunakan untuk manajemen keamanan (memberi/mencabut hak akses). Karena meta-commands
# seperti \dp tidak bisa jalan di Python, kita membaca ACL secara manual dari
# tabel sistem `pg_class` pada kolom `relacl`.
#
# KEMUNGKINAN OUTPUT (Jika Berhasil):
# Output: Berhasil GRANT SELECT pada tabel_uji_acl_77 ke user_baca_99
# Output: ACL Tabel -> Tabel: tabel_uji_acl_77, ACL: ['postgres=arwdDxtm/postgres', 'user_baca_99=r/postgres']
# Output: Berhasil REVOKE SELECT pada tabel_uji_acl_77 dari user_baca_99

print("--- 9. GRANT, REVOKE, DAN PEMBACAAN ACL ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Persiapan User dan Tabel
    cursor.execute("DROP ROLE IF EXISTS user_baca_99;")
    cursor.execute("CREATE ROLE user_baca_99;")
    
    cursor.execute("DROP TABLE IF EXISTS tabel_uji_acl_77;")
    cursor.execute("CREATE TABLE tabel_uji_acl_77 (id INT, nama VARCHAR(50));")
    
    # 1. GRANT (Memberikan Hak Akses SELECT)
    cursor.execute("GRANT SELECT ON tabel_uji_acl_77 TO user_baca_99;")
    print("Output: Berhasil GRANT SELECT pada tabel_uji_acl_77 ke user_baca_99")
    
    # 2. PEMBACAAN ACL DARI pg_class (Alternatif \dp di Python)
    query_acl = """
        SELECT relname, relacl 
        FROM pg_class 
        WHERE relname = 'tabel_uji_acl_77';
    """
    cursor.execute(query_acl)
    hasil_acl = cursor.fetchone()
    if hasil_acl:
        print(f"Output: ACL Tabel -> Tabel: {hasil_acl[0]}, ACL: {hasil_acl[1]}")
    
    # 3. REVOKE (Mencabut Hak Akses SELECT)
    cursor.execute("REVOKE SELECT ON tabel_uji_acl_77 FROM user_baca_99;")
    print("Output: Berhasil REVOKE SELECT pada tabel_uji_acl_77 dari user_baca_99")
    
    # Cek ACL setelah di-REVOKE
    cursor.execute(query_acl)
    hasil_acl_setelah = cursor.fetchone()
    if hasil_acl_setelah:
        print(f"Output: ACL Setelah REVOKE -> Tabel: {hasil_acl_setelah[0]}, ACL: {hasil_acl_setelah[1]}")
    
    # 4. Penjelasan Meta-Commands
    print("\nCatatan Meta-Commands (untuk dicoba langsung di terminal psql):")
    print(" - \\dt  : Menampilkan tabel.")
    print(" - \\du  : Menampilkan user/role.")
    print(" - \\dp  : Menampilkan hak akses (ACL) tabel.")
    print(" - \\dn+ : Menampilkan daftar schema.\n")
    
    # Cleanup
    cursor.execute("DROP TABLE IF EXISTS tabel_uji_acl_77;")
    cursor.execute("DROP ROLE IF EXISTS user_baca_99;")
    conn.commit()
    print("Output: Cleanup berhasil untuk sesi GRANT/REVOKE.\n")
    
    cursor.close()
except Exception as e:
    if conn:
        conn.rollback()
    print(f"Output Error: {e}\n")
finally:
    if conn:
        conn.close()


# ------------------------------------------------------------------------------
# 10. HAK AKSES USAGE, SERTA SYSTEM CATALOG (pg_tables & pg_authid)
# ------------------------------------------------------------------------------
# APA ITU:
# - USAGE: Adalah jenis hak akses (privilege) di PostgreSQL. Jika kita memiliki 
#   tabel di dalam suatu schema (selain schema public), memiliki hak SELECT saja 
#   pada tabel tersebut tidaklah cukup. User juga wajib diberi hak USAGE pada 
#   schema-nya agar bisa "melewati" atau mengakses isi dari schema tersebut.
# - pg_tables: Adalah view sistem (system catalog) yang berisi daftar informasi
#   semua tabel yang ada di database (seperti nama schema, nama tabel, owner).
# - pg_authid / pg_auth_members: Adalah tabel sistem internal PostgreSQL yang
#   menyimpan informasi terkait otentikasi (auth) dari role/user, termasuk
#   password terenkripsi (di pg_authid). Biasanya hanya superuser yang bisa
#   mengakses pg_authid demi keamanan, sedangkan user biasa menggunakan view 
#   pg_roles.
#
# FUNGSI:
# - USAGE: Digunakan untuk mengizinkan user memakai resource di sebuah schema, 
#   sequence, atau custom data type.
# - pg_tables: Membantu DBA atau developer untuk melihat, mengaudit, dan mencari
#   daftar tabel.
# - pg_authid: Digunakan sistem untuk keperluan otentikasi login pengguna dan
#   audit keamanan tingkat tinggi oleh superuser.
#
# KEMUNGKINAN OUTPUT (Jika Berhasil):
# Output: Berhasil GRANT USAGE pada schema skema_usage_123 ke user_tes_usage
# Output: Cek pg_tables -> Ditemukan tabel: tabel_tes_usage di schema skema_usage_123
# Output: Cek pg_authid -> Role: user_tes_usage ditemukan.

print("--- 10. HAK AKSES USAGE, SERTA SYSTEM CATALOG (pg_tables & pg_authid) ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Persiapan User, Schema, dan Tabel
    cursor.execute("DROP TABLE IF EXISTS skema_usage_123.tabel_tes_usage;")
    cursor.execute("DROP SCHEMA IF EXISTS skema_usage_123 CASCADE;")
    cursor.execute("DROP ROLE IF EXISTS user_tes_usage;")
    
    cursor.execute("CREATE ROLE user_tes_usage WITH LOGIN PASSWORD 'rahasia123';")
    cursor.execute("CREATE SCHEMA skema_usage_123;")
    cursor.execute("CREATE TABLE skema_usage_123.tabel_tes_usage (id INT, keterangan VARCHAR(50));")
    
    # 1. HAK AKSES USAGE
    cursor.execute("GRANT USAGE ON SCHEMA skema_usage_123 TO user_tes_usage;")
    print("Output: Berhasil GRANT USAGE pada schema skema_usage_123 ke user_tes_usage")
    
    cursor.execute("GRANT SELECT ON skema_usage_123.tabel_tes_usage TO user_tes_usage;")
    print("Output: Berhasil GRANT SELECT pada tabel_tes_usage ke user_tes_usage")
    
    # 2. MELIHAT DAFTAR TABEL MELALUI pg_tables
    query_pg_tables = """
        SELECT schemaname, tablename, tableowner 
        FROM pg_tables 
        WHERE tablename = 'tabel_tes_usage';
    """
    cursor.execute(query_pg_tables)
    hasil_tabel = cursor.fetchone()
    if hasil_tabel:
        print(f"Output: Cek pg_tables -> Ditemukan tabel: {hasil_tabel[1]} di schema {hasil_tabel[0]} dengan owner {hasil_tabel[2]}")
    
    # 3. MELIHAT DATA OTENTIKASI DI pg_authid 
    # (Gunakan try-except karena user default mungkin bukan superuser dan akan terkena Permission Denied)
    try:
        # Menggunakan SAVEPOINT agar jika query error, transaksi utama tidak batal
        cursor.execute("SAVEPOINT cek_auth;")
        query_pg_authid = """
            SELECT rolname, rolpassword 
            FROM pg_authid 
            WHERE rolname = 'user_tes_usage';
        """
        cursor.execute(query_pg_authid)
        hasil_auth = cursor.fetchone()
        if hasil_auth:
            print(f"Output: Cek pg_authid -> Role: {hasil_auth[0]}, Password (Enkripsi): {hasil_auth[1][:10]}...")
    except psycopg2.Error as e:
        print(f"Output: Gagal akses pg_authid (membutuhkan hak superuser). Error Code: {e.pgcode}")
        cursor.execute("ROLLBACK TO SAVEPOINT cek_auth;")
        
    # Cleanup
    cursor.execute("DROP TABLE IF EXISTS skema_usage_123.tabel_tes_usage;")
    cursor.execute("DROP SCHEMA IF EXISTS skema_usage_123 CASCADE;")
    cursor.execute("DROP ROLE IF EXISTS user_tes_usage;")
    conn.commit()
    print("Output: Cleanup berhasil untuk sesi USAGE, pg_tables & pg_authid.\n")
    
    cursor.close()
except Exception as e:
    if conn:
        conn.rollback()
    print(f"Output Error: {e}\n")
finally:
    if conn:
        conn.close()


# ------------------------------------------------------------------------------
# 11. ROLE MEMBERSHIP & INHERITANCE (PENUTUP)
# ------------------------------------------------------------------------------
# APA ITU:
# - ROLE MEMBERSHIP: Sebuah Role (user) dapat menjadi anggota (member) dari Role
#   lain (grup). Contoh: user 'readonly' adalah anggota dari grup 'tester'.
# - INHERIT: Atribut yang mengizinkan sebuah role secara otomatis mewarisi hak 
#   akses (privileges) dari role grup yang diikutinya.
#   (readonly -> tester, dengan INHERIT, privilege tester menjadi effective 
#   privilege bagi readonly).
# - MEMBERSHIP != PRIVILEGE: Menjadi anggota grup bukan berarti otomatis mendapat
#   izin. Jika role anggota memiliki opsi NOINHERIT, dia tidak langsung mendapat
#   privilege dari grupnya (harus menggunakan perintah SET ROLE terlebih dahulu).
#
# KONSEP PENTING MENGAKSES OBJEK DALAM SCHEMA:
# Untuk dapat mengakses tabel/objek di dalam sebuah schema (selain schema public),
# persyaratannya adalah kombinasi wajib dari DUA hal ini:
#
#        USAGE ON SCHEMA
#              +
#        PRIVILEGE ON OBJECT (misal: SELECT, INSERT, UPDATE, dll)
#
# Jika user hanya memiliki salah satu dari izin di atas, akses akan ditolak!
#
# KEMUNGKINAN OUTPUT (Jika Berhasil):
# Output: Berhasil memasukkan 'readonly' ke dalam grup 'tester'
# Output: Diberikan 'USAGE ON SCHEMA' + 'SELECT ON TABLE' ke grup 'tester'
# Output: Karena INHERIT, 'readonly' sekarang mewarisi effective privilege tersebut!

print("--- 11. ROLE MEMBERSHIP & INHERITANCE (PENUTUP) ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Persiapan Role dan Schema
    cursor.execute("DROP TABLE IF EXISTS schema_role_member.tabel_member;")
    cursor.execute("DROP SCHEMA IF EXISTS schema_role_member CASCADE;")
    cursor.execute("DROP ROLE IF EXISTS readonly;")
    cursor.execute("DROP ROLE IF EXISTS tester;")
    
    # 1. Membuat Role Grup 'tester'
    cursor.execute("CREATE ROLE tester;")
    
    # 2. Membuat Role User 'readonly' dengan atribut INHERIT
    cursor.execute("CREATE ROLE readonly WITH LOGIN PASSWORD 'rahasia' INHERIT;")
    
    # 3. Role Membership: Memasukkan 'readonly' ke grup 'tester'
    cursor.execute("GRANT tester TO readonly;")
    print("Output: Berhasil memasukkan 'readonly' ke dalam grup 'tester' (readonly -> tester)")
    
    # 4. Membuat Schema & Tabel
    cursor.execute("CREATE SCHEMA schema_role_member;")
    cursor.execute("CREATE TABLE schema_role_member.tabel_member (id INT);")
    
    # 5. Memberikan USAGE + Privilege ke grup 'tester'
    # 'tester' mendapat USAGE pada schema dan SELECT pada tabel.
    cursor.execute("GRANT USAGE ON SCHEMA schema_role_member TO tester;")
    cursor.execute("GRANT SELECT ON schema_role_member.tabel_member TO tester;")
    
    print("Output: Diberikan 'USAGE ON SCHEMA' + 'SELECT ON TABLE' ke grup 'tester'")
    print("Output: Karena INHERIT, privilege tester kini menjadi effective privilege bagi 'readonly'!")
    print("Output: User 'readonly' kini bisa mengakses tabel tersebut secara langsung.")
    
    # Cleanup
    cursor.execute("DROP TABLE IF EXISTS schema_role_member.tabel_member;")
    cursor.execute("DROP SCHEMA IF EXISTS schema_role_member CASCADE;")
    cursor.execute("DROP ROLE IF EXISTS readonly;")
    cursor.execute("DROP ROLE IF EXISTS tester;")
    conn.commit()
    print("Output: Cleanup berhasil untuk sesi Role Membership.\n")
    
    cursor.close()
except Exception as e:
    if conn:
        conn.rollback()
    print(f"Output Error: {e}\n")
finally:
    if conn:
        conn.close()


# ------------------------------------------------------------------------------
# 12. IDENTITY, SERIAL, DAN OVERRIDE SYSTEM VALUE
# ------------------------------------------------------------------------------
# APA ITU:
# - SERIAL: Tipe data pseudo di PostgreSQL (seperti SERIAL, BIGSERIAL) yang
#   secara otomatis membuat sequence (urutan angka) di belakang layar untuk
#   mengisi kolom secara auto-increment.
# - IDENTITY: Standar SQL modern untuk auto-increment (GENERATED ALWAYS AS IDENTITY
#   atau GENERATED BY DEFAULT AS IDENTITY). Lebih direkomendasikan daripada SERIAL
#   pada versi PostgreSQL terbaru karena manajemen privilege dan dependensinya lebih rapi.
# - OVERRIDE SYSTEM VALUE: Ketika kolom diset sebagai GENERATED ALWAYS AS IDENTITY,
#   sistem menolak jika kita mencoba memasukkan nilai manual (insert explicit id).
#   Untuk memaksa memasukkan nilai manual, kita menggunakan klausa 
#   OVERRIDING SYSTEM VALUE.
#
# FUNGSI:
# Digunakan untuk pembuatan Primary Key (ID) unik yang otomatis bertambah (1, 2, 3..).
# Membedakan penggunaan SERIAL lama dengan IDENTITY baru, serta cara "memaksa"
# insert data manual pada kolom IDENTITY yang dikunci.
#
# KEMUNGKINAN OUTPUT (Jika Berhasil):
# Output: Berhasil memasukkan data menggunakan SERIAL
# Output: Berhasil memasukkan data menggunakan IDENTITY (BY DEFAULT)
# Output: Gagal memasukkan data manual ke IDENTITY (ALWAYS) karena dikunci
# Output: Berhasil memasukkan data manual ke IDENTITY (ALWAYS) dengan OVERRIDING SYSTEM VALUE
# Output: Data Tabel Serial: [(1, 'Andi')]
# Output: Data Tabel Identity Default: [(1, 'Budi'), (99, 'Caca')]
# Output: Data Tabel Identity Always: [(1, 'Dodi'), (99, 'Euis')]

print("--- 12. IDENTITY, SERIAL, DAN OVERRIDE SYSTEM VALUE ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 1. Menggunakan SERIAL
    cursor.execute("DROP TABLE IF EXISTS contoh_serial;")
    cursor.execute("CREATE TABLE contoh_serial (id SERIAL PRIMARY KEY, nama VARCHAR(50));")
    cursor.execute("INSERT INTO contoh_serial (nama) VALUES ('Andi');")
    print("Output: Berhasil memasukkan data menggunakan SERIAL")
    
    # 2. Menggunakan IDENTITY (BY DEFAULT)
    # Bisa diisi otomatis, tapi kalau kita masukkan manual (contoh id=99) tidak akan error
    cursor.execute("DROP TABLE IF EXISTS contoh_identity_default;")
    cursor.execute("CREATE TABLE contoh_identity_default (id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY, nama VARCHAR(50));")
    cursor.execute("INSERT INTO contoh_identity_default (nama) VALUES ('Budi');")
    cursor.execute("INSERT INTO contoh_identity_default (id, nama) VALUES (99, 'Caca');")
    print("Output: Berhasil memasukkan data menggunakan IDENTITY (BY DEFAULT)")
    
    # 3. Menggunakan IDENTITY (ALWAYS)
    # Sistem yang menentukan ID. Jika diisi manual akan error kecuali memakai OVERRIDING
    cursor.execute("DROP TABLE IF EXISTS contoh_identity_always;")
    cursor.execute("CREATE TABLE contoh_identity_always (id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, nama VARCHAR(50));")
    cursor.execute("INSERT INTO contoh_identity_always (nama) VALUES ('Dodi');")
    
    # Mencoba insert manual tanpa OVERRIDING (Pasti Error)
    try:
        # SAVEPOINT agar transaksi tidak batal total saat error
        cursor.execute("SAVEPOINT uji_identity_always;")
        cursor.execute("INSERT INTO contoh_identity_always (id, nama) VALUES (99, 'Euis_Gagal');")
    except psycopg2.Error as e:
        print("Output: Gagal memasukkan data manual ke IDENTITY (ALWAYS) karena dikunci")
        cursor.execute("ROLLBACK TO SAVEPOINT uji_identity_always;")
        
    # Memaksa insert manual dengan OVERRIDING SYSTEM VALUE
    cursor.execute("INSERT INTO contoh_identity_always (id, nama) OVERRIDING SYSTEM VALUE VALUES (99, 'Euis');")
    print("Output: Berhasil memasukkan data manual ke IDENTITY (ALWAYS) dengan OVERRIDING SYSTEM VALUE")
    
    # Tampilkan Data
    cursor.execute("SELECT * FROM contoh_serial;")
    print(f"Output: Data Tabel Serial: {cursor.fetchall()}")
    
    cursor.execute("SELECT * FROM contoh_identity_default;")
    print(f"Output: Data Tabel Identity Default: {cursor.fetchall()}")
    
    cursor.execute("SELECT * FROM contoh_identity_always;")
    print(f"Output: Data Tabel Identity Always: {cursor.fetchall()}\n")
    
    # Cleanup
    cursor.execute("DROP TABLE IF EXISTS contoh_serial;")
    cursor.execute("DROP TABLE IF EXISTS contoh_identity_default;")
    cursor.execute("DROP TABLE IF EXISTS contoh_identity_always;")
    conn.commit()
    print("Output: Cleanup berhasil untuk sesi Identity & Serial.\n")
    
    cursor.close()
except Exception as e:
    if conn:
        conn.rollback()
    print(f"Output Error: {e}\n")
finally:
    if conn:
        conn.close()
