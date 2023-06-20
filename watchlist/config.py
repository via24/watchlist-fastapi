import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    database_url: str = os.getenv("DB_URL")
    secret_key: str = os.getenv("SECRET_KEY")

    class Config:
        env_file = ".env"


settings = Settings()
