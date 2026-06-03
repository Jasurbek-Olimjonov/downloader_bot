import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv('.env')


@dataclass
class PostgresConfig:
    PG_USER: str = os.getenv('PG_USER')
    PG_PASS: str = os.getenv('PG_PASS')
    PG_HOST: str = os.getenv('PG_HOST', 'localhost')
    PG_PORT: str = os.getenv('PG_PORT', '5432')
    PG_DB: str = os.getenv('PG_DB')

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.PG_USER}:{self.PG_PASS}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"


@dataclass
class BotConfig:
    bot: str = os.getenv('BOT_TOKEN')
    owner: str = os.getenv('OWNER')


@dataclass
class Configuration:
    database = PostgresConfig()
    bot = BotConfig()


conf = Configuration()
