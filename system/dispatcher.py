# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage

from core.config import BOT_TOKEN, PROXY_USER, PROXY_PASSWORD, PROXY_IP, PROXY_PORT

storage = MemoryStorage()

session = AiohttpSession(
    proxy=f"http://{PROXY_USER}:{PROXY_PASSWORD}@{PROXY_IP}:{PROXY_PORT}"
)  # Используется HTTP-прокси с аутентификацией для обхода блокировок

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(),  # Применение стандартных свойств бота (например, parse_mode)
    session=session  # Подключение сессии с прокси для работы бота
)

dp = Dispatcher(storage=storage)

# ID администраторов бота с особыми привилегиями
ADMIN_USER_ID = (535185511, 743541086)

# router = Router()
# dp.include_router(router)
