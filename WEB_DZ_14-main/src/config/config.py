from typing import Any

from pydantic import ConfigDict, field_validator, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://postgres:567234@localhost:5432/hw_11"
    SECRET_KEY_JWT: str = "974790aec4ac460bdc11645decad4dce7c139b7f2982b7428ec44e886ea588c6"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: EmailStr = "phenixua@meta.ua"
    MAIL_PASSWORD: str = "Phenix4625"
    MAIL_FROM: str = "phenixua@meta.ua"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.meta.ua"
    REDIS_DOMAIN: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    CLOUDINARY_NAME: str = 'deh9rrzak'
    CLOUDINARY_API_KEY: int = 427453781169512
    CLOUDINARY_API_SECRET: str = "MpkraDG6XpeLcJgL0u4GjRkM4dw"

    # валідація власних параметрів
    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v: Any):
        if v not in ["HS256", "HS512"]:
            raise ValueError("algorithm must be HS256 or HS512")
        return v

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")  # noqa


config = Settings()