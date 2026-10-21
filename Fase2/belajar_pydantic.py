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

from pydantic import BaseModel, Field, model_validator, ValidationError
from typing import Optional


# Contoh dasar BaseModel
class UserDasar(BaseModel):
    nama: str
    umur: int


# Saat dibuat, validasi otomatis berjalan:
# user = UserDasar(nama="Budi", umur="25")  # "25" dikonversi ke int -> OK
# user = UserDasar(nama=123, umur=25)        # 123 dikonversi ke str "123" -> OK
# user = UserDasar(nama="Budi", umur="abc") # ERROR: "abc" tidak bisa jadi int


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
# RINGKASAN PROGRES BELAJAR
# =============================================================================
#
# ✅ A. Dasar Pydantic              - BaseModel, type hints, type coercion
# ✅ B. Validasi Field dengan Field  - min_length, max_length, gt, lt
# ✅ C. Field wajib, nullable, default - Optional, None, default value
# ✅ D. Penanganan ValidationError   - try-except, exc.errors(), struktur error
# ✅ E. Pesan error kustom           - ERROR_MESSAGES, format_validation_errors()
# ✅ F. Validasi input vs business logic - pemisahan tanggung jawab
# 📖 G. model_validator              - Konsep dipahami, perlu latihan lebih
# ✅ H. model_dump() / model_dump_json() - Serialisasi ke dict dan JSON string
# ✅ I. model_validate() / model_validate_json() - Deserialisasi dari dict/JSON
# ✅ J. Konfigurasi extra            - ignore (default), forbid, allow
#
# --- MATERI SELANJUTNYA (Belum dipelajari) ---
# ❌ field_validator               - Validasi custom untuk 1 field tertentu
# ❌ Nested models                 - Model di dalam model
# ❌ model_config (Config class)   - Konfigurasi model lainnya (strict mode, dll.)
# ❌ Annotated types               - Menggabungkan type hints dengan metadata
# ❌ Generic models                - Model dengan tipe generik
# =============================================================================
