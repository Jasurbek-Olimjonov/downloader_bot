from aiogram.types import KeyboardButton
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def about_bot(status=None):
    kb = ReplyKeyboardBuilder()
    if status:
        kb.row(KeyboardButton(text=_("Users")),
               KeyboardButton(text=_("Documents 📝")))
    kb.row(
        KeyboardButton(text=_('About 🤖')),
        KeyboardButton(text=_('Settings ⚙️')),
        width=2
    )

    return kb.as_markup(resize_keyboard=True)


def settings(*, lan_code=None, status=None):
    kb = ReplyKeyboardBuilder()
    kb.row(
        KeyboardButton(text=_('Language 🌐', locale=lan_code)),
        KeyboardButton(text=_("Back 🔙", locale=lan_code)),
    )
    if status:
        kb.row(
            KeyboardButton(text=_("Check memory 📝", locale=lan_code)),
        )

    return kb.as_markup(resize_keyboard=True)


def documents():
    kb = ReplyKeyboardBuilder()
    kb.row(
        KeyboardButton(text=_("Logs ⚠️")),
        KeyboardButton(text=_("Toml 🔃")),
        KeyboardButton(text=_("Back 🔙")),
        width=2
    )

    return kb.as_markup(resize_keyboard=True)
