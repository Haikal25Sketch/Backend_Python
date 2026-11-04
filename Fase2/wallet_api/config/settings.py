from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    '''Mendefinisikan 5 field yang nanti akan divalidasi dari file .env'''
    db_host:str
    db_port:int
    db_user:str
    db_password:str
    db_name:str

    '''Konfigurasi model dengan SettingsConfigDict'''
    model_config = SettingsConfigDict(
                    env_file =".env",
                    env_file_encoding = "utf-8"
                    )

settings = Settings()

