# -*- coding: utf-8 -*-
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger  # https://github.com/Delgan/loguru

from account_manager.auth import CheckingAccountsValidity
from system.dispatcher import router


@router.message(F.text == "✅ Проверка аккаунтов")
async def checking_accounts_handler(message: Message, state: FSMContext):
    """✅ Проверка аккаунтов на валидность"""
    try:
        await state.clear()  # Сбрасываем текущее состояние FSM

        path_accounts = [
            "accounts/parsing",  # Путь к папке с сессиями
            "accounts/ai",  # Путь к папке с сессиями
            "accounts/free",  # Путь к папке с сессиями
            "accounts/parsing_grup"  # Путь к папке с сессиями
        ]

        for path in path_accounts:
            logger.info(f"✅ Проверка аккаунтов в папке {path}")
            # ✅ Проверка аккаунтов на валидность
            checker = CheckingAccountsValidity(message=message, path=path)
            available_sessions = await checker.checking_accounts()
            await message.answer(
                f"🔍 Найдено аккаунтов: {len(available_sessions)} в папке {path}\n"
                f"📱 Аккаунты: {', '.join([s.split('/')[-1] for s in available_sessions])}"
            )
        await message.answer(
            "✅ Проверка аккаунтов завершена"
        )

    except Exception as e:
        logger.exception(e)


def register_checking_accounts():
    """Регистрация обработчика для проверки аккаунтов на валидность"""
    router.message.register(checking_accounts_handler)
