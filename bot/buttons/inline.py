from aiogram.types import InlineKeyboardButton
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder


def language(lan_code):
    kb = InlineKeyboardBuilder()
    lan_list = ['en', 'uz', 'ko', 'ru']

    buttons = []
    for lan in lan_list:
        if lan == lan_code:
            buttons.append(InlineKeyboardButton(text=f"{lan} ✅", callback_data=f"choose_{lan}"))
        else:
            buttons.append(InlineKeyboardButton(text=lan, callback_data=f"choose_{lan}"))

    kb.row(*buttons)
    return kb.as_markup()


def format_keyboard():
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(text=_("Video"), callback_data="format_video"),
        InlineKeyboardButton(text=_("Audio"), callback_data="format_audio")
    )

    return kb.as_markup()


def clear():
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(text=_("Clear memory"), callback_data="clear_memory"),
    )

    return kb.as_markup()
