import asyncio
import glob
import logging
import os

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from redis.asyncio import Redis

from bot.calls.calls import bot_settings
from bot.calls.middlewares import CheckI18nLanCode
from bot.handlers import main_router
from config import conf
from database.base import db

redis = Redis(host='localhost', port=6379)
storage = RedisStorage(redis=redis)
dp = Dispatcher(storage=storage)


@dp.startup()
async def startup(bot: Bot):
    await db.create_all()
    os.makedirs('media', exist_ok=True)
    os.makedirs('locales', exist_ok=True)
    await bot.send_message(chat_id=conf.bot.owner, text='Bot started')


@dp.shutdown()
async def shutdown(bot: Bot):
    for file in glob.glob("media/*"):
        os.remove(file)
    await bot.send_message(chat_id=conf.bot.owner, text='Bot stopped')
    await bot.session.close()


async def main():
    bot = Bot(token=conf.bot.bot)
    await bot_settings(bot)
    i18n = I18n(path='locales')
    dp.update.outer_middleware.register(CheckI18nLanCode(i18n=i18n))
    dp.include_router(main_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
