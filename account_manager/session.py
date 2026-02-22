# account_manager/parser.py (или где у вас эта функция)
import random

from loguru import logger
from telethon.sessions import StringSession

from database.database import get_user_accounts
from keyboards.user.keyboards import menu_launch_tracking_keyboard


async def find_session_file(user_id: int, user, message):
    """
    Получает валидную StringSession из базы данных пользователя.

    :param user_id: (int) ID пользователя Telegram
    :param user: (User) Модель пользователя из БД (для языка и уведомлений)
    :param message: (aiogram.types.Message) Для отправки ответа
    :return: dict с данными аккаунта {"session_string": str, "phone": str} или None
    """
    try:
        # 🔹 Получаем все аккаунты пользователя из его персональной таблицы
        accounts = get_user_accounts(user_id)

        if not accounts:
            logger.warning(f"⚠️ У пользователя {user_id} нет подключённых аккаунтов в БД")
            await message.answer(
                "❌ У вас нет подключённых аккаунтов.\n\n"
                "Отправьте файл сессии `.session` или нажмите «Подключение аккаунта» в меню.",
                reply_markup=menu_launch_tracking_keyboard()
            )
            return None

        logger.info(f"📦 Найдено {len(accounts)} аккаунтов в БД для пользователя {user_id}")

        # 🔹 Случайным образом выбираем один аккаунт (можно изменить логику выбора)
        selected_account = random.choice(accounts)
        session_string = selected_account["session_string"]
        phone = selected_account["phone_number"]

        # 🔹 Быстрая проверка валидности StringSession (опционально, но рекомендуется)
        if not await _is_session_valid(session_string):
            logger.warning(f"⚠️ Сессия {phone} не валидна — удаляем из БД")
            await message.answer(
                f"⚠️ Аккаунт `{phone}` больше не действителен.\n"
                f"Пожалуйста, подключите аккаунт заново.",
                reply_markup=menu_launch_tracking_keyboard()
            )
            # 🔹 Удаляем невалидную сессию из БД
            from database.database import delete_user_account
            delete_user_account(user_id, session_string)
            # 🔹 Рекурсивно пробуем найти другой аккаунт
            return await find_session_file(user_id, user, message)

        logger.success(f"✅ Выбрана сессия: {phone} (первые 30 символов: {session_string[:30]}...)")

        return {
            "session_string": session_string,
            "phone_number": phone
        }

    except Exception as e:
        logger.exception(f"❌ Ошибка получения аккаунта из БД для пользователя {user_id}: {e}")
        await message.answer(
            "⚠️ Произошла ошибка при получении аккаунта. Попробуйте позже.",
            reply_markup=menu_launch_tracking_keyboard()
        )
        return None


async def _is_session_valid(session_string: str) -> bool:
    """
    Быстрая проверка валидности StringSession без полноценного подключения.

    :param session_string: Строка сессии Telethon
    :return: True если сессия выглядит валидной, False если нет
    """
    from telethon import TelegramClient
    from core.config import api_id, api_hash

    # 🔹 Простая проверка: сессия не должна быть пустой и должна иметь правильный формат
    if not session_string or len(session_string) < 50:
        return False

    # 🔹 Пробуем создать клиент и подключиться (быстрый тест)
    client = TelegramClient(StringSession(session_string), api_id, api_hash)

    try:
        await client.connect()
        is_authorized = await client.is_user_authorized()
        await client.disconnect()
        return is_authorized
    except Exception as e:
        logger.debug(f"⚠️ Проверка сессии не прошла: {type(e).__name__}")
        try:
            await client.disconnect()
        except:
            pass
        return False