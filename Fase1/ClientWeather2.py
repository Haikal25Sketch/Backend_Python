import json
import logging
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from typing import Optional
from pydantic import BaseModel,ValidationError
from dataclasses import dataclass,asdict
from datetime import datetime,date
import requests

def save (location:str,data:dict) -> None:
    """Untuk menyimpan data ke json"""
    with open(location,"w") as file:
        json.dump(data,file,indent=4)

def ambil(location:str) -> dict:
    """Untuk mengambil file json"""
    with open(location,"r") as file:
        data = json.load(file)
        return data

def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("app2.log")
    file_handler.setLevel(logging.INFO)

    terminal_handler = logging.StreamHandler()
    terminal_handler.setLevel(logging.ERROR)

    file_format = logging.Formatter("%(asctime)s | %(level)s | %(name)s | %(message)s ")

    terminal_format = logging.Formatter("%(level)s | %(message)s ")

    file_handler.setFormatter(file_format)
    terminal_handler.setFormatter(terminal_format)

    logger.addHandler(file_handler)
    logger.addHandler(terminal_handler)

    return logger

logger = setup_logging()

@dataclass
class WeatherReport:
    temperature : float
    kecepatan_angin : float
    kelembaban : int
    kondisi_langit : int
    hujan : int
    timestamp : datetime

class WeatherReportModel(BaseModel):
    temperature : float
    kecepatan_angin : float
    kelembaban : int
    kondisi_langit : int
    hujan : int
    timestamp : datetime

class BaseClient:

    def __init__(self):
        self.session = requests.Session()
        self.retry = Retry(
            total = 3,
            backoff_factor = 2,
            status_forcelist = [429,500,502,503,504])
        self.adapter = HTTPAdapter(max_retries=self.retry)
        self.session.mount("https://",self.adapter)
        self.session.mount("http://",self.adapter)
        self.session.headers.update({
        'User-Agent':'Mozilla/5.0 (Linux; Android 10; K)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 MobileSafari/537.36'})
        self.session.cookies.set("session_id","abc123")
        self.timeout = 10

class WeatherClient(BaseClient):
    def __init__(self,base_url:str):
        super().__init__()
        """Berisi url untuk ke open meteo dan jsonplaceholder"""
        self.base_url = base_url
        self.post_url = 'https://jsonplaceholder.typecode.com/posts'

    def get_weather(self,latitude:float,longitude:float) -> WeatherReportModel:
        url = self.base_url
        params = {
        "latitude":latitude,
        "longitude":longitude,
        "current":"temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m,rain"} # data yang mau gw ambil

        try:
            response = self.session.get(url,params=params,timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            print (data)
            result = data["current"]
            raport = WeatherReport(temperature=result["temperature_2m"],kecepatan_angin=result["wind_speed_10m"],kelembaban=result["relative_humidity_2m"],kondisi_langit=result["weather_code"],hujan=result["rain"],timestamp=datetime.now())

            raport_model = WeatherReportModel(temperature=raport.temperature,kecepatan_angin=raport.kecepatan_angin,kelembaban=raport.kelembaban,kondisi_langit=raport.kondisi_langit,hujan=raport.hujan,timestamp=raport.timestamp)

            hasil = raport_model.model_dump()
            hasil["timestamp"] = hasil["timestamp"].isoformat()
            save("raport2.json",hasil)
            return raport_model

        except requests.exceptions.RequestException as error:
            logger.error(f"TERJADI ERROR TIDAK TERDUGA SAAT MENGHUBUNGI SERVER : {error} ")
            raise

        except ValidationError as erro:
            logger.error(f"TERJADI MASALAH SAAT MELAKUKAN VALIDASI PYDANTIC : {erro} ")
            raise

        except TypeError as err:
            logger.error(f"TIPE DATA TIDAK SESUAI : {err} ")
            raise

        except Exception as e:
            logger.error(f"TERJADI ERROR YANG TIDAK TERDUGA : {e} ")
            raise


def run():
    cuaca=WeatherClient("https://api.open-meteo.com/v1/forecast")
    hasil = cuaca.get_weather(-7.65149694,108.14768194)
    cuaca_mapping = {
    0: "Cerah Sekali ",
    1: "Cenderung Cerah ",
    2: "Berawan Sebagian ",
    3: "Mendung/Berawan Tebal ",
    45: "Berkabut ",
    61: "Hujan Ringan ",
    63: "Hujan Sedang ",
    65: "Hujan Lebat ",
    95: "Badai Petir "
}
    kode_cuaca = hasil.kondisi_langit
    status_cuaca = cuaca_mapping.get(kode_cuaca,"KONDISI CUACA TIDAK DIKETAHUI!!")
    print ("===PERKIRAAN CUACA KARANGNUNGGAL TASIKMALAYA===")
    print (f"NAMA DESA : KARANGNUNGGAL\nSUHU : {hasil.temperature}°C\nKECEPATAN_ANGIN : {hasil.kecepatan_angin}%\nKONDISI LANGIT : {hasil.kondisi_langit}({status_cuaca})")
if __name__ == "__main__":
    run()
