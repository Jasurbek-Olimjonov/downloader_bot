import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv('.env')


@dataclass
class PostgresConfig:
    PG_USER: str = os.getenv('PG_USER')
    PG_PASS: str = os.getenv('PG_PASS')
    PG_HOST: str = os.getenv('PG_HOST')
    PG_PORT: str = os.getenv('PG_PORT')
    PG_DB: str = os.getenv('PG_DB')

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.PG_USER}:{self.PG_PASS}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"


@dataclass
class BotConfig:
    bot: str = os.getenv('BOT_TOKEN')
    owner: str = os.getenv('OWNER')


@dataclass
class WebConfig:
    url: str = os.getenv("WEB_URL")
    host: str = os.getenv("WEB_HOST")
    port: str = os.getenv("WEB_PORT")
    secret: str = os.getenv("WEB_SECRET")
    path: str = os.getenv("WEB_PATH")



@dataclass
class Configuration:
    database = PostgresConfig()
    bot = BotConfig()
    web = WebConfig()

conf = Configuration()
