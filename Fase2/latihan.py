from pydantic import BaseModel,Field,ValidationError,model_validator,ConfigDict

class UserCreate(BaseModel):
    nama:str
    umur:int
    hobi:str|None=None
    makanan_favorit:list[str]


User1 = UserCreate(nama='HuTao',umur=19,makanan_favorit=['Sushi','Yakiniku'])

data = {"nama":"HuTao","umur":18,"hobi":"makan","makanan_favorit":["sushi","Salmon"]}

User2= UserCreate.model_validate(data)
hasil =User2.model_dump_json()
hasil2 = User2.model_dump()
print (type(hasil))
print (type(hasil2))
print()

ERROR_MESSAGES = {
    'missing':'Field wajib diisi',
    'string_too_short':'Teks terlalu pendek',
    'string_too_long':'Teks terlalu panjang'
    }
print (ERROR_MESSAGES.get('missing'))






MESSAGES_ERROR = {
    ('nama','missing'):'Field wajib diisi',
    ('nama','text_too_short'):'teks terlalu pendek',
    ('nama','text_too_long'):'teks terlalu panjang'
    }




class MyBiniGuweh(BaseModel):

    model_config = ConfigDict(extra='forbid')
    id:int = Field(gt=0,description = 'id istri')
    nama:str = Field(min_length=5,max_length=30,description='Nama istri')
    umur:int = Field(gt=18,lt=40,description='Umur istri')

try:
    bini1=MyBiniGuweh(id=1,nama='Huhu',umur=16)

except ValidationError as error:
    messages =[]

    for errors in error.errors():
        if errors['loc'][0] == 'umur' and errors['type'] == 'greater_than':
            message = 'Umur harus lebih dari 18 tahun'

        elif errors['loc'][0] == 'nama' and errors['type'] == 'string_too_short':
            message = 'Nama minimal 5 karakter'

        else:
            message = 'Data tidak valid'

        messages.append(message)


    response = {"errors":messages}

    print (response)


print()
data_bini ={'id':2,'nama':"Citlali",'umur':25,'pasangan':'Haikal'}
bini2 =MyBiniGuweh.model_validate(data_bini)
print (bini2)


MESSAGES_ERROR = {
    ('nama','missing'):'Field wajib diisi',
    ('nama','text_too_short'):'teks terlalu pendek',
    ('nama','text_too_long'):'teks terlalu panjang'
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

class User(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    umur: int = Field(gt=18)
    partner:str

    @model_validator(mode='after')
    def check_partner(self):
        if self.username == self.partner:
            raise ValueError('User dan partner tidak boleh sama')

        return self


ERROR_MESSAGES = {
    ('username', 'string_too_short'): 'Username minimal 3 karakter',
    ('username', 'string_too_long'): 'Username maksimal 20 karakter',
    ('umur', 'greater_than'): 'Umur harus lebih dari 18 tahun',
    ('username', 'missing'): 'Username wajib diisi',
    ('umur', 'missing'): 'Umur wajib diisi',
    ((),'ValueError'):'User dan partner tidak boleh sama'
}

try:
    user = User(username='HuTao', umur=19,partner='HuTao')

except ValidationError as exc:
    response = format_validation_errors(exc)
    print (response)

