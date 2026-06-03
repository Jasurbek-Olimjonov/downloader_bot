import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Any

import aiohttp
import yt_dlp
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from config import conf
from database import User

JS_RUNTIME = {'node': {'path': conf.web.node}}

async def register(user, state: FSMContext):
    lan_code = await state.get_value('locale', user.language_code)
    user_data = {
        'id': user.id,
        'lan_code': lan_code,
    }
    status = await User.get(user.id)
    if status is None:
        await User.create(**user_data)


def get_info(url: str):
    opts: Any = {
        'quiet': True,
        'js_runtimes': JS_RUNTIME,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False)


def download_video(url: str, output_path: str):
    ydl_opts: Any = {
        'format': 'bestvideo[filesize<1G]+bestaudio[filesize<1G]/best[filesize<1G]',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
        'js_runtimes': JS_RUNTIME,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def download_audio(url: str, output_path: str):
    ydl_opts: Any = {
        'format': 'bestaudio/best[filesize<1G]',
        'outtmpl': output_path,
        'js_runtimes': JS_RUNTIME,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }
    # noinspection PyTypeChecker
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


async def if_image(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.head(url) as resp:
            content_type = resp.headers.get("Content-Type", '')
            return content_type.startswith('image/')


async def download_image(url: str, path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return True
            with open(path, 'wb') as f:
                f.write(await resp.read())
                return None


def setup_logger():
    os.makedirs('logs', exist_ok=True)
    if not os.path.exists('logs/errors.log'):
        with open('logs/errors.log', 'w') as f:
            f.write('Bismillah\n')
    logger = logging.getLogger('bot')
    logger.setLevel(logging.ERROR)
    handler = RotatingFileHandler(
        'logs/errors.log',
        maxBytes=5 * 1024 * 1024,
        backupCount=4,
        encoding='utf-8'
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(handler)

    return logger


log = setup_logger()


async def bot_settings(bot: Bot):
    command = [BotCommand(command='start', description='start')]

    await bot.set_my_commands(command, scope=BotCommandScopeAllPrivateChats())
    # await bot.set_my_commands(command, scope=BotCommandScopeAllGroupChats())
    # await bot.set_my_name('Free Downloader')
    # path = os.path.join(os.getcwd(), 'logo.jpg')
    # photo = FSInputFile(path)
    # await bot.set_my_profile_photo(InputProfilePhotoStatic(photo=photo))
    # await bot.set_my_description(
    #     description="This bot helps you download videos and audios from any platform",
    #     language_code="en")
    # await bot.set_my_description(
    #     description=("Абсолютно бесплатно - скачивайте что угодно и где угодно\n" +
    #                  "Если вы обнаружили ошибку, свяжитесь с нами:\n" +
    #                  "@all_problems_here_bot\n"),
    #     language_code="ru")
    # await bot.set_my_description(
    #     description=("Mutlaqo bepul - istalgan narsani, istalgan joyda yuklab oling\n" +
    #                  "Agar xatolik topsangiz, biz bilan bog'laning:\n" +
    #                  "@all_problems_here_bot\n"),
    #     language_code="uz")
    # await bot.set_my_description(
    #     description=("완전 무료 - 어디서든 무엇이든 다운로드하세요\n" +
    #                  "오류를 발견하시면 저희에게 연락해 주세요:\n" +
    #                  "@all_problems_here_bot\n"),
    #     language_code="ko")
    # await bot.set_my_short_description("Other services: t.me/all_free_services\n" +
    #                                    "Complaints: @all_problems_here_bot\n")
