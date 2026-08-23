import psycopg2
from psycopg2 import pool
import os

# ==============================================================================
# MATERI DASAR POSTGRESQL MENGGUNAKAN PYTHON (PSYCOPG2)
# ==============================================================================

# Konfigurasi Database Sementara (Sesuaikan dengan kredensial Anda)
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "password",
    "host": "127.0.0.1",
    "port": "5432"
}

# ------------------------------------------------------------------------------
# 1. KONEKSI DASAR & EKSEKUSI QUERY
# ------------------------------------------------------------------------------
def materi_1_koneksi_dasar():
    print("\n--- 1. KONEKSI DASAR ---")
    try:
        # Membuat koneksi ke database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Mengeksekusi query sederhana untuk mendapatkan versi PostgreSQL
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"Berhasil terhubung. Versi Database: {db_version[0]}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Gagal koneksi dasar: {e}")

# ------------------------------------------------------------------------------
# 2. CONNECTION POOLING
# ------------------------------------------------------------------------------
# Digunakan untuk me-manage koneksi database yang banyak agar lebih efisien
# dengan menggunakan kembali (reuse) koneksi yang sudah ada.
def materi_2_connection_pooling():
    print("\n--- 2. CONNECTION POOLING ---")
    try:
        # Membuat connection pool dengan minimal 1 dan maksimal 10 koneksi
        connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **DB_CONFIG)
        
        if connection_pool:
            print("Connection pool berhasil dibuat!")
            
            # Mengambil koneksi dari pool
            conn = connection_pool.getconn()
            if conn:
                print("Berhasil mengambil koneksi dari pool.")
                cursor = conn.cursor()
                cursor.execute("SELECT current_date;")
                print(f"Tanggal hari ini dari DB: {cursor.fetchone()[0]}")
                
                cursor.close()
                
                # Mengembalikan koneksi ke dalam pool agar bisa digunakan kembali
                connection_pool.putconn(conn)
                print("Koneksi dikembalikan ke pool.")
                
            # Menutup semua koneksi di pool (biasanya dipanggil saat aplikasi mati)
            connection_pool.closeall()
            print("Semua koneksi di pool ditutup.")
    except Exception as e:
        print(f"Error pada connection pooling: {e}")

# ------------------------------------------------------------------------------
# 3. GET POSTGRESQL PROCESS ID (PID)
# ------------------------------------------------------------------------------
# Mengetahui Process ID (PID) dari backend PostgreSQL yang melayani koneksi kita saat ini.
# Berguna untuk debugging atau monitoring (seperti melihat pg_stat_activity).
def materi_3_pg_backend_pid():
    print("\n--- 3. MENDAPATKAN POSTGRES PROCESS ID (PID) ---")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Mengambil PID dari sesi PostgreSQL saat ini
        cursor.execute("SELECT pg_backend_pid();")
        backend_pid = cursor.fetchone()[0]
        
        print(f"PostgreSQL Backend Process ID untuk koneksi ini adalah: {backend_pid}")
        
        # Bisa juga dibandingkan dengan process ID Python aplikasi kita (walau berbeda environment)
        print(f"Sebagai perbandingan, Python App PID kita adalah: {os.getpid()}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error mendapatkan PID: {e}")

# ------------------------------------------------------------------------------
# 4. TRANSAKSI (COMMIT & ROLLBACK)
# ------------------------------------------------------------------------------
# Memastikan konsistensi data. Jika semua berhasil maka COMMIT, jika ada error maka ROLLBACK.
def materi_4_transaksi():
    print("\n--- 4. TRANSAKSI (COMMIT & ROLLBACK) ---")
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Memulai block query untuk membuat tabel (hanya contoh)
        print("Mencoba membuat tabel dummy...")
        cursor.execute("CREATE TABLE IF NOT EXISTS contoh_transaksi (id SERIAL PRIMARY KEY, nama VARCHAR(50));")
        
        print("Memasukkan data dummy...")
        cursor.execute("INSERT INTO contoh_transaksi (nama) VALUES ('Test User');")
        
        # Menyimpan perubahan secara permanen (Commit)
        conn.commit()
        print("Transaksi berhasil di-commit!")
        
        # Cleanup (Optional)
        cursor.execute("DROP TABLE contoh_transaksi;")
        conn.commit()
        
        cursor.close()
    except Exception as e:
        # Jika terjadi error di tengah-tengah query, kita batalkan semua perubahan (Rollback)
        if conn:
            conn.rollback()
        print(f"Terjadi error, transaksi dibatalkan (Rollback). Error: {e}")
    finally:
        if conn:
            conn.close()

# ------------------------------------------------------------------------------
# 5. ERROR HANDLING SPESIFIK POSTGRESQL (PSYCOPG2)
# ------------------------------------------------------------------------------
# Menangani error database secara spesifik, bukan sekedar Exception umum.
def materi_5_error_handling():
    print("\n--- 5. ERROR HANDLING SPESIFIK POSTGRESQL ---")
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Mencoba query error dengan sengaja (tabel tidak ada)
        print("Mengeksekusi query yang sengaja salah...")
        cursor.execute("SELECT * FROM tabel_yang_tidak_pernah_ada;")
        
    except psycopg2.OperationalError as e:
        print(f"Operational Error (Misal: server mati, koneksi terputus): {e}")
    except psycopg2.ProgrammingError as e:
        print(f"Programming Error (Misal: sintaks SQL salah, tabel tidak ada): {e}")
    except psycopg2.Error as e:
        print(f"Error umum Database PostgreSQL: {e}")
    except Exception as e:
        print(f"Error dari sistem Python: {e}")
    finally:
        if conn:
            conn.rollback()
            conn.close()

# ==============================================================================
# JALANKAN SEMUA MATERI
# ==============================================================================
if __name__ == "__main__":
    print("=== BELAJAR DASAR POSTGRESQL DENGAN PYTHON ===")
    print("Catatan: Pastikan server PostgreSQL menyala dan DB_CONFIG sudah sesuai.\n")
    
    materi_1_koneksi_dasar()
    materi_2_connection_pooling()
    materi_3_pg_backend_pid()
    materi_4_transaksi()
    materi_5_error_handling()
