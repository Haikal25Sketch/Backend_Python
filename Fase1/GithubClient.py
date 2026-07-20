import requests
import json
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from dataclasses import dataclass
import logging
from datetime import datetime,date
from pydantic import BaseModel,ValidationError
from typing import Optional
import traceback

def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("Github.log")
    file_handler.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.ERROR)

    file_format = logging.Formatter(f"%(asctime)s | %(levelname)s | %(name)s | %(message)s ")
    file_handler.setFormatter(file_format)

    stream_format = logging.Formatter(f"%(levelname)s | %(message)s ")
    stream_handler.setFormatter(stream_format)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger

logger = setup_logging()

def save(location,data):
    with open(location,"w") as file:
        json.dump(data,file,indent=4)

def load(location):
    with open(location,"r") as file:
        data = json.load(file)
        return data



@dataclass
class GithubReport:
    login:str
    name:Optional[str]
    public_repos:int
    followers:int
    following:int
    bio:Optional[str] = None

class GithubReportModel(BaseModel):
    login:str
    name:Optional[str]
    public_repos:int
    followers:int
    following:int
    bio:Optional[str] = None

class Tool:
    def __init__(self):
        self.session = requests.Session()
        self.retry = Retry(
            total = 5,
            backoff_factor = 3,
            status_forcelist =[429,500,502,503,504]
            )
        self.adapter = HTTPAdapter(max_retries=self.retry)
        self.session.mount("https://",self.adapter)
        self.session.mount("http://",self.adapter)
        self.session.headers.update({
        'User-Agent':'Mozilla/5.0 (Linux; Android 11; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 MobileSafari/537.36'})
        self.timeout = 10
    

class GithubClient(Tool):
    def __init__(self,base_url):
        super().__init__()
        self.base_url = base_url

    def get_info(self,username:str):
        url = self.base_url
        try:
            response = self.session.get(f"{url}/{username}", timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            logger.info("DATA GITHUB BERHASIL DIDAPATKAN")
            "Menginputkan data json yang diperlukan ke GithubReport"
            report = GithubReport(login=data["login"],name=data["name"],public_repos=data["public_repos"],followers=data["followers"],following=data["following"],bio=data["bio"])

            "Menginputkan GithubReport ke pydantic untuk divalidasi"
            report_model = GithubReportModel(login=report.login,name=report.name,public_repos=report.public_repos,followers=report.followers,following=report.following,bio=report.bio)
            logger.info("DATA GITHUB BERHASIL DIVALIDASI")
            js = report_model.model_dump()
            save("reportGithub.json",js)
            logger.info("DATA GITHUB BERHASIL DISIMPAN DI FILE .json")
            
            return report_model
        except requests.exceptions.RequestException as e:
            logger.error(f"TERJADI MASALAH SAAT MENGHUBUNGI SERVER : {e}")
            raise
        except ValidationError as er:
            logger.error (f"TERJADI MASALAH SAAT MELAKUKAN VALIDASI : {er}")
            raise
        except TypeError as err:
            logger.error(f"TIPE DATA TIDAK SESUAI : {err}")
            raise
        except Exception as error:
            logger.error(f"TERJADI ERROR TIDAK TERDUGA : {error}")
            raise

def run():
    github = GithubClient("https://api.github.com/users")
    github.get_info("Haikal25Sketch")

if __name__ == "__main__":
    run()
