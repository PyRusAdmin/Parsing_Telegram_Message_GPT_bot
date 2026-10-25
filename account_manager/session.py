import random

from loguru import logger  # https://github.com/Delgan/loguru
from telethon import TelegramClient
from telethon.sessions import StringSession

from core.config import API_ID, API_HASH
from database.database import delete_account_from_db, get_user_accounts
from handlers.user_language import determines_user_language
from keyboards.keyboards import menu_launch_tracking_keyboard
from locales.locales import t


async def find_session_file(user_id: int, user, message):
    """
    Получает валидную StringSession из базы данных пользователя.

    :param user_id: (int) ID пользователя Telegram
    :param user: (User) Модель пользователя из БД (для языка и уведомлений)
    :param message: (aiogram.types.Message) Для отправки ответа
    :return: dict с данными аккаунта {"session_string": str, "phone": str} или None
    """
    try:
        # Получаем все аккаунты пользователя из его персональной таблицы
        accounts = get_user_accounts(user_id)

        # Определяем язык пользователя, который пользователь выбрал при старте бота
        user_lang = determines_user_language(message_or_callback=message.from_user.id)

        if not accounts:
            logger.warning(f"⚠️ У пользователя {user_id} нет подключённых аккаунтов в БД")
            await message.answer(
                t("no_accounts", lang=user_lang),
                reply_markup=menu_launch_tracking_keyboard()
            )
            return None

        logger.info(f"📦 Найдено {len(accounts)} аккаунтов в БД для пользователя {user_id}")

        # Случайным образом выбираем один аккаунт (можно изменить логику выбора)
        selected_account = random.choice(accounts)
        session_string = selected_account["session_string"]
        phone = selected_account["phone_number"]

        # Быстрая проверка валидности StringSession (опционально, но рекомендуется)
        if not await _is_session_valid(session_string):
            logger.warning(f"⚠️ Сессия {phone} не валидна — удаляем из БД")
            # Если аккаунт не валидный, то удаляем не валидный аккаунт из базы данных, персональной таблицы пользователя
            delete_account_from_user_table(user_id, session_string)
            await delete_account_from_db(session_string)
            await message.answer(
                t("session_invalid", lang=user_lang, phone=phone),
                reply_markup=menu_launch_tracking_keyboard()
            )

            # Рекурсивно пробуем найти другой аккаунт
            return await find_session_file(user_id, user, message)

        logger.success(f"✅ Выбрана сессия: {phone} (первые 30 символов: {session_string[:30]}...)")

        return {
            "session_string": session_string,
            "phone_number": phone
        }

    except Exception as e:
        logger.exception(f"❌ Ошибка получения аккаунта из БД для пользователя {user_id}: {e}")
        await message.answer(
            t("account_fetch_error", lang=user_lang),
            reply_markup=menu_launch_tracking_keyboard()
        )
        return None


async def _is_session_valid(session_string: str) -> bool:
    """
    Быстрая проверка валидности StringSession без полноценного подключения.

    :param session_string: Строка сессии Telethon
    :return: True если сессия выглядит валидной, False если нет
    """

    # Простая проверка: сессия не должна быть пустой и должна иметь правильный формат
    if not session_string or len(session_string) < 50:
        return False

    # Пробуем создать клиент и подключиться (быстрый тест)
    client = TelegramClient(StringSession(session_string), API_ID, API_HASH)

    try:
        await client.connect()
        is_authorized = await client.is_user_authorized()
        await client.disconnect()
        return is_authorized
    except Exception as e:
        logger.exception(f"⚠️ Проверка сессии не прошла: {type(e).__name__}")
        try:
            await client.disconnect()
        except Exception as e:
            logger.exception(e)
        return False
