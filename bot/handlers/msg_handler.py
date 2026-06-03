import glob
import os
from asyncio import get_event_loop
from concurrent.futures import ThreadPoolExecutor

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User, FSInputFile
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from yt_dlp.utils import DownloadError

from bot.buttons import about_bot, settings, language, format_keyboard
from bot.calls.calls import register, get_info, log, if_image, download_image
from bot.calls.filters import IsURL
from bot.calls.states import URL
from config import conf
from database import User as Users

message_router = Router()
message_router.message.filter(F.from_user.as_("user"))


@message_router.message(CommandStart())
async def starter(message: Message, user: User, state: FSMContext):
    await register(user, state)
    await message.answer(_('Welcome, {}').format(user.full_name), reply_markup=about_bot())


@message_router.message(F.text == __("Settings ⚙️"))
async def settings_handler(message: Message):
    await message.answer(_('Settings ⚙️'), reply_markup=settings())


@message_router.message(F.text == __("Back 🔙"))
async def back_handler(message: Message, user: User):
    await message.answer(_('Welcome, {}').format(user.full_name), reply_markup=about_bot())


@message_router.message(F.text == __("Language 🌐"))
async def language_handler(message: Message, user: User):
    this = await Users.get(user.id)
    lan = this.lan_code
    await message.answer(_("Language 🌐"), reply_markup=language(lan))


@message_router.message(F.text == __("About 🤖"))
async def about_handler(message: Message):
    await message.answer(_("This bot is to help you download\nvideos and audios from these platforms:"
                           "\nInstagram 📸,\nYouTube ▶️\nTik-Tok 🎥\nothers....\n"
                           "Just send me the url of the content"))


@message_router.message(IsURL())
async def handle_url(message: Message, state: FSMContext, user: User):
    url = str(message.text)
    await state.set_state(URL.waiting)
    await state.update_data(url=url)
    if await if_image(url):
        path = os.path.join(os.getcwd(), f'media/image_{user.id}.jpg')
        if await download_image(url, path):
            await message.answer(_("❌ Failed to fetch image\n"
                                   "Please check the URL and try again later"))
            log.error(f"\n❌ Failed to fetch image | user={user.full_name}\nurl={url}")
            return

        await message.answer_photo(FSInputFile(path), caption=_("Where did you obtain: @{}").format(conf.bot.username))
        for file in glob.glob(f"{path}"):
            os.remove(file)

    executor = ThreadPoolExecutor(max_workers=10)
    try:
        info = await get_event_loop().run_in_executor(executor, get_info, url)
    except DownloadError as e:
        log.error(f"\n❌ Failed to fetch content | user={user.full_name}\nurl={url} | error={e}")
        await message.answer(_("❌ Failed to fetch content\n"
                               "Please check the URL and try again later"))
        return

    thumbnail = info.get('thumbnail', '')
    title = info.get('title', 'Unknown')
    duration = info.get('duration_string', '')

    await message.answer_photo(
        photo=thumbnail,
        caption=f"🎬 <b>{title}</b>\n⏱ {duration}",
        reply_markup=format_keyboard(),
        parse_mode="HTML"
    )
