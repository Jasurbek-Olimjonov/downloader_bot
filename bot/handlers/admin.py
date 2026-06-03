import os

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, User, FSInputFile
from aiogram.utils.i18n import gettext as _, lazy_gettext as __

from bot.buttons import about_bot, settings, clear, documents
from bot.calls import states
from bot.calls.filters import IsOwner
from database import User as Users

owner_router = Router()

owner_router.message.filter(IsOwner())
owner_router.callback_query.filter(IsOwner())
owner_router.message.filter(F.from_user.as_("user"))


@owner_router.message(CommandStart())
async def starter(message: Message, user: User):
    await message.answer(_("Welcome, {}").format(user.full_name), reply_markup=about_bot('0'))


@owner_router.message(F.text == __("Users"))
async def users(message: Message):
    amount = await Users.get_all()
    await message.answer(_("Currently {} users are utilizing our bot").format(len(amount)))


@owner_router.message(F.text == __("Back 🔙"))
async def back_handler(message: Message, user: User):
    await message.answer(_('Welcome, {}').format(user.full_name), reply_markup=about_bot('0'))


@owner_router.message(F.text == __("Settings ⚙️"))
async def admin_settings(message: Message):
    await message.answer(_("Settings ⚙️"), reply_markup=settings(status='832'))


@owner_router.message(F.text == __("Check memory 📝"))
async def memory_check(message: Message):
    status = states.status
    status = 'active' if status is True else 'idle'
    files = os.listdir('media/')
    key = [clear(), None][len(files) == 0]
    await message.answer(_("Current exist files :{len}\n"
                           "Current status: {status}").format(len=len(files), status=status),
                         reply_markup=key)


@owner_router.message(F.text == __("Documents 📝"))
async def document_check(message: Message):
    await message.answer(_("Documents 📝"), reply_markup=documents())


@owner_router.message(F.text == __("Logs ⚠️"))
async def log_check(message: Message):
    file = os.path.join(os.getcwd(), 'logs/errors.log')
    need = os.path.join(os.getcwd(), 'logs/errors.txt')
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
    with open(need, 'w', encoding='utf-8') as f:
        f.write(text)
    os.remove(need)
    await message.answer_document(FSInputFile(need))


@owner_router.message(F.text == __("Toml 🔃"))
async def toml_check(message: Message):
    file = os.path.join(os.getcwd(), 'pyproject.toml')
    need = os.path.join(os.getcwd(), 'toml.txt')
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
    with open(need, 'w', encoding='utf-8') as f:
        f.write(text)
    os.remove(need)
    await message.answer_document(FSInputFile(need))
