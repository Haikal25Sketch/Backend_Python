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


# ------------------------------------------------------------------------------
# 13. TIPE DATA KARAKTER (TEXT, VARCHAR, CHAR)
# ------------------------------------------------------------------------------
# APA ITU:
# Di PostgreSQL, terdapat 3 tipe data utama untuk menyimpan string/teks:
# 1. TEXT       : Menyimpan string dengan panjang tidak terbatas.
# 2. VARCHAR(n) : Menyimpan string dengan panjang variabel, tetapi maksimal 'n' karakter. 
#                 (Jika tanpa 'n', sifatnya sama persis seperti TEXT).
# 3. CHAR(n)    : Menyimpan string dengan panjang tetap 'n' karakter. Jika teks yang
#                 dimasukkan kurang dari 'n', PostgreSQL akan menambahkan spasi (padding)
#                 di belakangnya hingga panjangnya pas 'n'. CHAR (tanpa 'n') berarti CHAR(1).
#
# KAPAN HARUS DIPAKAI & TIDAK DIPAKAI:
# - TEXT       : SANGAT DIREKOMENDASIKAN. Gunakan untuk hampir semua kebutuhan teks. Di
#                PostgreSQL, TEXT dan VARCHAR tidak memiliki perbedaan performa.
# - VARCHAR(n) : Gunakan HANYA JIKA Anda benar-benar perlu membatasi panjang input pengguna 
#                (misal maksimal 50 karakter) di level database.
# - CHAR(n)    : SEBAIKNYA JANGAN DIPAKAI. Sangat tidak direkomendasikan karena memakan
#                storage ekstra (karena padding spasi) dan sering menimbulkan masalah 
#                saat pencarian/perbandingan string.
#
# KEMUNGKINAN OUTPUT:
# Output: Berhasil membuat tabel tipe karakter
# Output: Insert data sukses!
# Output Data:
# - TEXT: 'Bebas sepanjang apapun' (Len: 22)
# - VARCHAR(10): 'MaksSepulh' (Len: 10)
# - CHAR(10): 'PasSepuluh' (Len: 10)
# - CHAR(10) dengan padding: 'Pendek    ' (Len: 10)

print("--- 13. TIPE DATA KARAKTER (TEXT, VARCHAR, CHAR) ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS contoh_tipe_karakter;")
    
    query_create = """
    CREATE TABLE contoh_tipe_karakter (
        kolom_text TEXT,
        kolom_varchar VARCHAR(10),
        kolom_char CHAR(10)
    );
    """
    cursor.execute(query_create)
    print("Output: Berhasil membuat tabel tipe karakter")
    
    # Insert data (perhatikan CHAR yang akan di-padding jika kurang dari 10)
    query_insert = """
    INSERT INTO contoh_tipe_karakter (kolom_text, kolom_varchar, kolom_char)
    VALUES 
    ('Bebas sepanjang apapun', 'MaksSepulh', 'PasSepuluh'),
    ('Data text lain', 'Pendek', 'Pendek');
    """
    cursor.execute(query_insert)
    print("Output: Insert data sukses!")
    
    # Ambil data dan lihat panjang aslinya (length)
    cursor.execute("SELECT kolom_text, length(kolom_text), kolom_varchar, length(kolom_varchar), kolom_char, length(kolom_char) FROM contoh_tipe_karakter;")
    rows = cursor.fetchall()
    
    print("Output Data:")
    for row in rows:
        print(f"- TEXT: '{row[0]}' (Len: {row[1]}) | VARCHAR(10): '{row[2]}' (Len: {row[3]}) | CHAR(10): '{row[4]}' (Len: {row[5]})")
        
    cursor.execute("DROP TABLE IF EXISTS contoh_tipe_karakter;")
    conn.commit()
    print("Output: Cleanup tabel berhasil.\\n")
    
    cursor.close()
except Exception as e:
    if conn:
        conn.rollback()
    print(f"Output Error: {e}\\n")
finally:
    if conn:
        conn.close()


# ------------------------------------------------------------------------------
# 14. TIPE DATA NUMERIK & TYPE CASTING (::)
# ------------------------------------------------------------------------------
# APA ITU:
# PostgreSQL memiliki beberapa tipe data angka (numerik) utama:
# - smallint : Angka bulat kecil, memakan memori 2 byte (-32768 s/d +32767).
# - integer  : Angka bulat standar, memakan memori 4 byte (-2 milyar s/d +2 milyar).
# - bigint   : Angka bulat besar, memakan memori 8 byte (sangat besar).
# - numeric  : Angka desimal presisi eksak (exact decimal). Sempurna untuk data uang 
#              atau finansial karena tidak ada pembulatan yang aneh.
# - real     : Angka desimal (floating point) 4 byte dengan presisi variabel/tidak eksak.
# - double precision : Angka desimal (floating point) 8 byte. Lebih detail dari real,
#                      biasa dipakai untuk kalkulasi saintifik, tapi bukan untuk uang.
#
# TYPE CASTING (::):
# Tanda `::` adalah sintaks unik khas PostgreSQL untuk mengubah (casting) suatu tipe 
# data menjadi tipe data lain secara langsung. Misalnya, mengubah string '123' 
# menjadi angka integer: `'123'::integer`.
#
# KEMUNGKINAN OUTPUT:
# Output: Berhasil membuat tabel numerik
# Output: Insert data numerik sukses!
# Output Casting 1: Tipe string '100.50' di-cast ke NUMERIC menjadi 100.50
# Output Casting 2: Tipe integer 50 di-cast ke TEXT menjadi '50'

print("--- 14. TIPE DATA NUMERIK & TYPE CASTING (::) ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS contoh_numerik;")
    
    query_create = """
    CREATE TABLE contoh_numerik (
        id smallint,
        umur integer,
        saldo bigint,
        harga numeric(10, 2),    -- maksimal 10 digit, 2 di belakang koma
        berat_real real,
        jarak_double double precision
    );
    """
    cursor.execute(query_create)
    print("Output: Berhasil membuat tabel numerik")
    
    # Insert data dengan contoh type casting (::) di dalam query
    query_insert = """
    INSERT INTO contoh_numerik (id, umur, saldo, harga, berat_real, jarak_double)
    VALUES (
        '1'::smallint,             -- casting dari string ke smallint
        '25'::integer,             -- casting dari string ke integer
        10000000000,               -- bigint tidak perlu di-cast jika muat
        '99.99'::numeric,          -- casting dari string ke numeric
        '65.5'::real,              -- casting ke real
        '12345.6789'::double precision
    );
    """
    cursor.execute(query_insert)
    print("Output: Insert data numerik sukses!")
    
    # Contoh Type Casting dalam SELECT (mengubah bentuk saat diambil)
    # 1. String -> Numeric
    # 2. Integer -> Text
    cursor.execute("SELECT '100.50'::numeric, 50::text;")
    row_cast = cursor.fetchone()
    print(f"Output Casting 1: String '100.50' ke NUMERIC -> {row_cast[0]} (Tipe Python: {type(row_cast[0])})")
    print(f"Output Casting 2: Integer 50 ke TEXT -> '{row_cast[1]}' (Tipe Python: {type(row_cast[1])})")
    
    cursor.execute("DROP TABLE IF EXISTS contoh_numerik;")
    conn.commit()
    print("Output: Cleanup tabel numerik berhasil.\\n")
    
    cursor.close()
except Exception as e:
    if conn:
        conn.rollback()
    print(f"Output Error: {e}\\n")
finally:
    if conn:
        conn.close()


# ------------------------------------------------------------------------------
# 15. TIPE DATA WAKTU (DATE, TIMESTAMP, TIMESTAMPTZ)
# ------------------------------------------------------------------------------
# APA ITU:
# PostgreSQL memiliki tipe data khusus untuk menangani tanggal dan waktu:
# - DATE        : Hanya menyimpan tanggal (Tahun, Bulan, Tanggal). Tidak ada jam/waktu.
#                 Contoh format: 'YYYY-MM-DD' ('2026-09-01').
# - TIMESTAMP   : Menyimpan tanggal dan waktu, TAPI TANPA zona waktu (timezone).
#                 Sering juga disebut `timestamp without time zone`.
#                 Menyimpan secara harfiah apa yang dimasukkan (misal: jam 10 pagi,
#                 tanpa peduli di negara mana).
# - TIMESTAMPTZ : Menyimpan tanggal dan waktu DENGAN zona waktu (timezone).
#                 Sering juga disebut `timestamp with time zone`.
#                 Ini adalah format PALING DIREKOMENDASIKAN di PostgreSQL. Data 
#                 selalu dikonversi ke UTC di dalam database, namun saat di-SELECT,
#                 PostgreSQL akan menampilkannya sesuai dengan zona waktu lokal aplikasi/client.
#
# FUNGSI & KAPAN DIPAKAI:
# - DATE        : Gunakan untuk data yang murni hanya butuh tanggal tanpa peduli jam,
#                 seperti Tanggal Lahir (DOB) atau Tanggal Gajian.
# - TIMESTAMP   : Gunakan HANYA jika Anda ingin waktu absolut yang sama di seluruh dunia 
#                 (contoh: jam dinding dalam sebuah acara/log fiktif yang tidak butuh konversi
#                 zona waktu antar negara).
# - TIMESTAMPTZ : Gunakan SELALU untuk mencatat kapan sebuah data dibuat (created_at) 
#                 atau diubah (updated_at). Mencegah kebingungan zona waktu jika aplikasi
#                 Anda diakses oleh pengguna dari negara/zona waktu yang berbeda.
#
# KEMUNGKINAN OUTPUT:
# Output: Berhasil membuat tabel tanggal dan waktu
# Output: Insert data waktu sukses!
# Output Data:
# - DATE       : 1995-08-17 (Tipe: <class 'datetime.date'>)
# - TIMESTAMP  : 2026-09-01 10:00:00 (Tipe: <class 'datetime.datetime'>)
# - TIMESTAMPTZ: 2026-09-01 11:17:17+00:00 (Tipe: <class 'datetime.datetime'>)

