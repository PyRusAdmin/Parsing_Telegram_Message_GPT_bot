from loguru import logger  # https://github.com/Delgan/loguru

from account_manager.auth import CheckingAccountsValidity
from database.personal_tracking import get_user_accounts
from handlers.user_language import determines_user_language
from keyboards.keyboards import menu_launch_tracking_keyboard
from locales.locales import t


async def find_session_file(user_id: int, message):
    """
    Получает валидную StringSession из базы данных пользователя.

    :param user_id: (int) ID пользователя Telegram
    :param message: (aiogram.types.Message) Для отправки ответа
    :return: dict с данными аккаунта {"session_string": str, "phone": str} или None
    """
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=message.from_user.id)

    # Получаем все аккаунты пользователя из его персональной таблицы
    accounts = get_user_accounts(user_id)

    if not accounts:
        logger.warning(f"⚠️ У пользователя {user_id} нет подключённых аккаунтов в БД")
        await message.answer(
            t("no_accounts", lang=user_lang),
            reply_markup=menu_launch_tracking_keyboard()
        )
        return None

    logger.info(f"📦 Найдено {len(accounts)} аккаунтов в БД для пользователя {user_id}")
    # Подключеный аккаунт пользователя
    session_string = accounts["session_string"]

    checker = CheckingAccountsValidity()
    await checker.verify_account(session_name=session_string, user_id=user_id, user_lang=user_lang)

    logger.success(f"✅ Выбрана сессия: {session_string} (первые 30 символов: {session_string[:30]}...)")

    return {
        "session_string": session_string,
    }
