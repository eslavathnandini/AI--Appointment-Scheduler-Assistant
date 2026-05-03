from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    ocr_api_key: str
    openai_api_key: Optional[str] = None
    timezone: str = "Asia/Kolkata"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()