print("--- 15. TIPE DATA WAKTU (DATE, TIMESTAMP, TIMESTAMPTZ) ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS contoh_waktu;")
    
    query_create = """
    CREATE TABLE contoh_waktu (
        id SERIAL PRIMARY KEY,
        tanggal_lahir DATE,
        waktu_login TIMESTAMP,
        waktu_transaksi TIMESTAMPTZ
    );
    """
    cursor.execute(query_create)
    print("Output: Berhasil membuat tabel tanggal dan waktu")
    
    # Insert data menggunakan fungsi built-in PostgreSQL (CURRENT_DATE, NOW())
    # NOW() otomatis menyimpan waktu lengkap. PostgreSQL menyesuaikan ke TIMESTAMP/TIMESTAMPTZ.
    query_insert = """
    INSERT INTO contoh_waktu (tanggal_lahir, waktu_login, waktu_transaksi)
    VALUES (
        '1995-08-17',                 -- Input literal untuk DATE
        '2026-09-01 10:00:00',        -- Input literal TIMESTAMP tanpa zona waktu
        NOW()                         -- Fungsi waktu saat ini
    );
    """
    cursor.execute(query_insert)
    print("Output: Insert data waktu sukses!")
    
    # Ambil data
    cursor.execute("SELECT tanggal_lahir, waktu_login, waktu_transaksi FROM contoh_waktu;")
    row = cursor.fetchone()
    
    if row:
        print("Output Data:")
        print(f"- DATE       : {row[0]} (Tipe: {type(row[0])})")
        print(f"- TIMESTAMP  : {row[1]} (Tipe: {type(row[1])})")
        print(f"- TIMESTAMPTZ: {row[2]} (Tipe: {type(row[2])})")
        
    cursor.execute("DROP TABLE IF EXISTS contoh_waktu;")
    conn.commit()
    print("Output: Cleanup tabel waktu berhasil.\n")
    
    cursor.close()
except Exception as e:
    if conn:
        conn.rollback()
    print(f"Output Error: {e}\n")
finally:
    if conn:
        conn.close()


# ------------------------------------------------------------------------------
# 16. BOOLEAN, NULL, DAN THREE-VALUED LOGIC
# ------------------------------------------------------------------------------
# APA ITU:
# - BOOLEAN : Tipe data yang hanya memiliki 3 kemungkinan nilai (Three-Valued Logic):
#             TRUE (Benar), FALSE (Salah), dan NULL (Tidak Diketahui/Kosong).
# - NULL    : Merepresentasikan nilai yang hilang, tidak diketahui, atau tidak ada.
#             NULL BUKANLAH angka nol (0), dan BUKAN string kosong ('').
# - THREE-VALUED LOGIC: Logika unik di mana operasi perbandingan atau logika yang
#             melibatkan NULL seringkali menghasilkan NULL (Unknown).
#
# OPERASI KOMBINASI AND & OR DENGAN NULL:
# - AND:
#   > TRUE AND NULL  menghasilkan NULL
#   > FALSE AND NULL menghasilkan FALSE
# - OR:
#   > TRUE OR NULL   menghasilkan TRUE
#   > FALSE OR NULL  menghasilkan NULL
#
# KEMUNGKINAN OUTPUT:
# Output: Evaluasi AND dan OR dengan NULL selesai.
# Output: TRUE AND NULL  -> None (NULL)
# Output: FALSE AND NULL -> False
# Output: TRUE OR NULL   -> True
# Output: FALSE OR NULL  -> None (NULL)

