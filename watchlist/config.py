from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    username: str = "用户名"
    email: EmailStr = "example@123.com"
    password: str = "123456"
    # fastapi docs
    envir: str = "dev"  # {dev, prod}

    class Config:
        env_file = ".env"


settings = Settings()
