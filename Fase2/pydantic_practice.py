
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    ValidationError,
    field_validator,
    model_validator,
    AliasChoices,
    AliasPath
)

from typing import Optional
from uuid import UUID
import uuid

# ==================================================
# BAGIAN 1 - BASIC MODEL & FIELD
# ==================================================

class UserCreate(BaseModel):

    # TODO 1:
    username:str=Field(min_length=3,max_length=30)

    # TODO 2:
    email:str=Field(min_length=5)
    # email berupa string dengan batasan panjang
    # minimal 5 karakter.

    # TODO 3:
    age:int=Field(ge=18)
    # age berupa integer dan minimal 18.
HuTao = UserCreate(username="HuTao",email="HuTao23@gmail.com",age=25)
print (HuTao)
print()
# ==================================================
# BAGIAN 2 - FIELD VALIDATOR
# ==================================================

class UsernameModel(BaseModel):
    username: str

    # TODO 4:
    # Buat field_validator untuk username.
    @field_validator("username",mode="before")
    @classmethod
    def clear_character(cls,value):
        if isinstance(value,str):
            return value.strip().title()
        return value
    
    # Bersihkan spasi di awal dan akhir.
    # Ubah username menjadi huruf kecil.
    #
    # Gunakan mode yang sudah kamu pelajari.

Kagura = UsernameModel(username= "      kagura")
print (Kagura)
# ==================================================
# BAGIAN 3 - MODEL VALIDATOR
# ==================================================

class RegisterModel(BaseModel):

    username: str
    partner: str

    @model_validator(mode="after")
    def clearmodel(self):
        if self.username == self.partner:
            raise ValueError("Username dan partner tidak boleh sama")
    # TODO 5:
    # Pastikan username tidak boleh sama dengan partner.
    #
    # Gunakan model_validator.
    # Tentukan mode yang sesuai.
    # Jika sama, raise ValueError.
try:
    Milim=RegisterModel(username= "MilimNava",partner="MilimNava")

except ValidationError as exc:
    print ("Error : ",exc)
print()
# ==================================================
# BAGIAN 4 - SERIALIZATION & VALIDATION
# ==================================================

class ProductModel(BaseModel):

    name: str
    price: int
    quantity: int


# TODO 6:
#
# Buat instance ProductModel menggunakan data:
#
data_produk = {
     "name": "Keyboard",
     "price": 150000,
     "quantity": 2
}

# Kemudian:
# A. Ubah menjadi dictionary.
# B. Ubah menjadi JSON string.
# C. Validasi ulang menggunakan model_validate.
# D. Validasi JSON menggunakan model_validate_json.
#
# Simpan hasil setiap proses dalam variabel berbeda.
try:
    produk = ProductModel.model_validate(data_produk)
    data_dict = produk.model_dump()
    data_json = produk.model_dump_json()

    produk_dict = ProductModel.model_validate(data_dict)
    print ("Ini adalah dict :",produk_dict)
    produk_json = ProductModel.model_validate_json(data_json)
    print (f"Dari dict -> Model : {produk_dict}")
    print (f"Dari json -> Model : {produk_json}")

except ValidationError as exc:
    print (exc)

# ==================================================
# BAGIAN 5 - EXTRA CONFIGURATION
# ==================================================

class UserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nama:str
    umur:int

print()

    # TODO 7:
    # Konfigurasikan extra agar field tambahan
    # dari client ditolak.
#try: Ini error dan akan ditolak oleh pydantic
#    from_user = UserRequest(nama="Changli",umur=18,pasangan = "Razim")

#except ValidationError as exc:
#    print (exc)

class UserResponse(BaseModel):

    username: str
    email: str
    password: str

print()


    # TODO 8:
    # Buat password tidak ikut dalam hasil model_dump.
for_user = UserResponse(username="Reze",email="kudaranai@gmail.com",password="Kambinggenshin7765+")

non_password = for_user.model_dump(exclude={"password"})
print (non_password)