print("--- 16. BOOLEAN, NULL, DAN THREE-VALUED LOGIC ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Evaluasi logika AND
    cursor.execute("SELECT true AND NULL, false AND NULL;")
    hasil_and = cursor.fetchone()
    
    # Evaluasi logika OR
    cursor.execute("SELECT true OR NULL, false OR NULL;")
    hasil_or = cursor.fetchone()
    
    print("Output:")
    print(f"- TRUE AND NULL  -> {hasil_and[0]}")
    print(f"- FALSE AND NULL -> {hasil_and[1]}")
    print(f"- TRUE OR NULL   -> {hasil_or[0]}")
    print(f"- FALSE OR NULL  -> {hasil_or[1]}\n")
    
    cursor.close()
except Exception as e:
    print(f"Output Error: {e}\n")
finally:
    if conn:
        conn.close()


# ------------------------------------------------------------------------------
# 17. COALESCE
# ------------------------------------------------------------------------------
# APA ITU:
# COALESCE adalah fungsi yang menerima daftar nilai (argumen) dan mengembalikan
# nilai PERTAMA yang BUKAN NULL.
#
# FUNGSI:
# Sangat berguna untuk memberikan "nilai default" jika data asli bernilai NULL.
# Misalnya, jika kolom "diskon" NULL, kita bisa menggunakan COALESCE(diskon, 0)
# agar perhitungan matematika tidak menjadi NULL.
#
# KEMUNGKINAN OUTPUT:
# Output: COALESCE(NULL, NULL, 100, 200) -> 100
# Output: Diskon Produk A: 0 (Data asli NULL diganti 0)

print("--- 17. COALESCE ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COALESCE(NULL, NULL, 100, 200);")
    hasil_coalesce = cursor.fetchone()[0]
    print(f"Output: COALESCE(NULL, NULL, 100, 200) -> {hasil_coalesce}")
    
    # Simulasi penggunaan COALESCE pada data
    cursor.execute("SELECT COALESCE(NULL, 0);") # Simulasi kolom diskon yang NULL
    diskon = cursor.fetchone()[0]
    print(f"Output: Diskon Produk A: {diskon} (Data asli NULL diganti 0)\n")
    
    cursor.close()
except Exception as e:
    print(f"Output Error: {e}\n")
finally:
    if conn:
        conn.close()


# ------------------------------------------------------------------------------
# 18. CASE (SEARCHED CASE DAN SIMPLE CASE)
# ------------------------------------------------------------------------------
# APA ITU:
# CASE adalah struktur kondisional (mirip IF-ELSE dalam pemrograman) yang dapat
# digunakan langsung di dalam query SQL. Terdapat dua jenis:
#
# 1. SIMPLE CASE:
#    Membandingkan satu ekspresi/kolom dengan beberapa nilai pasti secara langsung.
#    Cocok untuk perbandingan persamaan (equality).
#    Sintaks: CASE ekspresi WHEN nilai1 THEN hasil1 WHEN nilai2 THEN hasil2 ELSE hasil_default END
#
# 2. SEARCHED CASE:
#    Mengevaluasi setiap kondisi boolean (bisa pakai >, <, AND, OR, dsb).
#    Lebih fleksibel dari Simple CASE.
#    Sintaks: CASE WHEN kondisi1 THEN hasil1 WHEN kondisi2 THEN hasil2 ELSE hasil_default END
#
# KEMUNGKINAN OUTPUT:
# Output Simple CASE (Status 2) -> 'Selesai'
# Output Searched CASE (Nilai 85) -> 'Lulus dengan Baik'

print("--- 18. CASE (SEARCHED CASE DAN SIMPLE CASE) ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 1. SIMPLE CASE
    # Misalkan status: 1 (Baru), 2 (Selesai), 3 (Batal)
    query_simple_case = """
        SELECT 
            CASE 2
                WHEN 1 THEN 'Baru'
                WHEN 2 THEN 'Selesai'
                WHEN 3 THEN 'Batal'
                ELSE 'Tidak Diketahui'
            END;
    """
    cursor.execute(query_simple_case)
    hasil_simple = cursor.fetchone()[0]
    print(f"Output Simple CASE (Status 2) -> '{hasil_simple}'")
    
    # 2. SEARCHED CASE
    # Misalkan nilai siswa: 85
    query_searched_case = """
        SELECT 
            CASE 
                WHEN 85 >= 90 THEN 'Sempurna'
                WHEN 85 >= 80 THEN 'Lulus dengan Baik'
                WHEN 85 >= 60 THEN 'Lulus'
                ELSE 'Gagal'
            END;
    """
    cursor.execute(query_searched_case)
    hasil_searched = cursor.fetchone()[0]
    print(f"Output Searched CASE (Nilai 85) -> '{hasil_searched}'\n")
    
    cursor.close()
except Exception as e:
    print(f"Output Error: {e}\n")
finally:
    if conn:
        conn.close()


# ------------------------------------------------------------------------------
# 19. STRING FUNCTIONS (||, CONCAT, CONCAT_WS)
# ------------------------------------------------------------------------------
# APA ITU:
# Fungsi dan operator string digunakan untuk menggabungkan dua atau lebih
# string menjadi satu kesatuan string.
#
# 1. Operator `||` (Piping / Concatenation Operator):
#    Menggabungkan string. Aturannya: Jika salah satu nilai yang digabung bernilai NULL,
#    maka hasil keseluruhan akan menjadi NULL.
#    Contoh: 'Halo ' || 'Dunia' -> 'Halo Dunia'
#            'Halo ' || NULL -> NULL
#
# 2. Fungsi CONCAT():
#    Menggabungkan argumen. Aturannya: Mengabaikan nilai NULL. Jika ada NULL,
#    NULL tersebut dianggap sebagai string kosong ('').
#    Contoh: CONCAT('Halo ', NULL, 'Dunia') -> 'Halo Dunia'
#
# 3. Fungsi CONCAT_WS() (Concatenate With Separator):
#    Menggabungkan string dengan pemisah (separator) di awal argumen.
#    Aturannya: Mengabaikan nilai NULL (tidak menambahkan separator ekstra untuk NULL).
#    Sintaks: CONCAT_WS(separator, string1, string2, ...)
#    Contoh: CONCAT_WS(', ', 'Apel', NULL, 'Jeruk') -> 'Apel, Jeruk'
#
# KEMUNGKINAN OUTPUT:
# Output Operator || (dengan NULL) -> None (NULL di Python)
# Output CONCAT (dengan NULL) -> 'Data PostgreSQL'
# Output CONCAT_WS -> 'Budi, 25, Jakarta'

print("--- 19. STRING FUNCTIONS (||, CONCAT, CONCAT_WS) ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 1. Operator ||
    cursor.execute("SELECT 'Belajar ' || NULL || 'PostgreSQL';")
    hasil_piping = cursor.fetchone()[0]
    print(f"Output Operator || (dengan NULL) -> {hasil_piping}")
    
    # 2. CONCAT
    cursor.execute("SELECT CONCAT('Data ', NULL, 'PostgreSQL');")
    hasil_concat = cursor.fetchone()[0]
    print(f"Output CONCAT (dengan NULL) -> '{hasil_concat}'")
    
    # 3. CONCAT_WS
    cursor.execute("SELECT CONCAT_WS(', ', 'Budi', NULL, '25', 'Jakarta');")
    hasil_concat_ws = cursor.fetchone()[0]
    print(f"Output CONCAT_WS -> '{hasil_concat_ws}'\n")
    
    cursor.close()
except Exception as e:
    print(f"Output Error: {e}\n")
finally:
    if conn:
        conn.close()


# ------------------------------------------------------------------------------
# 20. TIMESTAMPTZ DENGAN UTC DAN JENIS-JENISNYA
# ------------------------------------------------------------------------------
# APA ITU:
# PostgreSQL memiliki beberapa tipe data untuk menangani waktu dan tanggal.
#
# JENIS-JENIS TIPE DATA WAKTU:
# 1. DATE: Hanya menyimpan tanggal (Tahun-Bulan-Hari). Contoh: '2023-10-25'
# 2. TIME: Hanya menyimpan waktu (Jam:Menit:Detik). Contoh: '14:30:00'
# 3. TIMESTAMP: Menyimpan tanggal dan waktu TANPA zona waktu (Timestamp without time zone).
# 4. TIMESTAMPTZ: Menyimpan tanggal dan waktu DENGAN zona waktu (Timestamp with time zone).
#
# ATURAN TIMESTAMPTZ DAN UTC:
# - Saat kita memasukkan data TIMESTAMPTZ, PostgreSQL akan mengkonversinya
#   ke zona waktu UTC (Universal Time Coordinated) secara internal sebelum menyimpannya.
# - Saat kita melakukan query (SELECT) data tersebut, PostgreSQL akan mengubahnya 
#   kembali dari UTC ke zona waktu (timezone) yang sedang aktif di session/server saat itu.
# - Sangat disarankan (best practice) menyimpan waktu dalam format UTC dan tipe TIMESTAMPTZ
#   untuk menghindari kebingungan zona waktu dalam aplikasi global.
#
# KEMUNGKINAN OUTPUT:
# Output CURRENT_TIMESTAMP (Timestamptz) -> (Tergantung waktu server)
# Output TIMEZONE UTC -> (Waktu dalam UTC)

print("--- 20. TIMESTAMPTZ DENGAN UTC DAN JENIS-JENISNYA ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Melihat waktu saat ini (biasanya tipe TIMESTAMPTZ)
    cursor.execute("SELECT CURRENT_TIMESTAMP;")
    hasil_now = cursor.fetchone()[0]
    print(f"Output CURRENT_TIMESTAMP (Timestamptz) -> {hasil_now}")
    
    # Konversi waktu saat ini ke UTC secara eksplisit
    cursor.execute("SELECT CURRENT_TIMESTAMP AT TIME ZONE 'UTC';")
    hasil_utc = cursor.fetchone()[0]
    print(f"Output waktu di zona UTC -> {hasil_utc}\n")
    
    cursor.close()
except Exception as e:
    print(f"Output Error: {e}\n")
finally:
    if conn:
        conn.close()

# ------------------------------------------------------------------------------
# 21. OPERASI INTERVAL, DATE, DAN TIMESTAMP
# ------------------------------------------------------------------------------
# APA ITU:
# PostgreSQL memungkinkan kita melakukan operasi matematika pada tipe data waktu
# menggunakan tipe INTERVAL, serta menambahkan/mengurangi DATE dan TIMESTAMP.
#
# ATURAN OPERASI:
# 1. DATE + INTERVAL       -> TIMESTAMP (Menambahkan rentang waktu ke tanggal menghasilkan timestamp)
# 2. DATE - DATE           -> INTEGER (Mengurangi dua tanggal menghasilkan selisih jumlah hari)
# 3. TIMESTAMP + INTERVAL  -> TIMESTAMP (Menambahkan rentang waktu ke timestamp menghasilkan timestamp baru)
# 4. TIMESTAMP - TIMESTAMP -> INTERVAL (Mengurangi dua timestamp menghasilkan rentang waktu/interval)
#
# FUNGSI TAMBAHAN:
# - CURRENT_TIMESTAMP      : Mengembalikan tanggal dan waktu saat ini (dengan zona waktu / timestamptz)
# - AGE(timestamp1, timestamp2) : Menghitung selisih umur/durasi antara dua waktu (atau dari sekarang), hasilnya INTERVAL.
# - DATE_TRUNC('unit', timestamp) : Memotong timestamp ke unit tertentu (contoh: 'month' membulatkan ke tanggal 1 di bulan itu).
# - EXTRACT(unit FROM timestamp) : Mengekstrak nilai spesifik dari waktu (contoh: mengambil angka tahun atau bulan saja).

print("--- 21. OPERASI INTERVAL, DATE, DAN TIMESTAMP ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 1. Contoh DATE + INTERVAL -> TIMESTAMP
    cursor.execute("SELECT DATE '2023-01-01' + INTERVAL '5 days';")
    hasil_date_int = cursor.fetchone()[0]
    print(f"DATE + INTERVAL '5 days' -> {hasil_date_int} (Tipe: {type(hasil_date_int)})")

    # 2. Contoh DATE - DATE -> INTEGER (Jumlah hari)
    cursor.execute("SELECT DATE '2023-01-10' - DATE '2023-01-01';")
    hasil_date_date = cursor.fetchone()[0]
    print(f"DATE - DATE ('2023-01-10' - '2023-01-01') -> {hasil_date_date} hari (Tipe: {type(hasil_date_date)})")

    # 3. Contoh TIMESTAMP + INTERVAL -> TIMESTAMP
    cursor.execute("SELECT TIMESTAMP '2023-01-01 10:00:00' + INTERVAL '2 hours';")
    hasil_ts_int = cursor.fetchone()[0]
    print(f"TIMESTAMP + INTERVAL '2 hours' -> {hasil_ts_int} (Tipe: {type(hasil_ts_int)})")

    # 4. Contoh TIMESTAMP - TIMESTAMP -> INTERVAL
    cursor.execute("SELECT TIMESTAMP '2023-01-01 12:00:00' - TIMESTAMP '2023-01-01 10:00:00';")
    hasil_ts_ts = cursor.fetchone()[0]
    print(f"TIMESTAMP - TIMESTAMP -> {hasil_ts_ts} (Tipe: {type(hasil_ts_ts)})")
    
    # 5. Contoh CURRENT_TIMESTAMP
    cursor.execute("SELECT CURRENT_TIMESTAMP;")
    hasil_curr_ts = cursor.fetchone()[0]
    print(f"CURRENT_TIMESTAMP -> {hasil_curr_ts} (Tipe: {type(hasil_curr_ts)})")
    
    # 6. Contoh Fungsi AGE() -> INTERVAL
    cursor.execute("SELECT AGE(TIMESTAMP '2025-05-15', TIMESTAMP '2023-01-01');")
    hasil_age = cursor.fetchone()[0]
    print(f"AGE('2025-05-15', '2023-01-01') -> {hasil_age} (Tipe: {type(hasil_age)})")

    # 7. Contoh Fungsi DATE_TRUNC() -> TIMESTAMP
    cursor.execute("SELECT DATE_TRUNC('month', TIMESTAMP '2023-10-25 14:30:00');")
    hasil_date_trunc = cursor.fetchone()[0]
    print(f"DATE_TRUNC('month', '2023-10-25 14:30:00') -> {hasil_date_trunc} (Tipe: {type(hasil_date_trunc)})")

    # 8. Contoh Fungsi EXTRACT() -> NUMERIC / FLOAT
    cursor.execute("SELECT EXTRACT(year FROM TIMESTAMP '2023-10-25 14:30:00');")
    hasil_extract = cursor.fetchone()[0]
    print(f"EXTRACT(year FROM '2023-10-25 14:30:00') -> {hasil_extract} (Tipe: {type(hasil_extract)})\n")
    
    cursor.close()
except Exception as e:
    print(f"Output Error: {e}\n")
finally:
    if conn:
        conn.close()


# ------------------------------------------------------------------------------
# 22. UUID DAN RANDOM CHARACTERS
# ------------------------------------------------------------------------------
# APA ITU:
# UUID (Universally Unique Identifier) adalah tipe data 128-bit (berupa string hex 
# sepanjang 32 karakter yang dipisah tanda hubung) yang sangat ideal digunakan 
# sebagai Primary Key agar unik secara global di seluruh sistem/database.
#
# CARA MENDAPATKAN KARAKTER ACAK / UUID:
# - PostgreSQL versi 13+ memiliki fungsi bawaan `gen_random_uuid()` untuk menghasilkan
#   UUID versi 4 secara otomatis (random).
# - Pada versi lebih lama, kita bisa menggunakan extension `uuid-ossp` dengan
#   menjalankan query: CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; dan menggunakan
#   fungsi `uuid_generate_v4()`.
# Tapi ada juga versi yang lebih aman jika user ingin menjadikannya sebagai primary key yaitu 'uuidv7()'.
# KEMUNGKINAN OUTPUT:
# Output: Berhasil membuat tabel dengan UUID
# Output UUID Acak yang dihasilkan: 32 karakter acak (contoh: 550e8400-e29b-41d4-a716-446655440000)

print("--- 22. UUID DAN RANDOM CHARACTERS ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 1. Menghasilkan UUID secara langsung menggunakan gen_random_uuid()
    cursor.execute("SELECT gen_random_uuid();")
    random_uuid = cursor.fetchone()[0]
    print(f"Output UUID Acak langsung dari DB: {random_uuid} (Tipe: {type(random_uuid)})")
    
    # 2. Contoh implementasi UUID pada tabel
    cursor.execute("DROP TABLE IF EXISTS contoh_uuid;")
    query_create = """
    CREATE TABLE contoh_uuid (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        nama VARCHAR(50)
    );
    """
    cursor.execute(query_create)
    
    cursor.execute("INSERT INTO contoh_uuid (nama) VALUES ('Pengguna Pertama') RETURNING id;")
    inserted_id = cursor.fetchone()[0]
    print(f"Output: Berhasil insert data dengan UUID ID: {inserted_id}\\n")
    
    cursor.execute("DROP TABLE IF EXISTS contoh_uuid;")
    conn.commit()
    
    cursor.close()
except Exception as e:
    if conn:
        conn.rollback()
    print(f"Output Error: {e}\\n")
finally:
    if conn:
        conn.close()


# ------------------------------------------------------------------------------
# 23. ARRAY, AKSES ELEMENT, DAN CARDINALITY
# ------------------------------------------------------------------------------
# APA ITU:
# PostgreSQL memungkinkan sebuah kolom tabel untuk menyimpan sekumpulan nilai 
# berupa Array (daftar list). Array bisa memiliki tipe data apa saja (misal: INT[], TEXT[]).
#
# ATURAN & FUNGSI ARRAY DI POSTGRESQL:
# - Indexing di PostgreSQL dimulai dari angka 1 (bukan 0 seperti pada Python).
# - Mengakses elemen: menggunakan kurung siku, contoh `hobi[1]`.
# - cardinality(array): Fungsi untuk mendapatkan jumlah elemen di dalam array (panjang array).
# - array_append(array, elemen): Menambahkan elemen baru ke akhir array.
# - Operator `ANY` / `ALL`: Digunakan dalam klausa WHERE untuk memfilter array.
#
# KEMUNGKINAN OUTPUT:
# Output: Berhasil insert data array!
# Output Array Asli: ['Membaca', 'Berenang', 'Coding']
# Output Akses Index ke-2: Berenang
# Output Cardinality (Jumlah Hobi): 3

print("--- 23. ARRAY, AKSES ELEMENT, DAN CARDINALITY ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS contoh_array;")
    query_create = """
    CREATE TABLE contoh_array (
        id SERIAL PRIMARY KEY,
        nama VARCHAR(50),
        hobi TEXT[]
    );
    """
    cursor.execute(query_create)
    
    # Insert data array. Di Python kita bisa melempar list secara langsung ke driver psycopg2
    hobi_list = ['Membaca', 'Berenang', 'Coding']
    cursor.execute("INSERT INTO contoh_array (nama, hobi) VALUES (%s, %s);", ('Budi', hobi_list))
    print("Output: Berhasil insert data array!")
    
    # 1. Mengambil seluruh Array
    cursor.execute("SELECT hobi FROM contoh_array WHERE nama = 'Budi';")
    hasil_array = cursor.fetchone()[0]
    print(f"Output Array Asli dari DB: {hasil_array} (Tipe Python: {type(hasil_array)})")
    
    # 2. Mengakses Elemen Array (Ingat: Index dimulai dari 1) dan Cardinality
    # array_length(hobi, 1) juga bisa digunakan, tapi cardinality() lebih disarankan
    query_akses = "SELECT hobi[2], cardinality(hobi) FROM contoh_array WHERE nama = 'Budi';"
    cursor.execute(query_akses)
    hasil_akses = cursor.fetchone()
    print(f"Output Akses Index ke-2: {hasil_akses[0]}")
    print(f"Output Cardinality (Jumlah Hobi): {hasil_akses[1]}")
    
    # 3. Penggunaan fungsi ANY (Pencarian di dalam Array)
    cursor.execute("SELECT nama FROM contoh_array WHERE 'Coding' = ANY(hobi);")
    hasil_any = cursor.fetchone()
    if hasil_any:
        print(f"Output Pencarian (ANY): Ditemukan user bernama {hasil_any[0]} yang memiliki hobi Coding\\n")
        
    cursor.execute("DROP TABLE IF EXISTS contoh_array;")
    conn.commit()
    
    cursor.close()
except Exception as e:
    if conn:
        conn.rollback()
    print(f"Output Error: {e}\\n")
finally:
    if conn:
        conn.close()


# ------------------------------------------------------------------------------
# 24. JSON DAN JSONB
# ------------------------------------------------------------------------------
# APA ITU:
# PostgreSQL memiliki dukungan native untuk tipe data JSON.
# - JSON : Disimpan sebagai teks persis seperti yang diinputkan (termasuk spasi, urutan key).
#          Pengecekan validitas struktur JSON dilakukan saat insert, tapi proses baca (parsing)
#          dilakukan ulang saat query dijalankan.
# - JSONB: (JSON Binary). Disimpan dalam format binary yang sudah ter-parsing. Spasi
#          akan dihilangkan, urutan key tidak dijamin sama. SANGAT JAUH LEBIH CEPAT
#          dibanding JSON biasa saat melakukan pencarian (query) dan MENDUKUNG INDEXING 
#          (seperti GIN index). Sangat disarankan selalu pakai JSONB daripada JSON.
#
# CARA AKSES/MENGAMBIL DATA:
# - `->`  : Mengambil nilai JSON sebagai tipe JSON (mengembalikan dengan tanda kutip jika string).
# - `->>` : Mengambil nilai JSON sebagai tipe TEXT (mengembalikan tanpa tanda kutip).
# - `#>`  : Mengambil JSON object pada path tertentu.
# - `#>>` : Mengambil JSON text pada path tertentu.
#
# KEMUNGKINAN OUTPUT:
# Output: Berhasil membuat dan insert data ke tabel JSONB
# Output: Nama dari JSONB (sebagai TEXT): 'Siti'
# Output: Umur dari JSONB: 25
# Output: Kota (Nested JSON): 'Jakarta'

print("--- 24. JSON DAN JSONB ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS contoh_jsonb;")
    query_create = """
    CREATE TABLE contoh_jsonb (
        id SERIAL PRIMARY KEY,
        profil JSONB
    );
    """
    cursor.execute(query_create)
    
    # Data JSON/Dictionary dari Python yang akan dimasukkan ke database
    # psycopg2 otomatis mem-parsing Dictionary Python menjadi string JSON untuk PostgreSQL
    import json
    data_profil = {
        "nama": "Siti",
        "umur": 25,
        "alamat": {
            "kota": "Jakarta",
            "kodepos": "12345"
        },
        "skills": ["Python", "SQL"]
    }
    
    # Karena kita menggunakan Dictionary, psycopg2 akan memasukkannya dengan baik jika
    # kita melakukan dump string
    cursor.execute("INSERT INTO contoh_jsonb (profil) VALUES (%s);", (json.dumps(data_profil),))
    print("Output: Berhasil membuat dan insert data ke tabel JSONB")
    
    # 1. Mengambil field tunggal dari JSONB
    # Menggunakan -> (kembalian jsonb), dan ->> (kembalian text)
    query_ambil = """
        SELECT 
            profil->>'nama' AS nama_text, 
            profil->'nama' AS nama_json,
            profil->>'umur' AS umur_text
        FROM contoh_jsonb;
    """
    cursor.execute(query_ambil)
    hasil_jsonb = cursor.fetchone()
    print(f"Output ->> (Tipe Teks) : {hasil_jsonb[0]}")
    print(f"Output ->  (Tipe JSONb): {hasil_jsonb[1]}")
    print(f"Output Umur (Teks)     : {hasil_jsonb[2]}")
    
    # 2. Mengambil Nested JSON (Data Bersarang) menggunakan tipe path #>>
    # Meminta elemen: alamat -> kota
    query_nested = "SELECT profil#>>'{alamat,kota}' FROM contoh_jsonb;"
    cursor.execute(query_nested)
    hasil_nested = cursor.fetchone()[0]
    print(f"Output Kota (Nested JSON dengan #>>): {hasil_nested}")
    
    # 3. Filtering/Pencarian menggunakan JSONB operator `@>` (Contains)
    # Mencari baris yang JSON profilnya mengandung key "umur": 25
    query_cari = "SELECT profil->>'nama' FROM contoh_jsonb WHERE profil @> '{\"umur\": 25}'::jsonb;"
    cursor.execute(query_cari)
    hasil_cari = cursor.fetchone()[0]
    print(f"Output Filtering (Contains @>): User dengan umur 25 adalah {hasil_cari}\\n")
    
    cursor.execute("DROP TABLE IF EXISTS contoh_jsonb;")
    conn.commit()
    print(f"Output Filtering (Contains @>): User dengan umur 25 adalah {hasil_cari}\n")
    
    cursor.execute("DROP TABLE IF EXISTS contoh_jsonb;")
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
# 25. OPERATOR @> (CONTAINS) PADA JSONB & ARRAY
# ------------------------------------------------------------------------------
# APA ITU:
# Operator `@>` dibaca sebagai "Contains" (mengandung). Digunakan untuk memeriksa 
# apakah kumpulan nilai pada sisi kiri mengandung kumpulan nilai pada sisi kanan.
# 
# FUNGSI:
# Sangat kuat dan cepat bila digunakan untuk melakukan pencarian di dalam tipe data
# array atau struktur JSONB tanpa harus mengurai nilainya secara manual.
#
# KEMUNGKINAN OUTPUT (Jika Berhasil):
# Output: Data array mengandung [2, 3] -> (1, [1, 2, 3])
# Output: JSONB mengandung key 'tag' dengan nilai 'python' -> (1, '{"tag": ["python", "sql"]}')

print("--- 25. OPERATOR @> (CONTAINS) PADA JSONB & ARRAY ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 1. Contoh pada ARRAY
    cursor.execute("DROP TABLE IF EXISTS uji_contains_array;")
    cursor.execute("CREATE TABLE uji_contains_array (id INT, angka INT[]);")
    cursor.execute("INSERT INTO uji_contains_array VALUES (1, ARRAY[1, 2, 3]), (2, ARRAY[4, 5, 6]);")
    
    # Mencari yang mengandung 2 dan 3
    cursor.execute("SELECT * FROM uji_contains_array WHERE angka @> ARRAY[2, 3];")
    print(f"Output Array @> (Mencari 2 dan 3): {cursor.fetchall()}")
    
    # 2. Contoh pada JSONB
    cursor.execute("DROP TABLE IF EXISTS uji_contains_jsonb;")
    cursor.execute("CREATE TABLE uji_contains_jsonb (id INT, data JSONB);")
    cursor.execute("INSERT INTO uji_contains_jsonb VALUES (1, '{\"tag\": [\"python\", \"sql\"]}'), (2, '{\"tag\": [\"java\"]}');")
    
    # Mencari yang JSONB-nya mengandung tag python
    cursor.execute("SELECT * FROM uji_contains_jsonb WHERE data @> '{\"tag\": [\"python\"]}';")
    print(f"Output JSONB @> (Mencari tag python): {cursor.fetchall()}\n")
    
    cursor.execute("DROP TABLE IF EXISTS uji_contains_array;")
    cursor.execute("DROP TABLE IF EXISTS uji_contains_jsonb;")
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
# 26. JSONB + GIN INDEX
# ------------------------------------------------------------------------------
# APA ITU:
# GIN (Generalized Inverted Index) adalah jenis indeks di PostgreSQL yang khusus 
# dirancang untuk menangani tipe data gabungan/komposit yang kompleks seperti 
# JSONB, Array, atau teks Full Text Search.
# 
# FUNGSI:
# Digunakan secara kombinasi dengan JSONB untuk membuat proses pencarian key/value 
# atau pencarian isi elemen JSON menjadi sangat cepat walau datanya sangat besar.
# Tanpa GIN Index, pencarian elemen di dalam JSONB yang besar akan lambat.
#
# KEMUNGKINAN OUTPUT (Jika Berhasil):
# Output: Berhasil membuat tabel dengan data JSONB
# Output: Berhasil menambahkan GIN index
# Output: Pencarian sukses! Data: (1, '{"role": "admin", "user": "alice"}')

print("--- 26. JSONB + GIN INDEX ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS jsonb_gin_test;")
    cursor.execute("CREATE TABLE jsonb_gin_test (id INT, dokumen JSONB);")
    
    # Insert data
    cursor.execute("INSERT INTO jsonb_gin_test VALUES (1, '{\"user\": \"alice\", \"role\": \"admin\"}'), (2, '{\"user\": \"bob\", \"role\": \"staff\"}');")
    print("Output: Berhasil membuat tabel dan insert data JSONB")
    
    # Membuat GIN Index
    cursor.execute("CREATE INDEX idx_gin_dokumen ON jsonb_gin_test USING GIN (dokumen);")
    print("Output: Berhasil menambahkan GIN index pada kolom 'dokumen'")
    
    # Pencarian cepat
    cursor.execute("SELECT * FROM jsonb_gin_test WHERE dokumen @> '{\"role\": \"admin\"}';")
    print(f"Output Pencarian via GIN Index (Cari admin): {cursor.fetchall()}\n")
    
    cursor.execute("DROP TABLE IF EXISTS jsonb_gin_test;")
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
# 27. TIPE DATA ENUM & META-COMMAND \dT
# ------------------------------------------------------------------------------
# APA ITU:
# - ENUM (Enumerated Type) adalah tipe data kustom di PostgreSQL di mana kita 
#   mendefinisikan batasan nilai-nilai statis apa saja yang boleh disimpan 
#   (contoh: 'L', 'P' atau 'PENDING', 'SUKSES', 'GAGAL').
# - \dT adalah perintah di psql (Meta-Command) untuk menampilkan/melihat daftar 
#   tipe data (data types) kustom buatan user, seperti tipe ENUM.
#
# FUNGSI:
# - ENUM sangat berguna untuk menjamin integritas dan efisiensi data karena data
#   hanya bisa disi dengan nilai yang sudah didefinisikan sebelumnya, mencegah typo.
# - \dT adalah cara instan untuk mengecek tipe data buatan kita ada atau tidak 
#   di terminal.
#
# KEMUNGKINAN OUTPUT (Jika Berhasil):
# Output: Berhasil membuat tipe ENUM dan tabel
# Output: Insert data valid sukses! [(1, 'PENDING')]
# Output: Gagal insert karena nilai 'PROSES' bukan bagian dari ENUM!

print("--- 27. TIPE DATA ENUM & META-COMMAND \\dT ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Bersihkan tipe/tabel sebelumnya (agar tidak menumpuk)
    cursor.execute("DROP TABLE IF EXISTS transaksi;")
    cursor.execute("DROP TYPE IF EXISTS status_pesanan CASCADE;")
    
    # 1. CREATE TYPE ENUM
    cursor.execute("CREATE TYPE status_pesanan AS ENUM ('PENDING', 'SUKSES', 'GAGAL');")
    print("Output: Berhasil membuat tipe ENUM 'status_pesanan'")
    
    cursor.execute("CREATE TABLE transaksi (id INT, status status_pesanan);")
    cursor.execute("INSERT INTO transaksi VALUES (1, 'PENDING');")
    print("Output: Insert dengan ENUM valid sukses.")
    
    cursor.execute("SELECT * FROM transaksi;")
    print(f"Output Data ENUM: {cursor.fetchall()}")
    
    # 2. Test Insert Invalid Enum
    try:
        cursor.execute("SAVEPOINT uji_enum;")
        cursor.execute("INSERT INTO transaksi VALUES (2, 'PROSES');") # Error, tidak ada di ENUM
    except psycopg2.Error as e:
        print("Output: Gagal insert karena 'PROSES' bukan bagian dari ENUM!")
        cursor.execute("ROLLBACK TO SAVEPOINT uji_enum;")
        
    print("\nCatatan Meta-Command \\dT:")
    print("Ketik '\\dT' (tanpa tanda kutip) langsung di prompt terminal psql untuk ")
    print("melihat seluruh daftar tipe data kustom (termasuk tipe ENUM ini).\n")
    
    cursor.execute("DROP TABLE IF EXISTS transaksi;")
    cursor.execute("DROP TYPE IF EXISTS status_pesanan CASCADE;")
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
# 28. FOREIGN KEY BEHAVIOR (SEMUA JENIS)
# ------------------------------------------------------------------------------
# APA ITU:
# Foreign Key Behavior menentukan apa yang harus database lakukan pada baris data di 
# tabel "anak" (child / dependent) ketika data rujukan utamanya di tabel "induk" (parent) 
# DIHAPUS (DELETE) atau DIUBAH (UPDATE).
#
# JENIS-JENISNYA:
# 1. NO ACTION (Default) : Menolak penghapusan parent jika masih ada child yang 
#    merujuk. Penolakan / error dilempar pada akhir transaksi.
# 2. RESTRICT    : Menolak seketika (langsung error) penghapusan/perubahan parent.
# 3. CASCADE     : Ikut otomatis menghapus/mengubah baris data di tabel child jika 
#    baris parent dihapus/diubah.
# 4. SET NULL    : Kolom FK di tabel child akan diubah menjadi NULL jika parent dihapus.
# 5. SET DEFAULT : Kolom FK di tabel child akan dikembalikan ke nilai default-nya.
#
# FUNGSI:
# Mempertahankan Referential Integrity (integritas relasi antar data tabel).
#
# KEMUNGKINAN OUTPUT (Jika Berhasil):
# Output Uji 1: [RESTRICT] Gagal menghapus parent, dicegah oleh FK!
# Output Uji 2: [CASCADE] Child ikut terhapus, sisa child: []
# Output Uji 3: [SET NULL] Parent dihapus, nilai child mjd NULL: [(301, None)]
# Output Uji 4: [SET DEFAULT] Parent dihapus, child kembali default: [(401, 99)]

print("--- 28. FOREIGN KEY BEHAVIOR (SEMUA JENIS) ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS child_default, child_null, child_cascade, child_restrict, parent_table CASCADE;")
    
    # Buat Parent
    cursor.execute("CREATE TABLE parent_table (id INT PRIMARY KEY, nama VARCHAR(50));")
    
    # Buat 4 Jenis Child Table dengan Behavior berbeda-beda
    cursor.execute("CREATE TABLE child_restrict (id INT, p_id INT REFERENCES parent_table(id) ON DELETE RESTRICT);")
    cursor.execute("CREATE TABLE child_cascade (id INT, p_id INT REFERENCES parent_table(id) ON DELETE CASCADE);")
    cursor.execute("CREATE TABLE child_null (id INT, p_id INT REFERENCES parent_table(id) ON DELETE SET NULL);")
    cursor.execute("CREATE TABLE child_default (id INT, p_id INT DEFAULT 99 REFERENCES parent_table(id) ON DELETE SET DEFAULT);")
    
    # Insert Data Parent
    cursor.execute("INSERT INTO parent_table VALUES (1, 'Induk 1'), (2, 'Induk 2'), (3, 'Induk 3'), (4, 'Induk 4'), (99, 'Induk Default');")
    
    # Insert Data Child
    cursor.execute("INSERT INTO child_restrict VALUES (101, 1);")
    cursor.execute("INSERT INTO child_cascade VALUES (201, 2);")
    cursor.execute("INSERT INTO child_null VALUES (301, 3);")
    cursor.execute("INSERT INTO child_default VALUES (401, 4);")
    print("Output: Tabel dan baris data awal berhasil di-insert.\n")
    
    # UJI 1: RESTRICT
    try:
        cursor.execute("SAVEPOINT uji_restrict;")
        cursor.execute("DELETE FROM parent_table WHERE id = 1;")
    except psycopg2.Error as e:
        print("Output Uji 1: [RESTRICT/NO ACTION] Gagal menghapus parent (id=1) karena dicegah oleh Foreign Key!")
        cursor.execute("ROLLBACK TO SAVEPOINT uji_restrict;")
        
    # UJI 2: CASCADE
    cursor.execute("DELETE FROM parent_table WHERE id = 2;")
    cursor.execute("SELECT * FROM child_cascade;")
    print(f"Output Uji 2: [CASCADE] Parent id=2 dihapus, baris data child ikut terhapus: {cursor.fetchall()}")
    
    # UJI 3: SET NULL
    cursor.execute("DELETE FROM parent_table WHERE id = 3;")
    cursor.execute("SELECT * FROM child_null;")
    print(f"Output Uji 3: [SET NULL] Parent id=3 dihapus, nilai kolom p_id child mjd NULL: {cursor.fetchall()}")
    
    # UJI 4: SET DEFAULT
    cursor.execute("DELETE FROM parent_table WHERE id = 4;")
    cursor.execute("SELECT * FROM child_default;")
    print(f"Output Uji 4: [SET DEFAULT] Parent id=4 dihapus, p_id child mjd nilai default (99): {cursor.fetchall()}\n")
    
    # Cleanup
    cursor.execute("DROP TABLE IF EXISTS child_default, child_null, child_cascade, child_restrict, parent_table CASCADE;")
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
# 29. JOIN (INNER, LEFT, RIGHT, FULL OUTER, CROSS)
# ------------------------------------------------------------------------------
# APA ITU:
# JOIN digunakan untuk menggabungkan baris dari dua atau lebih tabel berdasarkan
# kolom terkait (relasi) di antara tabel-tabel tersebut.
#
# JENIS-JENIS JOIN UTAMA:
# 1. INNER JOIN : Mengembalikan baris-baris yang memiliki kecocokan (match) di KEDUA tabel.
# 2. LEFT JOIN  : Mengembalikan SEMUA baris dari tabel kiri, dan baris yang cocok dari tabel kanan. Jika tidak cocok, tabel kanan berisi NULL.
# 3. RIGHT JOIN : Mengembalikan SEMUA baris dari tabel kanan, dan baris yang cocok dari tabel kiri. Jika tidak cocok, tabel kiri berisi NULL.
# 4. FULL JOIN  : Mengembalikan SEMUA baris bila ada kecocokan baik di tabel kiri atau kanan. Menggabungkan hasil LEFT & RIGHT JOIN.
# 5. CROSS JOIN : Mengembalikan kombinasi perkalian kartesian (Cartesian product) dari kedua tabel. (Setiap baris di tabel A digabung dengan setiap baris di tabel B).
#
# FUNGSI:
# Mengambil dan merelasikan data yang tersebar di banyak tabel menjadi satu hasil yang komprehensif.
#
# KEMUNGKINAN OUTPUT (Jika Berhasil):
# Output: Tabel departemen dan karyawan berhasil dibuat dan diisi.
# Output INNER JOIN: Menampilkan data yang memiliki relasi lengkap.
# Output LEFT JOIN: Menampilkan semua karyawan, meskipun tidak memiliki departemen.
# Output FULL JOIN: Menampilkan semua data dari kedua tabel, dengan NULL jika tidak ada relasi.

print("--- 29. JOIN (INNER, LEFT, RIGHT, FULL OUTER, CROSS) ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Setup Tabel
    cursor.execute("DROP TABLE IF EXISTS karyawan, departemen CASCADE;")
    cursor.execute("CREATE TABLE departemen (id INT PRIMARY KEY, nama_dept VARCHAR(50));")
    cursor.execute("CREATE TABLE karyawan (id INT PRIMARY KEY, nama VARCHAR(50), dept_id INT);")
    
    # Insert Data
    cursor.execute("INSERT INTO departemen VALUES (1, 'IT'), (2, 'HRD'), (3, 'Finance');")
    cursor.execute("INSERT INTO karyawan VALUES (101, 'Andi', 1), (102, 'Budi', 2), (103, 'Caca', NULL), (104, 'Deni', 1);")
    print("Output: Tabel departemen dan karyawan berhasil dibuat dan diisi.\n")
    
    # 1. INNER JOIN
    query_inner = """
        SELECT k.nama, d.nama_dept 
        FROM karyawan k
        INNER JOIN departemen d ON k.dept_id = d.id;
    """
    cursor.execute(query_inner)
    print(f"Output INNER JOIN (Hanya yang cocok):\n{cursor.fetchall()}\n")
    
    # 2. LEFT JOIN
    query_left = """
        SELECT k.nama, d.nama_dept 
        FROM karyawan k
        LEFT JOIN departemen d ON k.dept_id = d.id;
    """
    cursor.execute(query_left)
    print(f"Output LEFT JOIN (Semua karyawan):\n{cursor.fetchall()}\n")
    
    # 3. RIGHT JOIN
    query_right = """
        SELECT k.nama, d.nama_dept 
        FROM karyawan k
        RIGHT JOIN departemen d ON k.dept_id = d.id;
    """
    cursor.execute(query_right)
    print(f"Output RIGHT JOIN (Semua departemen):\n{cursor.fetchall()}\n")
    
    # 4. FULL OUTER JOIN
    query_full = """
        SELECT k.nama, d.nama_dept 
        FROM karyawan k
        FULL OUTER JOIN departemen d ON k.dept_id = d.id;
    """
    cursor.execute(query_full)
    print(f"Output FULL OUTER JOIN (Semua data karyawan & departemen):\n{cursor.fetchall()}\n")
    
    # 5. CROSS JOIN
    query_cross = """
        SELECT k.nama, d.nama_dept 
        FROM karyawan k
        CROSS JOIN departemen d;
    """
    cursor.execute(query_cross)
    # Karena hasilnya panjang (4 karyawan * 3 dept = 12 baris), kita tampilkan panjangnya atau sebagian saja
    hasil_cross = cursor.fetchall()
    print(f"Output CROSS JOIN (Perkalian kartesian): Total {len(hasil_cross)} baris data.\n")
    
    # Cleanup
    cursor.execute("DROP TABLE IF EXISTS karyawan, departemen CASCADE;")
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
# 30. RECURSIVE CTE (COMMON TABLE EXPRESSIONS)
# ------------------------------------------------------------------------------
# APA ITU:
# CTE (Common Table Expression) adalah hasil set sementara yang diberi nama dan
# digunakan di dalam sebuah query (didefinisikan menggunakan klausa WITH).
# Recursive CTE adalah CTE yang memanggil dirinya sendiri.
#
# FUNGSI:
# Sangat berguna untuk mengelola atau menampilkan data hierarkis (struktur tree),
# seperti struktur organisasi (karyawan dan manajer), kategori bersarang (nested
# categories), atau sekadar menghasilkan deret angka.
#
# KEMUNGKINAN OUTPUT (Jika Berhasil):
# Output: Deret angka 1 sampai 5
# Output: Hierarki Organisasi (CEO -> Manajer -> Staf)
#
print("--- 30. RECURSIVE CTE ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # 1. Contoh Sederhana: Menghasilkan deret angka 1 sampai 5
    query_deret = """
        WITH RECURSIVE deret_angka(n) AS (
            SELECT 1                 -- Base case
            UNION ALL
            SELECT n + 1 FROM deret_angka WHERE n < 5 -- Recursive step
        )
        SELECT n FROM deret_angka;
    """
    cursor.execute(query_deret)
    print(f"Output Deret Angka 1-5:\n{cursor.fetchall()}\n")
    
    # 2. Contoh Hierarki Data Organisasi
    cursor.execute("DROP TABLE IF EXISTS karyawan_hierarki;")
    cursor.execute("CREATE TABLE karyawan_hierarki (id INT PRIMARY KEY, nama VARCHAR(50), manajer_id INT);")
    cursor.execute("INSERT INTO karyawan_hierarki VALUES (1, 'Budi (CEO)', NULL), (2, 'Andi (Manajer IT)', 1), (3, 'Caca (Staf IT)', 2), (4, 'Deni (Staf IT)', 2);")
    
    query_hierarki = """
        WITH RECURSIVE struktur_org AS (
            -- Base case: Karyawan tanpa manajer (CEO)
            SELECT id, nama, manajer_id, 1 AS tingkat
            FROM karyawan_hierarki
            WHERE manajer_id IS NULL
            
            UNION ALL
            
            -- Recursive step: Karyawan yang memiliki manajer
            SELECT k.id, k.nama, k.manajer_id, so.tingkat + 1
            FROM karyawan_hierarki k
            INNER JOIN struktur_org so ON k.manajer_id = so.id
        )
        SELECT tingkat, nama FROM struktur_org ORDER BY tingkat, id;
    """
    cursor.execute(query_hierarki)
    print(f"Output Hierarki Karyawan (Tingkat, Nama):\n{cursor.fetchall()}\n")
    
    # Cleanup
    cursor.execute("DROP TABLE IF EXISTS karyawan_hierarki;")
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
# 31. WINDOW FUNCTIONS (LAG, LEAD, & ROWS BETWEEN)
# ------------------------------------------------------------------------------
# APA ITU & FUNGSI:
# Window Functions melakukan kalkulasi terhadap serangkaian baris (window) yang 
# terhubung dengan baris saat ini. Berbeda dengan fungsi agregasi (GROUP BY) 
# yang menggabungkan hasil, Window Function mempertahankan baris aslinya.
#
# A. LAG & LEAD:
# - LAG(): Mengambil nilai dari baris SEBELUMNYA.
# - LEAD(): Mengambil nilai dari baris SETELAHNYA.
# *PENTING*: Fungsi ini BISA digunakan untuk melakukan PERHITUNGAN. Misalnya 
# menghitung persentase kenaikan/penurunan penjualan dari bulan sebelumnya, 
# selisih harga hari ini dengan kemarin, atau durasi antara event satu dengan lainnya.
#
# B. ROWS BETWEEN:
# Mendefinisikan secara spesifik "jendela" (window frame) baris mana saja yang 
# dilibatkan dalam kalkulasi. Terdiri dari:
# - PRECEDING: Baris sebelum baris saat ini (current row).
# - CURRENT ROW: Baris saat ini.
# - FOLLOWING: Baris setelah baris saat ini (current row).
# Contoh: ROWS BETWEEN 1 PRECEDING AND CURRENT ROW (Menghitung baris saat ini 
# ditambah 1 baris sebelumnya).
#
# KEMUNGKINAN OUTPUT (Jika Berhasil):
# Output perhitungan selisih pendapatan dari LAG
# Output Moving Average menggunakan ROWS BETWEEN
#
print("--- 31. WINDOW FUNCTIONS (LAG, LEAD, & ROWS BETWEEN) ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS penjualan_harian;")
    cursor.execute("CREATE TABLE penjualan_harian (tanggal DATE, pendapatan INT);")
    cursor.execute("INSERT INTO penjualan_harian VALUES ('2023-01-01', 100), ('2023-01-02', 150), ('2023-01-03', 120), ('2023-01-04', 200), ('2023-01-05', 250);")
    
    # 1. Menggunakan LAG dan LEAD untuk Perhitungan
    # Menghitung selisih pendapatan hari ini dibandingkan hari sebelumnya
    query_lag_lead = """
        SELECT 
            tanggal, 
            pendapatan,
            LAG(pendapatan) OVER(ORDER BY tanggal) AS pendapatan_kemarin,
            pendapatan - LAG(pendapatan) OVER(ORDER BY tanggal) AS selisih_dari_kemarin,
            LEAD(pendapatan) OVER(ORDER BY tanggal) AS pendapatan_besok
        FROM penjualan_harian;
    """
    cursor.execute(query_lag_lead)
    print("Output LAG & LEAD (Tanggal, Pendapatan, Pendapatan Kemarin, Selisih, Pendapatan Besok):")
    for row in cursor.fetchall():
        print(row)
    print()
    
    # 2. Menggunakan ROWS BETWEEN
    # Menghitung Moving Average (Rata-rata bergerak) untuk 3 hari: 1 hari sebelum, hari ini, dan 1 hari setelah
    query_rows_between = """
        SELECT 
            tanggal, 
            pendapatan,
            SUM(pendapatan) OVER(
                ORDER BY tanggal 
                ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
            ) AS total_3_hari,
            AVG(pendapatan) OVER(
                ORDER BY tanggal 
                ROWS BETWEEN 1 PRECEDING AND CURRENT ROW
            ) AS avg_2_hari_terakhir
        FROM penjualan_harian;
    """
    cursor.execute(query_rows_between)
    print("Output ROWS BETWEEN (Tanggal, Pendapatan, Total 3 Hari, Rata-rata 2 Hari Terakhir):")
    for row in cursor.fetchall():
        print(row)
    print()
    
    # Cleanup
    cursor.execute("DROP TABLE IF EXISTS penjualan_harian;")
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
# 32. VIEW
# ------------------------------------------------------------------------------
# APA ITU & KENAPA DIGUNAKAN:
# View adalah "tabel virtual" yang isinya didasarkan pada hasil query SQL.
# Kenapa digunakan:
# 1. Menyederhanakan query: Query kompleks (banyak JOIN) bisa disimpan sebagai View.
# 2. Keamanan: Menyembunyikan baris atau kolom sensitif dari pengguna tertentu.
# 3. Abstraksi/Konsistensi: Menyediakan antarmuka tabel yang tetap, meskipun struktur 
#    tabel asli (base table) diubah (selama kolom yang di-select tidak hilang).
#
# KAPAN MENGGUNAKAN VIEW VS CTE (Common Table Expression):
# - View: Gunakan ketika query tersebut SANGAT SERING digunakan berulang kali oleh 
#   berbagai query atau aplikasi lain (karena View bersifat persisten di database).
# - CTE: Gunakan untuk menyederhanakan satu query kompleks secara SEMENTARA. CTE 
#   hanya ada selama query tersebut dieksekusi dan tidak disimpan di database.
#
# MENGAPA CREATE OR REPLACE VIEW LEBIH BAGUS DARI MENGHAPUS & MEMBUAT BARU:
# Jika kita melakukan DROP VIEW lalu CREATE VIEW, object lain yang bergantung pada 
# view tersebut (misal view lain) akan error atau ikut terhapus.
# CREATE OR REPLACE VIEW akan mengubah query di balik view tanpa menghapus object 
# view itu sendiri, sehingga dependensi (hubungan dengan object lain) tetap aman.
#
# RESTRICT & CASCADE SAAT DROP VIEW:
# - RESTRICT (Default): Membatalkan penghapusan (DROP) jika ada object lain yang 
#   bergantung pada view tersebut.
# - CASCADE: Menghapus view tersebut BESERTA semua object lain yang bergantung padanya.
#
# UPDATABLE VIEW (VIEW YANG BISA DIUPDATE):
# View bisa di-INSERT, UPDATE, atau DELETE (dan otomatis mengubah tabel aslinya) JIKA:
# View tersebut sederhana, biasanya hanya dari 1 tabel dasar, TANPA fungsi agregat 
# (SUM, AVG), TANPA GROUP BY, HAVING, DISTINCT, UNION, atau LIMIT.
#
# VIEW YANG TIDAK BISA DIUPDATE SEMBARANGAN:
# View yang kompleks (banyak tabel dengan JOIN, agregasi, subquery). PostgreSQL 
# tidak tahu baris/tabel mana yang harus diubah jika kita melakukan update pada view 
# tersebut (Kecuali kita membuat trigger INSTEAD OF).
#
# WITH CHECK OPTION:
# Opsi keamanan pada View. Memastikan data yang di-INSERT atau di-UPDATE melalui 
# View HARUS memenuhi kondisi WHERE di dalam View tersebut. Jika tidak memenuhi, 
# operasi akan ditolak.
#
# KEMUNGKINAN OUTPUT (Jika Berhasil):
# Data view setelah diupdate, memperlihatkan bahwa data berhasil diubah.
#
print("--- 32. VIEW ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Persiapan Tabel Base
    cursor.execute("DROP TABLE IF EXISTS tb_pegawai CASCADE;")
    cursor.execute("""
        CREATE TABLE tb_pegawai (
            id SERIAL PRIMARY KEY,
            nama VARCHAR(50),
            departemen VARCHAR(50),
            gaji INT
        );
    """)
    cursor.execute("""
        INSERT INTO tb_pegawai (nama, departemen, gaji) VALUES 
        ('Andi', 'IT', 7000000), 
        ('Budi', 'HR', 5000000), 
        ('Citra', 'IT', 8500000),
        ('Dewi', 'Finance', 9000000);
    """)
    
    # 1. Membuat View Sederhana (Updatable View)
    cursor.execute("""
        CREATE OR REPLACE VIEW view_pegawai_it AS 
        SELECT id, nama, departemen, gaji 
        FROM tb_pegawai 
        WHERE departemen = 'IT';
    """)
    
    # 2. Mengupdate Data Melalui View (Akan mengubah tb_pegawai juga)
    cursor.execute("UPDATE view_pegawai_it SET gaji = 7500000 WHERE nama = 'Andi';")
    
    # 3. Membuat View dengan WITH CHECK OPTION
    cursor.execute("""
        CREATE OR REPLACE VIEW view_pegawai_hr AS 
        SELECT id, nama, departemen, gaji 
        FROM tb_pegawai 
        WHERE departemen = 'HR'
        WITH CHECK OPTION;
    """)
    
    # Jika kita insert pegawai IT melalui view_pegawai_hr, akan ERROR, tapi karena
    # kita berada di dalam block try-except, query tersebut di-comment saja sebagai contoh:
    # cursor.execute("INSERT INTO view_pegawai_hr (nama, departemen, gaji) VALUES ('Eko', 'IT', 6000000);") 
    
    # Mari kita select data view nya
    cursor.execute("SELECT * FROM view_pegawai_it;")
    print(f"Data view_pegawai_it (Gaji Andi sudah update menjadi 7500000):\n{cursor.fetchall()}\n")
    
    # Cleanup ( CASCADE juga akan menghapus view_pegawai_it dan view_pegawai_hr )
    cursor.execute("DROP TABLE IF EXISTS tb_pegawai CASCADE;")
    conn.commit()
    cursor.close()
except Exception as e:
    if conn:
        conn.rollback()
    print(f"Output Error: {e}\n")
finally:
    if conn:
        conn.close()

# ==============================================================================
# 33. MATERIALIZED VIEW
# ==============================================================================
#
# PENGERTIAN MATERIALIZED VIEW:
# Materialized View mirip dengan View biasa, tetapi perbedaannya adalah 
# Materialized View menyimpan BENTUK FISIK dari hasil query tersebut di dalam disk.
# 
# PERBEDAAN DENGAN VIEW BIASA:
# - View Biasa: Hanya menyimpan query-nya saja. Setiap kali kita me-SELECT view 
#   tersebut, database akan menjalankan ulang query aslinya secara real-time.
# - Materialized View: Menjalankan query sekali pada saat dibuat (atau direfresh) 
#   dan menyimpan hasilnya secara permanen (layaknya tabel sungguhan).
#
# KEUNTUNGAN:
# - Sangat cepat untuk dibaca (SELECT) karena datanya sudah tersedia, sangat cocok 
#   untuk query analitik/laporan kompleks yang membutuhkan waktu lama (misal: 
#   agregasi dari jutaan baris data, join kompleks).
#
# KEKURANGAN:
# - Data tidak real-time. Jika tabel asli (base table) berubah, data di Materialized 
#   View TIDAK akan berubah sampai kita melakukan REFRESH MATERIALIZED VIEW.
#
print("--- 33. MATERIALIZED VIEW ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Persiapan
    cursor.execute("DROP MATERIALIZED VIEW IF EXISTS mv_laporan_penjualan;")
    cursor.execute("DROP TABLE IF EXISTS tb_penjualan CASCADE;")
    
    cursor.execute("""
        CREATE TABLE tb_penjualan (
            id SERIAL PRIMARY KEY,
            produk VARCHAR(50),
            jumlah INT,
            harga_satuan INT
        );
    """)
    cursor.execute("""
        INSERT INTO tb_penjualan (produk, jumlah, harga_satuan) VALUES 
        ('Laptop', 2, 10000000), 
        ('Mouse', 10, 150000), 
        ('Keyboard', 5, 500000);
    """)

    # 1. Membuat Materialized View
    # Menyimpan hasil agregasi ke dalam materialized view
    cursor.execute("""
        CREATE MATERIALIZED VIEW mv_laporan_penjualan AS
        SELECT produk, sum(jumlah * harga_satuan) AS total_pendapatan
        FROM tb_penjualan
        GROUP BY produk;
    """)

    # Menampilkan data Materialized View
    cursor.execute("SELECT * FROM mv_laporan_penjualan;")
    print(f"Data Materialized View AWAL:\n{cursor.fetchall()}\n")

    # 2. Perubahan pada Tabel Asli
    # Kita masukkan data baru ke tabel asli
    cursor.execute("INSERT INTO tb_penjualan (produk, jumlah, harga_satuan) VALUES ('Mouse', 5, 150000);")
    
    # 3. SELECT Materialized View Sebelum Refresh
    # Data di mv_laporan_penjualan belum berubah (TIDAK real-time)
    cursor.execute("SELECT * FROM mv_laporan_penjualan WHERE produk = 'Mouse';")
    print(f"Data Materialized View untuk Mouse SEBELUM Refresh (Masih lama):\n{cursor.fetchall()}\n")

    # 4. REFRESH MATERIALIZED VIEW
    # Memperbarui data Materialized View agar sinkron dengan data tabel asli saat ini
    cursor.execute("REFRESH MATERIALIZED VIEW mv_laporan_penjualan;")
    
    # 5. SELECT Materialized View Setelah Refresh
    cursor.execute("SELECT * FROM mv_laporan_penjualan WHERE produk = 'Mouse';")
    print(f"Data Materialized View untuk Mouse SETELAH Refresh (Sudah terupdate):\n{cursor.fetchall()}\n")

    # Cleanup
    cursor.execute("DROP MATERIALIZED VIEW IF EXISTS mv_laporan_penjualan;")
    cursor.execute("DROP TABLE IF EXISTS tb_penjualan CASCADE;")
    
    conn.commit()
    cursor.close()
except Exception as e:
    if conn:
        conn.rollback()
    print(f"Output Error: {e}\n")
finally:
    if conn:
        conn.close()

# ==============================================================================
# 34. CREATE FUNCTION (STORED FUNCTION)
# ==============================================================================
#
# PENGERTIAN FUNCTION:
# Function di PostgreSQL memungkinkan kita menyimpan sekumpulan logika/blok kode 
# SQL atau prosedural (PL/pgSQL) di dalam database server.
#
# KEGUNAAN:
# - Reusability: Kode yang sering digunakan bisa disimpan di database, lalu 
#   dipanggil oleh berbagai aplikasi tanpa perlu menulis ulang query/logika kompleks.
# - Performa: Mengurangi traffic jaringan (network traffic) karena proses dilakukan 
#   langsung di server database.
# - Keamanan: Membatasi akses langsung ke tabel dan mengharuskan user melewati 
#   logika di dalam function.
#
# STRUKTUR DASAR (PL/pgSQL):
# CREATE [OR REPLACE] FUNCTION nama_fungsi(parameter1 tipe_data, ...) 
# RETURNS tipe_data_return AS $$
# DECLARE
#    -- deklarasi variabel lokal (opsional)
# BEGIN
#    -- blok logika / query
#    RETURN nilai_kembalian;
# END;
# $$ LANGUAGE plpgsql;
#
print("--- 34. CREATE FUNCTION ---")
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 1. Membuat Function yang menerima 2 angka dan mengembalikan hasil kalinya
    cursor.execute("""
        CREATE OR REPLACE FUNCTION hitung_perkalian(a INT, b INT)
        RETURNS INT AS $$
        BEGIN
            RETURN a * b;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Memanggil Function
    cursor.execute("SELECT hitung_perkalian(15, 4);")
    hasil_kali = cursor.fetchone()[0]
    print(f"Hasil panggil function hitung_perkalian(15, 4): {hasil_kali}\n")

    # 2. Function kompleks (mengambil data dari tabel)
    cursor.execute("DROP TABLE IF EXISTS tb_produk CASCADE;")
    cursor.execute("""
        CREATE TABLE tb_produk (
            id SERIAL PRIMARY KEY,
            nama_produk VARCHAR(100),
            stok INT
        );
    """)
    cursor.execute("INSERT INTO tb_produk (nama_produk, stok) VALUES ('Meja', 20), ('Kursi', 50);")

    # Function untuk mengecek apakah stok cukup untuk dibeli
    cursor.execute("""
        CREATE OR REPLACE FUNCTION cek_ketersediaan_stok(p_id_produk INT, p_jumlah_diminta INT)
        RETURNS BOOLEAN AS $$
        DECLARE
            v_stok_tersedia INT;
        BEGIN
            -- Ambil stok produk masukkan ke variabel lokal
            SELECT stok INTO v_stok_tersedia FROM tb_produk WHERE id = p_id_produk;
            
            -- Logika kondisi
            IF v_stok_tersedia >= p_jumlah_diminta THEN
                RETURN TRUE;
            ELSE
                RETURN FALSE;
            END IF;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Memanggil Function kompleks
    cursor.execute("SELECT cek_ketersediaan_stok(1, 15);") # Meja stok 20, diminta 15 (cukup)
    cukup_1 = cursor.fetchone()[0]
    
    cursor.execute("SELECT cek_ketersediaan_stok(2, 60);") # Kursi stok 50, diminta 60 (tidak cukup)
    cukup_2 = cursor.fetchone()[0]

    print(f"Apakah stok Meja cukup untuk 15 barang? {cukup_1}")
    print(f"Apakah stok Kursi cukup untuk 60 barang? {cukup_2}\n")

    # Cleanup
    cursor.execute("DROP FUNCTION IF EXISTS hitung_perkalian(INT, INT);")
    cursor.execute("DROP FUNCTION IF EXISTS cek_ketersediaan_stok(INT, INT);")
    cursor.execute("DROP TABLE IF EXISTS tb_produk CASCADE;")

    conn.commit()
    cursor.close()
except Exception as e:
    if conn:
        conn.rollback()
    print(f"Output Error: {e}\n")
finally:
    if conn:
        conn.close()
