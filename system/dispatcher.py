# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage

from core.config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()

dp = Dispatcher(storage=storage)

# ID администраторов бота с особыми привилегиями
ADMIN_USER_ID = (535185511, 7181118530)

router = Router()
dp.include_router(router)
