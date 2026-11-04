# =============================================================================
# CATATAN BELAJAR PYDANTIC V2
# Terakhir diperbarui: 2026-10-18
# =============================================================================
#
# STATUS PENGUASAAN:
#   ✅ Sudah dipahami dan dikuasai
#   📖 Sudah dipelajari, perlu latihan lebih lanjut
#   ❌ Belum dipelajari
#
# =============================================================================


# =============================================================================
# A. DASAR PYDANTIC ✅
# =============================================================================
#
# Konsep:
# - BaseModel adalah kelas dasar untuk membuat model data di Pydantic.
# - Validasi otomatis berjalan saat instance model dibuat.
# - Menggunakan type hints (str, int, float, bool, dll.) sebagai deklarasi tipe.
# - Pydantic melakukan type coercion (konversi tipe) jika memungkinkan,
#   contoh: "25" (string) bisa dikonversi ke int jika field bertipe int.

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator,
    field_validator,
    ValidationError,
    AliasPath,
    AliasChoices,
)
from typing import Optional, Any
from enum import Enum


# Contoh dasar BaseModel
class UserDasar(BaseModel):
    nama: str
    umur: int


# Saat dibuat, validasi otomatis berjalan:
# user = UserDasar(nama="Budi", umur="25")  # "25" dikonversi ke int -> OK
# user = UserDasar(nama=123, umur=25)        # 123 dikonversi ke str "123" -> OK
# user = UserDasar(nama="Budi", umur="abc") # ERROR: "abc" tidak bisa jadi int


# =============================================================================
# PANDUAN LENGKAP PARAMETER ConfigDict (PYDANTIC V2) 📖
# =============================================================================
#
# Konsep:
# Di Pydantic V2, konfigurasi model tidak lagi memakai class Config: (seperti V1),
# melainkan menggunakan atribut kelas:
#     model_config = ConfigDict(...)
#
# DAFTAR PARAMETER ConfigDict & PENJELASANNYA:
#
# 1. extra ('ignore' | 'forbid' | 'allow')
#    - Menentukan perlakuan terhadap field ekstra/tak terdaftar yang dikirimkan.
#    - 'ignore' (default): field tambahan diabaikan tanpa error.
#    - 'forbid': tolak dan lemparkan ValidationError jika ada field tambahan.
#    - 'allow' : terima field tambahan dan simpan di model.model_extra.
#
# 2. str_strip_whitespace (bool, default False)
#    - Jika True, otomatis memotong spasi depan/belakang (.strip()) pada SEMUA field string.
#
# 3. str_to_lower / str_to_upper (bool, default False)
#    - Jika True, otomatis mengubah semua field string menjadi huruf kecil (lowercase)
#      atau huruf besar (uppercase).
#
# 4. str_min_length / str_max_length (int, default None)
#    - Menetapkan batas panjang minimum atau maksimum karakter secara global untuk semua field string.
#
# 5. strict (bool, default False)
#    - Jika True, mematikan type coercion (konversi tipe otomatis) untuk seluruh field di model.
#    - Contoh: nilai string "123" tidak akan dikonversi ke int, melainkan langsung error.
#
# 6. frozen (bool, default False)
#    - Jika True, membuat instance model bersifat immutable (read-only setelah dibuat).
#    - Model yang frozen juga otomatis hashable sehingga bisa dijadikan elemen set atau key dict.
#
# 7. validate_assignment (bool, default False)
#    - Secara default, Pydantic hanya memvalidasi nilai saat model pertama kali diinisialisasi.
#    - Jika True, validasi akan kembali dijalankan saat atribut diubah (misal: user.umur = -10).
#
# 8. populate_by_name (bool, default False)
#    - Jika field memiliki alias (misal Field(alias="user_name")), secara default hanya
#      bisa diisi via nama aliasnya.
#    - Jika populate_by_name=True, field bisa diisi baik menggunakan nama alias ('user_name')
#      maupun nama atribut Python aslinya ('username').
#
# 9. from_attributes (bool, default False) - [Pengganti orm_mode=True di V1]
#    - Mengizinkan Pydantic membaca data dari atribut objek (obj.nama) bukan hanya dict (obj['nama']).
#    - Sangat penting saat integrasi dengan ORM seperti SQLAlchemy, Django ORM, atau class Python biasa
#      melalui Model.model_validate(obj_orm).
#
# 10. use_enum_values (bool, default False)
#     - Jika True, model akan menyimpan nilai mentah (.value) dari Enum, bukan objek Enum itu sendiri.
#
# 11. validate_default (bool, default False)
#     - Jika True, nilai default field juga akan divalidasi oleh validator saat inisialisasi.
#
# 12. arbitrary_types_allowed (bool, default False)
#     - Mengizinkan field menggunakan tipe data/class kustom yang tidak memiliki validator bawaan Pydantic
#       (misal koneksi database, class pihak ketiga, dll).
#
# 13. hide_input_in_errors (bool, default False)
#     - Menyembunyikan input data asli dari pesan ValidationError.
#     - Sangat penting untuk field sensitif seperti kata sandi, token API, atau data pribadi (PII).
#
# 14. loc_by_alias (bool, default True)
#     - Menentukan penamaan field di dalam pesan error loc.
#     - Jika True, menggunakan nama alias. Jika False, menggunakan nama atribut Python.
#
# 15. revalidate_instances ('always' | 'never' | 'subclass-instances', default 'never')
#     - Mengatur apakah instance model yang sudah divalidasi akan divalidasi ulang jika
#       dioper ke model lain.
#
# -----------------------------------------------------------------------------
# CONTOH PENGGUNAAN PARAMETER ConfigDict:
# -----------------------------------------------------------------------------

# Contoh A: Pembersihan String Otomatis (str_strip_whitespace, str_to_lower)
class ModelStringOtomatis(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, str_to_lower=True)
    username: str
    email: str

# Contoh B: Proteksi Immutabilitas (frozen)
class KoordinatImmutable(BaseModel):
    model_config = ConfigDict(frozen=True)
    x: int
    y: int

