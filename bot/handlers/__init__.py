from aiogram import Router

from bot.handlers.msg_handler import message_router
from bot.handlers.query_handler import query_router
from bot.handlers.admin import owner_router

main_router = Router()

main_router.include_routers(
owner_router,
    message_router,
    query_router
)
