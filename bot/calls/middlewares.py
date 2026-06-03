from typing import Any

from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18nMiddleware

from database.models.users import User


class CheckI18nLanCode(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: dict[str, Any]) -> str:
        from_user = data.get('event_from_user')
        if not from_user:
            return self.i18n.default_locale

        user = await User.get(from_user.id)
        if user:
            return user.lan_code
        return self.i18n.default_locale
