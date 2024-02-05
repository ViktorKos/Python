import logging


class Config:
    DB_URL = "postgresql+asyncpg://postgres:567234@localhost:5432/hw_11"
    LOG_LEVEL = logging.DEBUG


config = Config()