# Contoh C: Validasi saat Modifikasi Nilai (validate_assignment)
class RekeningBank(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    saldo: int = Field(ge=0)

# Contoh D: Fleksibilitas Input & ORM (populate_by_name & from_attributes)
class UserORM(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    user_id: int = Field(alias="userId")
    nama: str

# Contoh E: Keamanan Data Sensitif (hide_input_in_errors)
class AkunKeamanan(BaseModel):
    model_config = ConfigDict(hide_input_in_errors=True)
    password: str = Field(min_length=8)

# Contoh F: Enum Value & Tipe Kustom (use_enum_values, arbitrary_types_allowed)
class Level(str, Enum):
    ADMIN = "admin"
    GUEST = "guest"

class DatabaseDummy:
    """Kelas kustom non-Pydantic."""
    def __init__(self, host: str):
        self.host = host

class KonfigurasiApp(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        arbitrary_types_allowed=True
    )
    role: Level
    koneksi_db: DatabaseDummy


# =============================================================================
# DEMO IMPLEMENTASI ConfigDict (Dapat Dijalankan)
# =============================================================================
print("\n=== DEMO ConfigDict: str_strip_whitespace & str_to_lower ===")
data_user = ModelStringOtomatis(username="  BudiSantoso  ", email="  BUDI@EXAMPLE.COM  ")
print(f"Hasil normalisasi -> username: '{data_user.username}', email: '{data_user.email}'")

print("\n=== DEMO ConfigDict: frozen=True ===")
titik = KoordinatImmutable(x=10, y=20)
try:
    titik.x = 99  # Mencoba mengubah nilai pada model frozen
except ValidationError as exc:
    print(f"Berhasil dicegah (Frozen): {exc.errors()[0]['type']}")

print("\n=== DEMO ConfigDict: validate_assignment=True ===")
akun = RekeningBank(saldo=100000)
try:
    akun.saldo = -50000  # Tidak lolos validasi ge=0 saat reassignment
except ValidationError as exc:
    print(f"Berhasil dicegah saat ubah nilai: {exc.errors()[0]['msg']}")

print("\n=== DEMO ConfigDict: populate_by_name=True ===")
# Bisa dibuat pakai alias ("userId") atau nama field asli ("user_id"):
user1 = UserORM(userId=1, nama="Andi")
user2 = UserORM(user_id=2, nama="Budi")
print(f"Dari alias : {user1}")
print(f"Dari field : {user2}")

print("\n=== DEMO ConfigDict: hide_input_in_errors=True ===")
try:
    AkunKeamanan(password="123")  # Password terlalu pendek
except ValidationError as exc:
    # Pada str(exc), input_value dan input_type disembunyikan sehingga aman dari log/traceback:
    print("Pesan ValidationError (tanpa input_value):")
    print(str(exc))

print("\n=== DEMO ConfigDict: use_enum_values & arbitrary_types_allowed ===")
app_config = KonfigurasiApp(
    role=Level.ADMIN,
    koneksi_db=DatabaseDummy(host="localhost:5432")
)
print(f"Role (raw string): {app_config.role} (tipe: {type(app_config.role).__name__})")
print(f"Arbitrary class host: {app_config.koneksi_db.host}")


# =============================================================================
# B. VALIDASI FIELD DENGAN Field() ✅
# =============================================================================
#
# Konsep:
# - Field() digunakan untuk menambahkan aturan validasi lebih lanjut pada field.
# - Parameter yang sudah dipelajari:
#     min_length  -> panjang minimum string
#     max_length  -> panjang maksimum string
#     gt          -> greater than (lebih besar dari, tidak termasuk nilai itu)
#     lt          -> less than (lebih kecil dari, tidak termasuk nilai itu)
#
# Catatan tambahan (belum dipraktikkan):
#     ge          -> greater than or equal (>=)
#     le          -> less than or equal (<=)
#     pattern     -> regex pattern untuk validasi string


class User(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    umur: int = Field(gt=18)
    # umur harus > 18 (19 ke atas), bukan >= 18


# Contoh:
# User(username="ab", umur=20)    # ERROR: username terlalu pendek
# User(username="budi", umur=18)  # ERROR: umur harus > 18, bukan >= 18
# User(username="budi", umur=19)  # OK


# =============================================================================
# C. FIELD WAJIB, NULLABLE, DAN DEFAULT ✅
# =============================================================================
#
# Konsep:
# - Field WAJIB     : tidak ada default value dan tidak boleh None
# - Field NULLABLE  : boleh bernilai None, menggunakan Optional[tipe]
# - Field DEFAULT   : memiliki nilai bawaan jika tidak diisi
#
# ⚠️  PENTING: Nullable TIDAK sama dengan optional!
#     Optional[str] artinya nilainya boleh None, TAPI fieldnya tetap harus ada
#     (kecuali dikombinasikan dengan default=None).

class ContohField(BaseModel):
    # Field wajib: harus selalu diisi
    nama: str

    # Field nullable + default None: boleh diisi None atau dihilangkan
    email: Optional[str] = None

    # Field dengan default value
    aktif: bool = True

    # Field nullable TAPI wajib ada (harus eksplisit diisi, bahkan jika None)
    # Ini jarang digunakan tapi penting dipahami:
    # catatan: Optional[str]  <- tanpa default, field ini WAJIB ada (bisa berisi None)


# Contoh:
# ContohField(nama="Budi")                          # OK: email=None, aktif=True
# ContohField(nama="Budi", email=None, aktif=False) # OK
# ContohField()                                      # ERROR: nama wajib ada


# =============================================================================
# D. PENANGANAN ValidationError ✅
# =============================================================================
#
# Konsep:
# - Jika validasi gagal, Pydantic melempar ValidationError.
# - Gunakan try-except untuk menangkapnya.
# - exc.errors() mengembalikan list of dict, setiap dict berisi info 1 error.
#
# Struktur setiap error dict:
#   {
#     "type": str,   -> kode error (contoh: "string_too_short", "greater_than")
#     "loc": tuple,  -> lokasi field yang error (contoh: ("username",))
#     "msg": str,    -> pesan error default dari Pydantic
#     "input": any,  -> nilai yang dikirim user
#     "ctx": dict,   -> konteks tambahan (contoh: {"min_length": 3})
#   }
#
# ⚠️  PERHATIAN: Kode "type" bisa BERBEDA antara Pydantic V1 dan V2!
#     V1: "value_error.any_str.min_length"
#     V2: "string_too_short"
#     Selalu cek dokumentasi Pydantic V2 saat debug.

try:
    User(username="ab", umur=17)
except ValidationError as exc:
    print("=== Contoh exc.errors() ===")
    for error in exc.errors():
        print(f"  Field   : {error['loc']}")
        print(f"  Tipe    : {error['type']}")
        print(f"  Pesan   : {error['msg']}")
        print(f"  Input   : {error['input']}")
        print(f"  Konteks : {error.get('ctx')}")
        print()


# =============================================================================
# E. MEMBUAT PESAN ERROR KUSTOM ✅
# =============================================================================
#
# Konsep:
# - Buat dictionary ERROR_MESSAGES dengan key berupa tuple (field, error_type).
# - Gunakan .get() dengan pesan fallback jika key tidak ditemukan.
# - Buat fungsi format_validation_errors() yang menerima ValidationError.
# - Fungsi mengembalikan dict (cocok untuk respons API), bukan print.
# - PENTING: "return" harus di luar loop agar semua error terkumpul dulu.

ERROR_MESSAGES = {
    ("username", "string_too_short"): "Username minimal 3 karakter.",
    ("username", "string_too_long"): "Username maksimal 20 karakter.",
    ("username", "missing"): "Username wajib diisi.",
    ("umur", "greater_than"): "Umur harus lebih dari 18 tahun.",
    ("umur", "missing"): "Umur wajib diisi.",
}


def format_validation_errors(exc: ValidationError) -> dict:
    """
    Mengubah ValidationError menjadi dict respons API yang ramah pengguna.
    Mengembalikan dict, BUKAN langsung print.
    """
    errors = {}

    for error in exc.errors():
        # loc adalah tuple, ambil elemen pertama sebagai nama field
        field = error["loc"][0] if error["loc"] else "general"
        error_type = error["type"]

        # Coba ambil pesan kustom, fallback ke pesan default Pydantic
        pesan = ERROR_MESSAGES.get(
            (field, error_type),
            error["msg"]  # fallback: pesan default Pydantic
        )

        errors[field] = pesan

    # ⚠️ return ADA DI LUAR LOOP agar semua error dikumpulkan dulu
    return {
        "status": "error",
        "errors": errors
    }


# Contoh penggunaan:
try:
    User(username="ab", umur=17)
except ValidationError as exc:
    respons = format_validation_errors(exc)
    print("=== Respons API Error Kustom ===")
    print(respons)
    # Output: {'status': 'error', 'errors': {'username': 'Username minimal 3 karakter.', 'umur': 'Umur harus lebih dari 18 tahun.'}}


# =============================================================================
# F. VALIDASI INPUT vs BUSINESS LOGIC ✅
# =============================================================================
#
# Konsep: Pisahkan tanggung jawab validasi dengan jelas.
#
# Tanggung jawab PYDANTIC (validasi input/format):
#   - Tipe data sudah benar? (str, int, dll.)
#   - Panjang string sesuai batas?
#   - Nilai numerik dalam rentang yang diizinkan?
#   - Field wajib sudah diisi?
#
# Tanggung jawab SERVICE / BUSINESS LOGIC (aturan bisnis):
#   - Apakah username sudah digunakan orang lain? (cek ke database)
#   - Apakah saldo cukup untuk transaksi?
#   - Apakah promo masih berlaku?
#   - Apakah user punya izin untuk aksi ini?
#
# Tanggung jawab DATABASE:
#   - Integritas data (foreign key, unique constraint)
#   - Konsistensi transaksi (ACID)

# Contoh pemisahan:

class TransaksiInput(BaseModel):
    """Model untuk validasi INPUT transaksi (tanggung jawab Pydantic)."""
    jumlah: int = Field(gt=0, description="Jumlah transfer harus > 0")
    rekening_tujuan: str = Field(min_length=10, max_length=16)


def proses_transfer(data: TransaksiInput, saldo_pengirim: int) -> dict:
    """
    Service layer: menangani business logic setelah input valid.
    Pydantic sudah memastikan format benar, service memastikan logika bisnis.
    """
    # Business logic: cek saldo (bukan tugas Pydantic!)
    if data.jumlah > saldo_pengirim:
        return {"status": "error", "message": "Saldo tidak mencukupi."}

    # Lanjutkan proses transfer ke database...
    return {"status": "success", "message": f"Transfer {data.jumlah} berhasil."}


# =============================================================================
# G. PENGENALAN model_validator 📖
# (Sudah dipelajari konsepnya, BELUM sepenuhnya dikuasai)
# =============================================================================
#
# Konsep:
# - model_validator adalah decorator untuk validasi yang melibatkan
#   BANYAK FIELD sekaligus (cross-field validation).
# - Berbeda dengan Field() yang hanya untuk 1 field.
#
# Tiga mode yang tersedia:
#
#   mode='before'  -> Berjalan SEBELUM validasi field dimulai.
#                     Menerima data mentah (dict/raw input).
#                     Cocok untuk: normalisasi data, rename key, preprocessing.
#                     Harus mengembalikan data (dict) yang sudah dimodifikasi.
#
#   mode='after'   -> Berjalan SETELAH semua field berhasil divalidasi.
#                     Menerima instance model (self) yang sudah terbentuk.
#                     Cocok untuk: cek hubungan antarfield (misal: password match).
#                     HARUS mengembalikan self jika validasi berhasil.
#
#   mode='wrap'    -> Membungkus seluruh proses validasi.
#                     Lebih kompleks, jarang digunakan untuk kasus umum.
#                     (belum dipelajari lebih lanjut)
#
# ⚠️  PENTING:
#     - Jika validator gagal, lempar ValueError -> Pydantic ubah jadi ValidationError.
#     - Validator "after" WAJIB mengembalikan self.

class UserRegistrasi(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=8)
    password_confirmation: str

    # --- Contoh mode='after' ---
    # Berjalan setelah semua field valid. Memeriksa hubungan antarfield.
    @model_validator(mode='after')
    def cek_password_cocok(self) -> 'UserRegistrasi':
        """Memastikan password dan password_confirmation sama."""
        if self.password != self.password_confirmation:
            raise ValueError("Password dan konfirmasi password tidak cocok.")
        # WAJIB kembalikan self jika berhasil
        return self


# Contoh penggunaan:
print("\n=== Contoh model_validator mode='after' ===")

# Kasus 1: password cocok -> OK
try:
    user_ok = UserRegistrasi(
        username="budi123",
        password="rahasia99",
        password_confirmation="rahasia99"
    )
    print(f"Registrasi berhasil: {user_ok.username}")
except ValidationError as exc:
    print(f"Error: {exc}")

# Kasus 2: password tidak cocok -> ValidationError
try:
    user_gagal = UserRegistrasi(
        username="bangladesh",
        password="rahasia99",
        password_confirmation="salah123"
    )
except ValidationError as exc:
    print(f"Registrasi gagal: {exc.errors()}")


# --- Contoh mode='before' ---
# Berjalan sebelum validasi field. Menerima data mentah, mengembalikan dict baru.

class UserNormalisasi(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: str

    @model_validator(mode='before')
    @classmethod
    def normalisasi_input(cls, data: dict) -> dict:
        """Normalisasi data sebelum validasi: trim spasi & lowercase email."""
        if isinstance(data, dict):
            if "username" in data and isinstance(data["username"], str):
                data["username"] = data["username"].strip()
            if "email" in data and isinstance(data["email"], str):
                data["email"] = data["email"].strip().lower()
        return data  # WAJIB kembalikan data (dict)


# Contoh:
print("\n=== Contoh model_validator mode='before' ===")
user_norm = UserNormalisasi(username="  Budi  ", email="  BUDI@EXAMPLE.COM  ")
print(f"Username: '{user_norm.username}'")  # 'Budi' (spasi dihapus)
print(f"Email: '{user_norm.email}'")        # 'budi@example.com' (lowercase)


# =============================================================================
# H. SERIALISASI: model_dump() DAN model_dump_json() ✅
# =============================================================================
#
# Konsep:
# - Serialisasi = mengubah object model menjadi format lain (dict / JSON string).
# - model_dump()      -> mengubah model menjadi Python dict
# - model_dump_json() -> mengubah model menjadi JSON string (bytes-safe)
#
# Parameter penting pada model_dump():
#   include   -> set field yang INGIN disertakan (whitelist)
#   exclude   -> set field yang INGIN dikecualikan (blacklist)
#   by_alias  -> gunakan alias field (jika ada) sebagai key dict
#   exclude_none  -> hapus field yang bernilai None dari output
#   exclude_unset -> hapus field yang tidak diisi saat pembuatan (pakai default)
#
# Catatan:
# - model_dump_json() menerima parameter yang SAMA dengan model_dump().
# - Hasilnya adalah string JSON, bukan dict.
# - Berguna untuk kirim data ke API, simpan ke file, atau logging.

class Produk(BaseModel):
    id: int
    nama: str
    harga: float
    stok: Optional[int] = None
    catatan: Optional[str] = None


produk = Produk(id=1, nama="Laptop", harga=15000000.0, stok=10)

print("\n=== model_dump() ===")
# Dasar: semua field
print(produk.model_dump())
# Output: {'id': 1, 'nama': 'Laptop', 'harga': 15000000.0, 'stok': 10, 'catatan': None}

# Hanya field tertentu (include)
print(produk.model_dump(include={"id", "nama", "harga"}))
# Output: {'id': 1, 'nama': 'Laptop', 'harga': 15000000.0}

# Kecualikan field tertentu (exclude)
print(produk.model_dump(exclude={"catatan"}))
# Output: {'id': 1, 'nama': 'Laptop', 'harga': 15000000.0, 'stok': 10}

# Hapus field yang bernilai None (exclude_none)
print(produk.model_dump(exclude_none=True))
# Output: {'id': 1, 'nama': 'Laptop', 'harga': 15000000.0, 'stok': 10}
# catatan=None tidak muncul karena exclude_none=True

print("\n=== model_dump_json() ===")
# Menghasilkan JSON string
print(produk.model_dump_json())
# Output: '{"id":1,"nama":"Laptop","harga":15000000.0,"stok":10,"catatan":null}'

# Dengan exclude_none
print(produk.model_dump_json(exclude_none=True))
# Output: '{"id":1,"nama":"Laptop","harga":15000000.0,"stok":10}'

# Dengan indentasi (untuk tampilan yang rapi)
print(produk.model_dump_json(indent=2))


# =============================================================================
# I. DESERIALISASI: model_validate() DAN model_validate_json() ✅
# =============================================================================
#
# Konsep:
# - Deserialisasi = mengubah data eksternal (dict / JSON string) menjadi model.
# - model_validate()      -> membuat model dari Python dict
# - model_validate_json() -> membuat model dari JSON string
#
# Perbedaan dengan konstruktor biasa (Model(**data)):
#   - Model(**data)           -> cara umum, menerima keyword arguments
#   - model_validate(dict)    -> cara eksplisit, menerima dict langsung
#   - model_validate_json(str)-> cara dari JSON string, lebih efisien untuk JSON
#
# Kapan pakai model_validate()?
#   - Saat menerima data dari dict yang sudah ada (misal: dari database)
#   - Lebih mudah dibaca ketika data dalam bentuk dict
#
# Kapan pakai model_validate_json()?
#   - Saat menerima JSON dari API eksternal, request body HTTP, atau file JSON
#   - Lebih efisien daripada json.loads() + model_validate() secara terpisah

print("\n=== model_validate() ===")
# Buat model dari dict (misalnya data dari database)
data_dari_db = {"id": 2, "nama": "Mouse", "harga": 250000.0, "stok": 50}
produk_dari_db = Produk.model_validate(data_dari_db)
print(produk_dari_db)
# Output: id=2 nama='Mouse' harga=250000.0 stok=50 catatan=None

# model_validate() tetap melakukan validasi Pydantic
try:
    data_invalid = {"id": "bukan_angka", "nama": "Keyboard", "harga": -100}
    Produk.model_validate(data_invalid)
except ValidationError as exc:
    print(f"Validasi gagal: {exc.errors()}")

print("\n=== model_validate_json() ===")
# Buat model dari JSON string (misalnya dari request API)
json_string = '{"id": 3, "nama": "Headphone", "harga": 500000.0, "stok": 25}'
produk_dari_json = Produk.model_validate_json(json_string)
print(produk_dari_json)
# Output: id=3 nama='Headphone' harga=500000.0 stok=25 catatan=None

# model_validate_json() juga melakukan validasi
try:
    json_invalid = '{"id": 4, "nama": 123, "harga": "mahal"}'
    Produk.model_validate_json(json_invalid)
except ValidationError as exc:
    print(f"Validasi JSON gagal: {exc.errors()}")


# Contoh alur lengkap: model -> JSON -> model (round-trip)
print("\n=== Round-trip: model -> JSON -> model ===")
produk_awal = Produk(id=5, nama="Webcam", harga=750000.0)
json_hasil = produk_awal.model_dump_json(exclude_none=True)
print(f"JSON: {json_hasil}")
produk_kembali = Produk.model_validate_json(json_hasil)
print(f"Model kembali: {produk_kembali}")


# =============================================================================
# J. KONFIGURASI EXTRA: ignore, forbid, allow ✅
# =============================================================================
#
# Konsep:
# - Secara default, Pydantic V2 akan MENGABAIKAN field yang tidak didefinisikan
#   di model (extra fields).
# - Perilaku ini bisa dikustomisasi menggunakan model_config dengan extra=...
#
# Tiga nilai untuk extra:
#
#   extra='ignore'  (DEFAULT)
#     -> Field ekstra diabaikan diam-diam, tidak disimpan, tidak error.
#     -> Cocok untuk: API yang mungkin mengirim field tambahan yang tidak relevan.
#
#   extra='forbid'
#     -> Field ekstra akan menyebabkan ValidationError.
#     -> Cocok untuk: API yang ingin memastikan tidak ada field tidak dikenal
#        (mencegah typo atau data berbahaya).
#
#   extra='allow'
#     -> Field ekstra diterima dan DISIMPAN dalam model.
#     -> Bisa diakses via model.model_extra atau model.__pydantic_extra__
#     -> Cocok untuk: schema yang fleksibel / dinamis.
#
# Cara menggunakannya: gunakan model_config dari pydantic

from pydantic import ConfigDict


# --- Contoh extra='ignore' (perilaku default) ---
class ModelIgnore(BaseModel):
    model_config = ConfigDict(extra='ignore')
    nama: str
    umur: int


print("\n=== extra='ignore' ===")
obj_ignore = ModelIgnore(nama="Budi", umur=25, field_ekstra="diabaikan")
print(obj_ignore)
# Output: nama='Budi' umur=25
# field_ekstra tidak ada di model, tidak error


# --- Contoh extra='forbid' ---
class ModelForbid(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nama: str
    umur: int


print("\n=== extra='forbid' ===")
try:
    obj_forbid = ModelForbid(nama="Budi", umur=25, field_ekstra="dilarang")
except ValidationError as exc:
    print(f"Error: {exc.errors()}")
    # Output: error karena field_ekstra tidak diizinkan

# Tanpa field ekstra -> OK
obj_forbid_ok = ModelForbid(nama="Ani", umur=30)
print(f"OK: {obj_forbid_ok}")


# --- Contoh extra='allow' ---
class ModelAllow(BaseModel):
    model_config = ConfigDict(extra='allow')
    nama: str
    umur: int


print("\n=== extra='allow' ===")
obj_allow = ModelAllow(nama="Budi", umur=25, hobi="coding", kota="Jakarta")
print(obj_allow)
# Output: nama='Budi' umur=25 hobi='coding' kota='Jakarta'

# Akses field ekstra via model_extra
print(f"Field ekstra: {obj_allow.model_extra}")
# Output: {'hobi': 'coding', 'kota': 'Jakarta'}

# Field ekstra juga ikut saat di-dump
print(f"model_dump(): {obj_allow.model_dump()}")
# Output: {'nama': 'Budi', 'umur': 25, 'hobi': 'coding', 'kota': 'Jakarta'}


# =============================================================================
# K. FIELD VALIDATOR (field_validator) ✅
# =============================================================================
#
# Konsep:
# - field_validator adalah decorator untuk validasi custom pada SATU field tertentu.
# - Berbeda dengan Field() yang hanya bisa mengatur batasan bawaan Pydantic
#   (min_length, gt, dll.), field_validator memungkinkan logika validasi BEBAS.
# - Berguna saat perlu: format string, cek regex, konversi data, atau aturan
#   bisnis sederhana yang spesifik untuk satu field.
#
# Sintaks dasar:
#   @field_validator('nama_field')
#   @classmethod
#   def nama_validator(cls, value):
#       # logika validasi...
#       return value  # WAJIB kembalikan value jika valid
#
# Dua mode utama:
#
#   mode='before'
#     -> Berjalan SEBELUM validasi tipe Pydantic.
#     -> Menerima nilai mentah (raw input), cocok untuk normalisasi/konversi.
#     -> Wajib kembalikan value yang sudah dimodifikasi.
#
#   mode='after'  (DEFAULT di Pydantic V2)
#     -> Berjalan SETELAH validasi tipe Pydantic berhasil.
#     -> Menerima nilai yang sudah dikonversi ke tipe yang benar.
#     -> Wajib kembalikan value.
#
# ⚠️  PENTING:
#     - Harus pakai @classmethod.
#     - Jika validasi gagal, lempar ValueError -> Pydantic ubah jadi ValidationError.
#     - Bisa memvalidasi beberapa field sekaligus: @field_validator('field1', 'field2')


# --- Contoh 1: Normalisasi string (mode='before') ---
# Gunakan mode='before' saat ingin mengubah/normalisasi nilai SEBELUM dicek tipenya.

class UserBersih(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: str

    @field_validator('username', mode='before')
    @classmethod
    def bersihkan_username(cls, value):
        """Hapus spasi di awal/akhir username sebelum validasi."""
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator('email', mode='before')
    @classmethod
    def normalisasi_email(cls, value):
        """Trim spasi dan ubah email ke lowercase."""
        if isinstance(value, str):
            return value.strip().lower()
        return value


print("\n=== field_validator mode='before': Normalisasi ===")
user_bersih = UserBersih(username="  Budi  ", email="  BUDI@EXAMPLE.COM  ")
print(f"Username : '{user_bersih.username}'")  # 'Budi' (spasi dihapus)
print(f"Email    : '{user_bersih.email}'")     # 'budi@example.com'


# --- Contoh 2: Validasi format (mode='after') ---
# Gunakan mode='after' saat ingin memvalidasi nilai yang sudah bertipe benar.

import re

class UserTerdaftar(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: str
    no_hp: str

    @field_validator('email', mode='after')
    @classmethod
    def validasi_email(cls, value):
        """Pastikan email memiliki format yang benar (ada @ dan domain)."""
        pola_email = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
        if not re.match(pola_email, value):
            raise ValueError("Format email tidak valid.")
        return value

    @field_validator('no_hp', mode='after')
    @classmethod
    def validasi_no_hp(cls, value):
        """Pastikan nomor HP hanya berisi angka dan dimulai dengan 08 atau +62."""
        # Hapus spasi dan tanda hubung dulu
        value = value.replace(" ", "").replace("-", "")
        if not re.match(r'^(08|\+62)\d{8,11}$', value):
            raise ValueError("Nomor HP tidak valid. Gunakan format 08xx atau +62xx.")
        return value


print("\n=== field_validator mode='after': Validasi Format ===")

# Kasus 1: Semua valid -> OK
try:
    user_ok = UserTerdaftar(
        username="budi123",
        email="budi@example.com",
        no_hp="08123456789"
    )
    print(f"Berhasil: {user_ok.username}, {user_ok.email}, {user_ok.no_hp}")
except ValidationError as exc:
    print(f"Error: {exc}")

# Kasus 2: Email tidak valid -> ValidationError
try:
    UserTerdaftar(username="ani", email="bukan-email", no_hp="08123456789")
except ValidationError as exc:
    for err in exc.errors():
        print(f"Error [{err['loc'][0]}]: {err['msg']}")

# Kasus 3: Nomor HP tidak valid -> ValidationError
try:
    UserTerdaftar(username="cici", email="cici@mail.com", no_hp="12345")
except ValidationError as exc:
    for err in exc.errors():
        print(f"Error [{err['loc'][0]}]: {err['msg']}")


# --- Contoh 3: Memvalidasi beberapa field sekaligus ---
# Satu validator bisa menangani beberapa field dengan menyebutkannya semua.

class FormulirKontak(BaseModel):
    nama_depan: str
    nama_belakang: str

    @field_validator('nama_depan', 'nama_belakang', mode='before')
    @classmethod
    def bersihkan_dan_kapitalisasi(cls, value):
        """Trim spasi dan kapitalisasi setiap nama."""
        if isinstance(value, str):
            return value.strip().title()
        return value


print("\n=== field_validator untuk beberapa field ===")
kontak = FormulirKontak(nama_depan="  budi  ", nama_belakang="  santoso  ")
print(f"Nama lengkap: {kontak.nama_depan} {kontak.nama_belakang}")
# Output: Nama lengkap: Budi Santoso


# --- Perbandingan: kapan pakai Field() vs field_validator? ---
#
# Gunakan Field() ketika:
#   - Batasan sederhana: panjang string, rentang angka (gt, lt, ge, le)
#   - Aturan bawaan Pydantic sudah cukup
#   Contoh: umur: int = Field(gt=0, lt=120)
#
# Gunakan field_validator ketika:
#   - Perlu logika Python bebas (regex, konversi, kondisi kompleks)
#   - Perlu normalisasi (strip, lowercase, title case, dll.)
#   - Aturan bawaan Field() tidak cukup
#   Contoh: validasi format email, nomor telepon, NIK, kode pos, dll.
#
# Kedua bisa DIKOMBINASIKAN pada field yang sama:
#   email: str = Field(min_length=5)   <- cek panjang dulu via Field()
#   @field_validator('email') ...      <- cek format via validator


# =============================================================================
# L. ALIAS ✅
# =============================================================================
#
# Konsep:
# - Alias adalah nama alternatif untuk sebuah field.
# - Berguna ketika nama field di input/JSON berbeda dengan nama atribut Python
#   (misalnya format camelCase dari API JavaScript ke snake_case di Python).
#
# Ada 3 jenis alias di Pydantic V2:
#   1. validation_alias : nama alias saat validasi / deserialisasi (input)
#   2. serialization_alias: nama alias saat dump / serialisasi (output)
#   3. alias : mengatur validation_alias sekaligus serialization_alias
#
# Pengaturan penting:
#   - Secara default jika alias diset, saat inisialisasi WAJIB menggunakan alias.
#   - Gunakan ConfigDict(populate_by_name=True) agar field bisa diisi baik
#     menggunakan nama field asli di Python maupun nama aliasnya!
#   - Saat dump: model_dump(by_alias=True) untuk menggunakan alias pada output.

class UserProfile(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # Menggunakan alias biasa (berlaku untuk input & output)
    user_id: int = Field(alias="userId")
    nama_lengkap: str = Field(alias="fullName")
    # serialization_alias: saat validasi input pakai 'email_address', saat dump pakai 'email'
    email_kontak: str = Field(validation_alias="email_address", serialization_alias="email")

print("\n=== L. ALIAS ===")
# 1. Inisialisasi menggunakan alias (misal data dari JSON API eksternal)
data_eksternal = {
    "userId": 101,
    "fullName": "Ahmad Dani",
    "email_address": "ahmad@example.com"
}
user1 = UserProfile.model_validate(data_eksternal)
print("Model dari alias:", user1)
print("Akses atribut Python:", user1.user_id, "|", user1.nama_lengkap)

# 2. Karena populate_by_name=True, bisa juga pakai nama atribut Python langsung:
user2 = UserProfile(user_id=102, nama_lengkap="Budi Santoso", email_address="budi@example.com")
print("Model dari nama Python:", user2)

# 3. Serialisasi / Dump:
print("Dump default (nama atribut):", user1.model_dump())
# Output: {'user_id': 101, 'nama_lengkap': 'Ahmad Dani', 'email_kontak': 'ahmad@example.com'}

print("Dump by_alias=True (nama alias):", user1.model_dump(by_alias=True))
# Output: {'userId': 101, 'fullName': 'Ahmad Dani', 'email': 'ahmad@example.com'}


# =============================================================================
# M. NESTED MODEL (MODEL DI DALAM MODEL) ✅
# =============================================================================
#
# Konsep:
# - Nested model adalah teknik menggunakan BaseModel lain sebagai tipe data suatu field.
# - Pydantic secara rekursif memvalidasi model yang ada di dalamnya.
# - Input bisa berupa dict biasa atau instance model yang sudah dibuat.
# - Sangat berguna untuk data relasional, payload JSON bersarang, struktur objek kompleks.

class Alamat(BaseModel):
    jalan: str
    kota: str
    kode_pos: str = Field(min_length=5, max_length=5)

class RekeningBank(BaseModel):
    nomor_rekening: str = Field(min_length=10, max_length=16)
    nama_bank: str

class Nasabah(BaseModel):
    id_nasabah: int
    nama: str = Field(min_length=3)
    # Nested model di dalam model
    alamat: Alamat
    rekening: RekeningBank

print("\n=== M. NESTED MODEL ===")
payload_nasabah = {
    "id_nasabah": 1,
    "nama": "Citra Lestari",
    # Nested dict otomatis divalidasi dan diubah menjadi instance Alamat
    "alamat": {
        "jalan": "Jl. Sudirman Kav. 21",
        "kota": "Jakarta Pusat",
        "kode_pos": "10220"
    },
    # Nested dict kedua otomatis divalidasi menjadi instance RekeningBank
    "rekening": {
        "nomor_rekening": "123456789012",
        "nama_bank": "BCA"
    }
}

nasabah = Nasabah.model_validate(payload_nasabah)
print("Data Nasabah:", nasabah)
print("Akses nested field:", nasabah.alamat.kota, "| Bank:", nasabah.rekening.nama_bank)

# Jika ada field nested yang tidak valid, error loc akan menunjukkan jalurnya:
try:
    Nasabah.model_validate({
        "id_nasabah": 2,
        "nama": "Doni",
        "alamat": {"jalan": "Jl. Mawar", "kota": "Bandung", "kode_pos": "123"}, # kode_pos < 5
        "rekening": {"nomor_rekening": "1234567890", "nama_bank": "Mandiri"}
    })
except ValidationError as exc:
    print("Contoh loc error nested:")
    for err in exc.errors():
        # Loc akan berisi tuple seperti ('alamat', 'kode_pos')
        print(f"  Field path: {err['loc']} -> {err['msg']}")


# =============================================================================
# N. ALIAS PATH & ALIAS CHOICES ✅
# =============================================================================
#
# Konsep:
# - AliasPath: Digunakan ketika kita ingin mengambil data dari JSON bersarang (nested)
#   tetapi dimasukkan ke dalam field model yang FLAT (tanpa harus buat sub-model).
# - AliasChoices: Menyediakan beberapa pilihan nama alias. Pydantic akan mengambil
#   nilai dari pilihan pertama yang ditemukan di payload input.
#
# Sangat cocok untuk integrasi API pihak ketiga dengan payload berantakan/berubah-ubah.

class DataPegawai(BaseModel):
    # Mengambil nilai dari nested dict: input_data["perusahaan"]["divisi"]["nama"]
    divisi: str = Field(validation_alias=AliasPath("perusahaan", "divisi", "nama"))

    # Fleksibel: terima nama field 'hp', 'phone', atau 'no_telepon'
    kontak: str = Field(validation_alias=AliasChoices("hp", "phone", "no_telepon"))

print("\n=== N. ALIAS PATH & ALIAS CHOICES ===")

# Contoh payload dari sistem eksternal
data_karyawan_a = {
    "perusahaan": {
        "divisi": {
            "nama": "Backend Engineering"
        }
    },
    "phone": "081298765432"
}

pegawai_a = DataPegawai.model_validate(data_karyawan_a)
print("Hasil AliasPath & AliasChoices:")
print(f"  Divisi: {pegawai_a.divisi}")
print(f"  Kontak: {pegawai_a.kontak}")

# Payload lain dengan alias alternatif ('no_telepon'):
data_karyawan_b = {
    "perusahaan": {
        "divisi": {
            "nama": "Data Science"
        }
    },
    "no_telepon": "082111223344"
}
pegawai_b = DataPegawai.model_validate(data_karyawan_b)
print(f"Hasil payload alternatif -> Divisi: {pegawai_b.divisi}, Kontak: {pegawai_b.kontak}")


# =============================================================================
# O. STRICT MODE (strict=True) ✅
# =============================================================================
#
# Konsep:
# - Secara default, Pydantic sangat pemaaf dan melakukan TYPE COERCION:
#   misal: string "123" otomatis jadi int 123, int 1 otomatis jadi bool True,
#          float 42.0 otomatis jadi int 42.
# - Kadang-kadang kita TIDAK INGIN konversi otomatis ini (misal validasi data finansial,
#   token otentikasi, atau tipe data presisi).
# - strict=True mematikan type coercion: tipe data HARUS persis sama!
#
# Penerapan:
# 1. Per-field: Field(strict=True)
# 2. Per-model: model_config = ConfigDict(strict=True)

class PembayaranStrict(BaseModel):
    # Field biasa (coercion diperbolehkan)
    keterangan: str
    
    # Strict per-field: amount harus float/int asli, bukan string "50000"
    amount: float = Field(strict=True, gt=0)
    
    # Strict per-field: status_sukses harus boolean murni (True/False), BUKAN 1, 0, atau "true"
    status_sukses: bool = Field(strict=True)

class TransaksiStrictTotal(BaseModel):
    # Mengaktifkan strict mode untuk SELURUH model
    model_config = ConfigDict(strict=True)

    kode_trx: str
    nominal: int
    is_settled: bool

print("\n=== O. STRICT MODE ===")

# Kasus 1: Input tipe tepat -> Berhasil
bayar_ok = PembayaranStrict(keterangan="Topup", amount=50000.0, status_sukses=True)
print("Strict lolos:", bayar_ok)

# Kasus 2: Coba lakukan coercion pada field strict -> ValidationError!
try:
    PembayaranStrict(
        keterangan="Topup",
        amount="50000.0",   # ERROR: string tidak akan di-coerce ke float
        status_sukses=1     # ERROR: integer 1 tidak akan di-coerce ke bool
    )
except ValidationError as exc:
    print("Contoh kegagalan Strict Mode:")
    for err in exc.errors():
        print(f"  Field {err['loc'][0]}: type={err['type']} | input={err['input']}")


# =============================================================================
# P. BASESETTINGS (pydantic-settings) ✅
# =============================================================================
#
# Konsep:
# - BaseSettings adalah kelas dari library tambahan `pydantic-settings` (install:
#   pip install pydantic-settings) yang digunakan khusus untuk manajemen
#   KONFIGURASI APLIKASI (bukan untuk validasi data request seperti BaseModel).
# - BaseSettings secara otomatis membaca nilai dari:
#     1. Environment variables (variabel lingkungan sistem)
#     2. File .env (dengan SettingsConfigDict)
#     3. Nilai default yang didefinisikan di kelas
# - Cocok digunakan untuk: koneksi database, API key, secret key, host, port, dll.
# - Menggunakan SettingsConfigDict (bukan ConfigDict) untuk konfigurasi khusus settings.
#
# Perbedaan BaseSettings vs BaseModel:
# ┌─────────────────┬─────────────────────────────┬──────────────────────────────┐
# │ Aspek           │ BaseModel                   │ BaseSettings                 │
# ├─────────────────┼─────────────────────────────┼──────────────────────────────┤
# │ Tujuan          │ Validasi data request/respon│ Konfigurasi aplikasi         │
# │ Sumber data     │ Dict / JSON dari input user │ .env, env vars, secrets      │
# │ Import dari     │ pydantic                    │ pydantic_settings            │
# │ Konfigurasi     │ ConfigDict                  │ SettingsConfigDict           │
# │ Contoh pakai    │ Request body API, form data │ DB_HOST, SECRET_KEY, PORT    │
# └─────────────────┴─────────────────────────────┴──────────────────────────────┘
#
# Cara kerja prioritas nilai (dari tertinggi ke terendah):
# 1. Init argument langsung: Settings(db_host="override")
# 2. Environment variable di sistem: export DB_HOST=localhost
# 3. File .env: DB_HOST=localhost
# 4. Default value di kelas: db_host: str = "localhost"
#
# Instalasi:
#   pip install pydantic-settings

from pydantic_settings import BaseSettings, SettingsConfigDict

print("\n=== P. BASESETTINGS ===")


# --- Contoh 1: BaseSettings Dasar ---
# Membaca dari environment variable atau .env

class AppSettings(BaseSettings):
    # Field tanpa default -> WAJIB ada di env atau .env, jika tidak ada -> Error
    app_name: str
    app_version: str

    # Field dengan default -> Opsional, jika tidak ada di env -> pakai default
    debug: bool = False
    max_connections: int = 10

    # SettingsConfigDict: Konfigurasi khusus BaseSettings
    model_config = SettingsConfigDict(
        env_file=".env",           # Path ke file .env (relatif dari direktori kerja)
        env_file_encoding="utf-8", # Encoding file .env
        case_sensitive=False,      # Env var tidak case-sensitive (APP_NAME == app_name)
        extra="ignore",            # Abaikan variabel env yang tidak terdaftar
    )


# --- Contoh 2: Konfigurasi Database (Pola Umum di Project Nyata) ---
# Seperti yang ada di wallet_api/config/settings.py

class DatabaseSettings(BaseSettings):
    db_host: str
    db_port: int = 5432       # Default PostgreSQL port
    db_user: str
    db_password: str
    db_name: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Method tambahan: menghasilkan DATABASE_URL untuk SQLAlchemy
    def get_database_url(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


# --- Contoh 3: env_prefix ---
# env_prefix digunakan ketika semua variabel config di env/file .env
# memiliki awalan (prefix) yang sama.
# Contoh: semua env var diawali "APP_" -> APP_HOST, APP_PORT, APP_SECRET_KEY

class ServerSettings(BaseSettings):
    # Field di kelas menggunakan nama tanpa prefix
    # Tapi env var-nya harus menggunakan prefix: APP_HOST, APP_PORT, dll.
    host: str = "127.0.0.1"
    port: int = 8000
    secret_key: str = "default-secret"
    reload: bool = False

    model_config = SettingsConfigDict(
        env_prefix="APP_",         # Semua env var harus diawali APP_
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# --- Contoh 4: Memuat dan Menggunakan Settings ---
# Pattern singleton yang umum dipakai di project FastAPI/Python nyata

# Simulasi: Set environment variable secara langsung di Python (untuk demo)
import os

# Simulasikan isi .env untuk contoh di bawah
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_USER"] = "admin"
os.environ["DB_PASSWORD"] = "supersecret"
os.environ["DB_NAME"] = "mydb"

# Instansiasi Settings (otomatis baca dari env / .env)
db_settings = DatabaseSettings()

print("Konfigurasi Database:")
print(f"  Host     : {db_settings.db_host}")
print(f"  Port     : {db_settings.db_port}")
print(f"  User     : {db_settings.db_user}")
print(f"  DB Name  : {db_settings.db_name}")
print(f"  Password : {'*' * len(db_settings.db_password)}  (disembunyikan)")
print(f"  DB URL   : {db_settings.get_database_url()}")

# --- Contoh 5: Override nilai saat instansiasi (untuk testing) ---
# Berguna saat unit testing agar tidak tergantung file .env asli

db_test = DatabaseSettings(
    db_host="test-db-host",
    db_port=5433,
    db_user="test_user",
    db_password="test_pass",
    db_name="test_db"
)
print("\nKonfigurasi Database (Test Override):")
print(f"  Host : {db_test.db_host}")
print(f"  DB   : {db_test.db_name}")

# --- Contoh 6: Validasi tipe otomatis (sama seperti BaseModel) ---
# BaseSettings tetap melakukan validasi tipe, termasuk coercion dari string env var

os.environ["APP_HOST"] = "0.0.0.0"
os.environ["APP_PORT"] = "9000"   # String di env, otomatis dikonversi ke int
os.environ["APP_RELOAD"] = "true" # String di env, otomatis dikonversi ke bool

server = ServerSettings()
print("\nKonfigurasi Server (env_prefix='APP_'):")
print(f"  Host   : {server.host}")
print(f"  Port   : {server.port} (tipe: {type(server.port).__name__})")  # int
print(f"  Reload : {server.reload} (tipe: {type(server.reload).__name__})")  # bool

# --- CATATAN PENTING: File .env & Keamanan ---
#
# ⚠️  File .env JANGAN pernah di-commit ke Git/GitHub karena berisi data sensitif!
#
# Tambahkan ke .gitignore:
#     .env
#     .env.local
#     .env.production
#
# ✅ Gunakan .env.example (berisi nama key tanpa value asli) untuk referensi tim:
#     DB_HOST=
#     DB_PORT=
#     DB_USER=
#     DB_PASSWORD=
#     DB_NAME=


# =============================================================================
# RINGKASAN PROGRES BELAJAR
# =============================================================================
#
# ✅ A. Dasar Pydantic              - BaseModel, type hints, type coercion
# ✅ B. Validasi Field dengan Field  - min_length, max_length, gt, lt
# ✅ C. Field wajib, nullable, default - Optional, None, default value
# ✅ D. Penanganan ValidationError   - try-except, exc.errors(), struktur error
# ✅ E. Pesan error kustom           - ERROR_MESSAGES, format_validation_errors()
# ✅ F. Validasi input vs business logic - pemisahan tanggung jawab
# 📖 G. model_validator              - Konsep dipahami, cross-field validation
# ✅ H. model_dump() / model_dump_json() - Serialisasi ke dict dan JSON string
# ✅ I. model_validate() / model_validate_json() - Deserialisasi dari dict/JSON
# ✅ J. Konfigurasi extra            - ignore (default), forbid, allow
# ✅ K. field_validator              - Validasi custom per field, mode before/after
# ✅ L. Alias                        - Field(alias=...), validation_alias, serialization_alias, populate_by_name
# ✅ M. Nested Models                - Model bersarang, rekursif validasi, error path
# ✅ N. Alias Path & Alias Choices   - AliasPath (flattening data), AliasChoices (fallback alias)
# ✅ O. Strict Mode                  - strict=True di Field atau ConfigDict, mematikan coercion
# ✅ P. BaseSettings                 - pydantic-settings, .env loading, SettingsConfigDict, env_prefix
#
# --- MATERI SELANJUTNYA (Belum dipelajari) ---
# ❌ Annotated types               - Menggabungkan type hints dengan metadata
# ❌ Generic models                - Model dengan tipe generik
# =============================================================================
