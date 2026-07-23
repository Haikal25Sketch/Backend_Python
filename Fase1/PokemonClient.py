import json
import logging
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from typing import Optional
from pydantic import BaseModel,ValidationError
from dataclasses import dataclass,asdict
import requests

def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Handler 1 — ke file
    file_handler = logging.FileHandler("pokemon.log")
    file_handler.setLevel(logging.DEBUG)

    # Handler 2 — ke terminal
    terminal_handler = logging.StreamHandler()
    terminal_handler.setLevel(logging.WARNING)
    file_fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    file_handler.setFormatter(file_fmt)
    stream_fmt = logging.Formatter("%(levelname)s |  %(message)s")
    terminal_handler.setFormatter(stream_fmt)
    if not logger.handlers:
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
class PokemonReport:
    name:str
    weight:int
    height:int
    base_experience:int
    pokemon_type:str
    base_hp:int
    base_attack:int
    base_defense:int
    base_special_attack:int
    base_special_defense:int
    base_speed:int

class PokemonReportModel(BaseModel):
    name:str
    weight:int
    height:int
    base_experience:int
    pokemon_type:str
    base_hp:int
    base_attack:int
    base_defense:int
    base_special_attack:int
    base_special_defense:int
    base_speed:int

class Tool:
    def __init__(self):
        self.session = requests.Session()
        self.retry = Retry(
            total = 5,
            backoff_factor = 3,
            status_forcelist = [429,500,502,503,504]
            )
        self.adapter = HTTPAdapter(max_retries=self.retry)
        self.session.mount("https://",self.adapter)
        self.session.mount("http://",self.adapter)
        self.session.headers.update({
            'User-Agent':'Mozilla/5.0 (Linux; Android 11; K) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 MobileSafari/537.36'})
        self.timeout = 8


class PokemonClient(Tool):
    def __init__(self,base_url):
        super().__init__()
        self.base_url = base_url

    def get_info(self,pokemon_name):
        url = self.base_url
        try:
            response = self.session.get(f"{url}/{pokemon_name}",timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            logger.info("DATA POKEMON BERHASIL DIDAPATKAN")

            report = PokemonReport(name=data["name"],weight=data["weight"],height=data["height"],base_experience=data["base_experience"],pokemon_type =data["types"][0]["type"]["name"],base_hp=data["stats"][0]["base_stat"],base_attack=data["stats"][1]["base_stat"],base_defense=data["stats"][2]["base_stat"],base_special_attack=data["stats"][3]["base_stat"],base_special_defense=data["stats"][4]["base_stat"],base_speed=data["stats"][5]["base_stat"])

            report_model = PokemonReportModel(name=report.name,weight=report.weight,height=report.height,base_experience=report.base_experience,pokemon_type=report.pokemon_type,base_hp=report.base_hp,base_attack=report.base_attack,base_defense=report.base_defense,base_special_attack=report.base_special_attack,base_special_defense=report.base_special_defense,base_speed=report.base_speed)
            logger.info("DATA POKEMON BERHASIL DIVALIDASI")
            result = report_model.model_dump()

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"TERJADI MASALAH SAAT MENGHUBUNGI SERVER : {e}")
            raise

        except ValidationError as er:
            logger.error(f"TERJADI MASALAH SAAT VALIDASI :{er} ")
            raise

        except TypeError as err:
            logger.error(f"TIPE DATA TIDAK SESUAI : {err}")
            raise

        except Exception as error:
            logger.error(f"TERJADI ERROR TIDAK TERDUGA : {error}")
            raise

def run():
    model = PokemonClient("https://pokeapi.co/api/v2/pokemon")
    hasil =[]
    pikachu = model.get_info("pikachu")
    charizard = model.get_info("charizard")
    flygon = model.get_info("flygon")
    hasil.append(pikachu)
    hasil.append(charizard)
    hasil.append(flygon)
    save("Pokemon.json",hasil)

if __name__ == "__main__":
    run()