# ==================================================
# BAGIAN 6 - ALIAS
# ==================================================

class ItemRequest(BaseModel):
    

    # TODO 9:
    # Buat field internal:
    # nama_item
    # harga_satuan
    # kuantitas
    #
    # Client menggunakan:
    # itemName
    # unitPrice
    # qty
    #
    # Gunakan alias yang tepat.
    nama_item:str=Field(alias="itemName")
    harga_satuan:int=Field(ge=0,alias="unitPrice")
    kuantitas:int=Field(ge=1,alias="qty")

# TODO 10:
#
# Buat instance ItemRequest dari dictionary
# menggunakan nama field milik client.
#
# Kemudian serialisasikan dengan alias.

from_user = {"itemName":"Keadilan","unitPrice":100,"qty":10}
item_1 = ItemRequest.model_validate(from_user)
dct = item_1.model_dump(by_alias=True)
print (item_1)
print (dct)


# ==================================================
# BAGIAN 7 - ALIASCHOICES
# ==================================================

class CustomerRequest(BaseModel):
    

    # TODO 11:
    # Field internal: customer_name
    #
    # Client bisa mengirim:
    # customerName
    # customer
    # name
    #
    # Gunakan AliasChoices.
    customer_name:str=Field(AliasChoices("customerName","customer","name"))
    customer_id:int=Field(ge=1)

from_user1 = {"customerName":"Raihan","customer_id":1554}
from_user2 = {"customer":"Raihan","customer_id":1707}
from_user3 = {"name":"Raihan","customer_id":8876}

print()
result1 = CustomerRequest.model_validate(from_user1)
print (result1)
result2 = CustomerRequest.model_validate(from_user2)
print (result2)
result3 = CustomerRequest.model_validate(from_user3)
print (result3)

# ==================================================
# BAGIAN 8 - NESTED MODELS
# ==================================================

class WalletInfo(BaseModel):
    pass

    # TODO 12:
    # wallet_id berupa UUID.
    # balance berupa integer.
    wallet_id:uuid.UUID=Field(default_factory=uuid.uuid7)
    balance:int=Field(ge=1000)

class UserWalletResponse(BaseModel):

    username: str
    wallet:WalletInfo

    # TODO 13:
    # Hubungkan model WalletInfo
    # sebagai field wallet.

data_wallet = { "username":"Kito De fisa",
"wallet":{
    "balance":1500}
}


HuTaoWallet = UserWalletResponse.model_validate(data_wallet)
print (HuTaoWallet)

# ==================================================
# BAGIAN 9 - ALIASPATH
# ==================================================

class ExternalTransaction(BaseModel):
    username:str
    wallet:WalletInfo
    transaction:int=Field(validation_alias = AliasPath("transaction","detail","amount"))

data_wallet = { "username":"Kito De fisa",
"wallet":{"balance":15800},
"transaction":
    {"detail":
        {"amount":98000}
    }
}

Transaksi= ExternalTransaction.model_validate(data_wallet)
print()
print(Transaksi)

    # TODO 14:
    # Ambil amount dari struktur:
    #
    # transaction
    #     detail
    #         amount
    #
    # Gunakan AliasPath.


# ==================================================
# BAGIAN 10 - STRICT MODE
# ==================================================

class TransferRequest(BaseModel):
    pass

    # TODO 15:
    # amount harus integer.
    # Terapkan strict hanya pada field amount.

    # TODO 16:
    # description berupa string.
    # Jangan menerapkan strict pada field ini.


# ==================================================
# BONUS - ANALISIS PERILAKU PYDANTIC
# ==================================================

# TODO 17:
#
# Buat pengujian untuk membuktikan:
#
# A. Apa yang terjadi ketika amount menerima string angka?
# B. Apa yang terjadi ketika amount menerima integer?
# C. Apa yang terjadi ketika description menerima integer?
# D. Apa perbedaan hasil validasi ketiga kasus tersebut?
#
# Gunakan try-except ValidationError.
# Jangan hanya menebak. Buktikan melalui output Python.
