from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parent / ".env"

class Settings(BaseSettings):
    database_url: str
    base_url: str = "http://localhost:8080"   # participant UI; used if .env has no BASE_URL


    model_config = SettingsConfigDict(env_file=ENV_FILE)

settings = Settings()