import asyncio
import glob
import logging
import os

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from redis.asyncio import Redis

from bot.calls.calls import bot_settings
from bot.calls.middlewares import CheckI18nLanCode
from bot.handlers import main_router
from config import conf
from database.base import db

redis = Redis(host='localhost', port=6379)
storage = RedisStorage(redis=redis)
dp = Dispatcher(storage=storage)
TOKEN = conf.bot.bot
WEB_SERVER_HOST = conf.web.host
WEB_SERVER_PORT = conf.web.port
WEBHOOK_PATH = conf.web.path
WEBHOOK_SECRET = conf.web.secret
BASE_WEBHOOK_URL = conf.web.url

@dp.startup()
async def startup(bot: Bot):
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)
    await bot_settings(bot)
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
    i18n = I18n(path='locales')
    dp.update.outer_middleware.register(CheckI18nLanCode(i18n=i18n))
    dp.include_router(main_router)
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
    await site.start()

    await asyncio.Event().wait()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
