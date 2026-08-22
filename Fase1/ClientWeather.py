import json
import logging
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from typing import Optional
from pydantic import BaseModel,ValidationError
from dataclasses import dataclass,asdict 
from datetime import datetime,date
import requests

def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Handler 1 — ke file
    file_handler = logging.FileHandler("app.log")
    file_handler.setLevel(logging.DEBUG)

    # Handler 2 — ke terminal
    terminal_handler = logging.StreamHandler()
    terminal_handler.setLevel(logging.WARNING)
    file_fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    file_handler.setFormatter(file_fmt)
    stream_fmt = logging.Formatter("%(levelname)s |  %(message)s")
    terminal_handler.setFormatter(stream_fmt)

    logger.addHandler(file_handler)
    logger.addHandler(terminal_handler)
    return logger
logger = setup_logging()

def save(location:str,data:dict)-> None:
    """Untuk save ke json"""
    with open (location,"w") as file:
        json.dump(data,file,indent=4)

def load(location:str) -> dict:
    """untuk mengambil data json"""
    with open(location,"r") as file:
        data =json.load(file)
        return data
@dataclass
class WeatherReport:
    temperature:float
    kelembaban:int
    kecepatan_angin:float
    timestamp:datetime

class WeatherReportModel(BaseModel):
    temperature:float
    kelembaban:int
    kecepatan_angin:float
    timestamp:datetime # waktu data ini dicatat atau diambil

class BaseClient: 
    def __init__(self):
        self.session = requests.Session()
        self.retry = Retry(
            total = 3,
            backoff_factor=1,
            status_forcelist=[429,500,502,503,504])
        self.adapter = HTTPAdapter(max_retries = self.retry)
        self.session.mount("https://",self.adapter)
        self.session.mount("http://",self.adapter)
        self.session.headers.update({
        'User-Agent':'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 MobileSafari/537.36' })
        self.session.cookies.set("session_id","abc123")
        self.timeout = 10

#Header adalah metadata tentang request.
#User-Agent adalah salah satu header yang memberi tahu server identitas client.

class WeatherClient(BaseClient):
    def __init__(self,base_url):
        super().__init__()
        self.base_url = base_url
        self.post_url = 'https://jsonplaceholder.typicode.com/posts'
    def get_weather(self,latitude:float,longitude:float) -> WeatherReport:

        """Mendapatkan informasi cuaca dari open-meteo berdadarkan data yang kita kirim"""

        url = self.base_url
        params = {
        "latitude":latitude,
        "longitude":longitude,
        "current":"temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m" # Data cuaca yang mau diambil
        }
        try:
            response = self.session.get(url,params=params,timeout=self.timeout)
            response.raise_for_status()
            hasil_json = response.json()
            hasil = hasil_json["current"]
            logger.info("DATA CUACA BERHASIL DIDAPATKAN")

            """Menjadikan variabel hasil yang berisi current sebagai parameter WeatherReport"""

            report = WeatherReport(temperature=hasil["temperature_2m"],
                kelembaban=hasil["relative_humidity_2m"],kecepatan_angin=hasil["wind_speed_10m"],timestamp=datetime.now()) 

            """Menjadikan atribut report sebagai parameter dari Pydantic"""

            report_model = WeatherReportModel(temperature=report.temperature,kelembaban=report.kelembaban,kecepatan_angin=report.kecepatan_angin,timestamp=report.timestamp) 
            
            result=report_model.model_dump() # Mengubah pydantic menjadi dict dengan .model_dump()
            result["timestamp"]=result["timestamp"].isoformat() #mengubah  datetime menjadi string yang bisa diterima json
            save("report.json",result)
            logger.info("DATA CUACA BERHASIL DISIMPAN KE JSON")
            return report_model

        except requests.exceptions.RequestException as e:
            logger.error(f"TERJADI MASALAH SAAT MENYAMBUNG KE SERVER : {e}")
            raise
        except ValidationError as error:
            logger.error(f"TERJADI MASALAH SAAT VALIDASI : {error}")
            raise
        except TypeError as err:
            logger.error(f"TIPE DATA TIDAK SESUAI! : {err}")
            raise

    def create_post(self,title:str,body:str,user_id:int) -> dict: # post ke JSONPLACEHOLDER
        url = self.post_url
        payload ={"title":title, "body":body, "userId":user_id}
        try:
            response = self.session.post(url,json=payload)
            response.raise_for_status()
            hasil_json= response.json()
            return hasil_json

        except requests.exceptions.RequestException as error:
            logger.error(f"GAGAL MELAKUKAN KONEKSI KE SERVER KARENA {error}")
            raise
        except Exception as e:
            logger.error (f"ERROR TAK TERDUGA : {e}")
            raise
def main():
    client = WeatherClient("https://api.open-meteo.com/v1/forecast")

    result =client.get_weather(-6.402905, 106.778419)
    data = load("report.json")
    print (f"===DATA CUACA DEPOK {date.today()}===")
    print (f"Suhu:{data['temperature']}C\nKelembaban Relatif Udara : {data['kelembaban']}%\nKecepatan Angin : {data['kecepatan_angin']}km/jam")
    post = client.create_post("Weather Report",f"Suhu :{result.temperature}",1)

if __name__ == "__main__":
    main()
