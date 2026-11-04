from pydantic import BaseModel,Field,ValidationError,model_validator,ConfigDict,field_validator,ConfigDict

class SameValueError(Exception):
    pass

class UserCreate(BaseModel):
    model_config= ConfigDict(extra='forbid') #Melarang field yang ga ada disini untuk masuk

    nama:str
    umur:int=Field(ge=18,le=50)
    hobi:str|None=None
    makanan_favorit:str|list[str]=None
    partner:str

    @field_validator("nama","hobi","makanan_favorit","partner",mode= "before")
    @classmethod
    def transform_capitalize(cls,data): #Merubah karakter yang ditentukan menjadi .capitalize()/.title()
        if isinstance(data,list):
            return[str(item).title() for item in data]
        elif isinstance(data,str):
            return data.title()

        return data

    @field_validator("nama",mode="after") # menurut gw field validator tuh untuk validasi kedua jika after,tapi validasi pertama jika before
    @classmethod
    def check_not_number(cls,data): # Mencegah angka dalam data nama
        if any(char.isdigit() for char in data):
            raise ValueError("Nama tidak boleh mengandung angka")
        return data


    @model_validator(mode='before') #Validasi sebelum validasi
    @classmethod
    def check_before_validation(cls,data:dict):
        if isinstance(data,dict):
            if "nama" in data and isinstance(data["nama"],str):
                data["nama"]= data["nama"].strip("&")
            return data
    @model_validator(mode='after') #Validasi setelah validasi
    def check_after_validation(self):
        if self.nama == self.partner:
            raise SameValueError("Value tidak boleh sama")
        return self

ERROR_MESSAGES = {
    ('username', 'string_too_short'): 'Username minimal 3 karakter',
    ('username', 'string_too_long'): 'Username maksimal 20 karakter',
    ('umur', 'greater_than'): 'Umur harus lebih dari 18 tahun',
    ('username', 'missing'): 'Username wajib diisi',
    ('umur', 'missing'): 'Umur wajib diisi'
}

def format_validation_errors(error):
    messages = []

    for results in error.errors():
        print (results)
        key = (results['loc'],results['type'])

        message = ERROR_MESSAGES.get(key,'Data tidak valid')

        messages.append({'field':results['loc'],
        'message':message}
        )

    response = {'errors':messages}

    return response



try: # nama,makanan favorit dan partner akan dicapitalize karena sudah di validasi sebelum divalidasi 
    User1 = UserCreate(nama='huTao',umur=19,hobi='Mengubur orang',makanan_favorit=['sushi','yakiniku'],partner='zhongli',)
    print (User1)
except ValidationError as exc:
    response = format_validation_errors(exc)
    print (response)

MESSAGES_ERROR = {
    ('nama','missing'):'Field wajib diisi',
    ('nama','text_too_short'):'teks terlalu pendek',
    ('nama','text_too_long'):'teks terlalu panjang'
    }


try: #Percobaan error field umur
    data_user2={"nama":"Angela","umur":1,"hobi":"Support team","makanan_favorit":None,"partner":"Lancelot"}

    User2= UserCreate.model_validate(data_user2) # Ini adalah deserialisasi,yaitu merubah data mentah menjadi objek model python

except ValidationError as error:
    response = format_validation_errors(error)
    print (response)

print()

try:
    data_User3= {'nama':'Ganyu','umur':27,'hobi':'Memanah',"makanan_favorit":"Daging Kambing","partner":None}

    User3= UserCreate.model_validate(data_User3)
    print (User3)
    
except ValidationError as error:
    response = format_validation_errors(error)
    print (response)


#Latihan Alias

class DataKaryawanAlias(BaseModel):
    username:str=Field(alias="nama")
    gaji:int
    status:str=None

data1 = {"nama":"Haikal","gaji":1650000,"status":"Hadir"}

try:
    Haikal = DataKaryawanAlias.model_validate(data1)
    print (Haikal)
    print (Haikal.model_dump(by_alias = True)) # menghasilkan nama:haikal
    print (Haikal.model_dump()) # menghasilkan username:haikal

except ValidationError as exc:
    response = format_validation_errors(exc)
    print (response)


# Latihan serialization_alias

class DataKaryawanSerializationAlias(BaseModel):
    username:str=Field(serialization_alias="nama")
    gaji:int
    status:str=None

data1 = {"username":"Rimuru","gaji":178900,"status":"Hadir"}

try:
    Rimuru = DataKaryawanSerializationAlias.model_validate(data1)
    print (Rimuru)
    print (Rimuru.model_dump(by_alias = True)) #Menentukan nama field saat di serialisasikan (diubah) ke bentuk lain misal dict atau json

except ValidationError as exc:
    response = format_validation_errors(exc)
    print (response)

# Latihan Validation_alias
class DataKaryawanValidationAlias(BaseModel):
    username:str=Field(validation_alias="nama")
    gaji:int
    status:str=None

data1 = {"nama":"Ssnapy","gaji":178900,"status":"Hadir"}

try:
    Rimuru = DataKaryawanValidationAlias.model_validate(data1)
    print (Rimuru)
    print (Rimuru.model_dump(by_alias = True)) #Menentukan nama field yang diterima saat validasi(menerima data dari luar) 

except ValidationError as exc:
    response = format_validation_errors(exc)
    print (response)



# Alias choiches bisa lu kulik sendiri

#Latihan Nested models

class Address(BaseModel):
    city:int
    street:str

class DataPribadi(BaseModel):
    nama:str
    alamat:Address

Depok = Address(city="123",street="Kalimulya")
Haikal = DataPribadi(nama="Haikal",alamat=Depok)
print (type(Haikal.alamat))

# Latihan Strict(pemerketatan aturan)

class LatihanStrict(BaseModel):
    model_config = ConfigDict(strict=True) #Seakan menonaktifkan coercion(pengubahan yang bisa dilakukan pydantic dari str ke int)
    nama:str
    saldo:int

Saldo_Haikal = LatihanStrict(nama="Haikal",saldo=1000)


#Strict di Field

class LatihanStrictField(BaseModel):
    nama:str
    umur:int=Field(strict=True)

HuTao = LatihanStrictField(nama="HuTao",umur='ABC')
