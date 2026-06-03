import asyncio
import glob
import os
import time
from asyncio import get_event_loop
from concurrent.futures import ThreadPoolExecutor

from aiogram import Router, F, Bot
from aiogram.enums import ChatAction
from aiogram.exceptions import TelegramNetworkError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, User, FSInputFile
from aiogram.utils.i18n import gettext as _
from yt_dlp.utils import DownloadError

from bot.buttons import settings
from bot.calls import states
from bot.calls.calls import download_video, download_audio, log
from database import User as Users

query_router = Router()
query_router.callback_query.filter(F.from_user.as_("user"))


@query_router.callback_query(F.data.startswith('choose_'))
async def choose_handler(query: CallbackQuery, user: User):
    assert query.data
    assert query.message
    lan_code = query.data.removeprefix('choose_')
    await Users.update(user.id, lan_code=lan_code)
    await query.answer(_("Chosen", locale=lan_code))
    await query.message.answer(_("Welcome, {}", locale=lan_code).format(user.full_name),
                               reply_markup=settings(lan_code=lan_code))
    await query.message.delete()


@query_router.callback_query(F.data == 'format_video')
async def download_handler(query: CallbackQuery, state: FSMContext, user: User, bot: Bot):
    data = await state.get_data()
    states.status = True
    url = data['url']
    assert query.data
    bot_user = bot._me.username
    assert query.message
    await query.message.edit_caption(caption=_('⌛ Downloading...'))
    path = os.path.join(os.getcwd(), f'media/{user.id}_{int(time.time())}')
    try:
        await bot.send_chat_action(user.id, action=ChatAction.RECORD_VIDEO)
        executor = ThreadPoolExecutor(max_workers=10)
        try:
            await get_event_loop().run_in_executor(executor, download_video, url, f"{path}.%(ext)s")
        except DownloadError as e:
            await query.message.answer(_("No suitable format found under 1GB\n"
                                         "Please try something smaller"))
            log.error(f"Failed to download file | user={user.full_name}\nurl={url} | error={e}")
        actual = glob.glob(f"{path}.*")[0]
        await bot.send_chat_action(user.id, action=ChatAction.UPLOAD_VIDEO)
        for attempt in range(3):
            try:
                await query.message.answer_video(FSInputFile(actual),
                                                 caption=_("Where did you obtain: @{}").format(bot_user))
                break
            except TelegramNetworkError as e:
                if attempt == 2:
                    log.error(f"\n❌ Failed to send file | user={user.full_name}\nurl={url} | error={e}")
                    await query.message.answer(_("❌ Failed to send file. Please try again."))
                await asyncio.sleep(2)
        states.status = False

    finally:
        for file in glob.glob(f"{path}.*"):
            os.remove(file)
        states.status = False
        await state.clear()


@query_router.callback_query(F.data == 'format_audio')
async def audio_downloader(query: CallbackQuery, state: FSMContext, user: User, bot: Bot):
    data = await state.get_data()
    states.status = True
    url = data['url']
    assert query.data
    bot_user = bot._me.username
    assert query.message
    await query.message.edit_caption(caption=_('⌛ Downloading...'))
    path = os.path.join(os.getcwd(), f'media/{user.id}_{int(time.time())}')
    try:
        await bot.send_chat_action(user.id, action=ChatAction.RECORD_VOICE)
        executor = ThreadPoolExecutor(max_workers=10)
        try:
            await get_event_loop().run_in_executor(executor, download_audio, url, f"{path}.%(ext)s")
        except DownloadError as e:
            await query.message.answer(_("No suitable format found under 1GB\n"
                                         "Please try something smaller"))
            log.error(f"Failed to download file | user={user.full_name}\nurl={url} | error={e}")
        actual = glob.glob(f"{path}.*")[0]
        await bot.send_chat_action(user.id, action=ChatAction.UPLOAD_VOICE)
        for attempt in range(3):
            try:
                await query.message.answer_audio(FSInputFile(actual),
                                                 caption=_("Where did you obtain: @{}").format(bot_user))
                break
            except TelegramNetworkError as e:
                if attempt == 2:
                    log.error(f"\n❌ Failed to send file | user={user.full_name}\nurl={url} | error={e}")
                    await query.message.answer(_("❌ Failed to send file. Please try again."))
                await asyncio.sleep(2)
        states.status = False

    finally:
        for file in glob.glob(f"{path}.*"):
            os.remove(file)
    states.status = False
    await state.clear()


@query_router.callback_query(F.data == 'clear_memory')
async def memory_cleaner(query: CallbackQuery):
    for file in os.listdir('media/'):
        os.remove(os.path.join(os.getcwd(), f'media/{file}'))
    await query.answer(_("Done ✅"))
