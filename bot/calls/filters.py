from aiogram.filters import Filter
from aiogram.types import Message

from config import conf


class IsURL(Filter):
    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        return message.text.startswith(('https://', 'http://'))


class IsOwner(Filter):
    async def __call__(self, message: Message) -> bool:
        assert message.from_user
        if message.from_user.id == int(conf.bot.owner):
            return True
        return False
