import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    YANDEX_MAPS_API_KEY = os.getenv('YANDEX_MAPS_API_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY')