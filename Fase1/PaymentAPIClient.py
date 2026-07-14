import requests
import logging
import pydantic
import logging
from datetime import datetime
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
from enum import Enum #untuk mendefinisikan sebuah tipe data khusus yang berisi kumpulannilai konstanta(tetap) yang saling berkaitan dan sudah ditentukan sebelumnya.

class PaymentGatewayError(Exception):
    pass

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # Handler 2 — ke terminal
    terminal_handler = logging.StreamHandler()
    terminal_handler.setLevel(logging.ERROR)
    stream_fmt = logging.Formatter("%(levelname)s |  %(message)s")
    terminal_handler.setFormatter(stream_fmt)

    logger.addHandler(terminal_handler)
    return logger
logger = setup_logging()

class Status(str,Enum):
    SUCCESS ="SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"



class ValidationAPI(BaseModel):
    transaction_id: str
    amount: int
    status: Status
    timestamp: datetime

class PaymentGatewayClient:
    def __init__(self,base_url:str,timeout:tuple):
        self.base_url = base_url
        self.timeout = timeout
        self._session = requests.Session()
        self.retry = Retry(
            total =3,
            backoff_factor=1,
            status_forcelist = [500,502,503,504],
            raise_on_status=False # Biar raise_for_status() di method kita yang handle errornya, bukan urllib3
        )
        self.adapter = HTTPAdapter(max_retries = self.retry)
        self._session.mount("https://",self.adapter)
        self._session.mount("http://",self.adapter)

    def get_transaction_status(self,transaction_id):
        url = f"{self.base_url}/transactions/{transaction_id}"
        try:
            response = self._session.get(url,timeout=self.timeout)
            response.raise_for_status()
            hasil = ValidationAPI(**response.json())
            return hasil
        except requests.exceptions.RequestException as e:
            logger.error (f"API PAYMENT ERROR UNTUK ID {transaction_id} : {e}")
            raise PaymentGatewayError("GAGAL BERKOMUNIKASI DENGAN PIHAK PEMBAYARAN")
        except ValidationError as val:
            logger.error(f"DATA TIDAK VALID")
            raise PaymentGatewayError(f"DATA USER TIDAK VALID : {val}")

pay = PaymentGatewayClient("https://httpbin.org",(2.0,5.0))
try:
    pay.get_transaction_status("TPC-789")

except PaymentGatewayError as error:
    print ("ERROR TERTANGKAP : ",error)

