from typing import Dict, List
from pydantic_settings import BaseSettings
import os
import pathlib
import dotenv
from logging.config import dictConfig
from .logger import LogConfig
from fastapi import WebSocket


dictConfig(LogConfig().dict())


dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_path=dotenv_file, override=True)



BASE_DIR = pathlib.Path(__file__).parent.parent
env_path = BASE_DIR / '.env'

class Settings(BaseSettings):
    debug: bool = os.getenv('DEBUG', default=True)
    redis_url: str = os.getenv('REDIS_URL')
    bucket_token: str = os.getenv('BUCKET_TOKEN')
    bucket_value: str = os.getenv('BUCKET_VALUE')
    bucket_name: str = os.getenv('BUCKET_NAME')
    postgres_url: str = os.getenv('POSTGRES_URL')
    endpoint_url: str = os.getenv('ENDPOINT_URL')

settings = Settings()