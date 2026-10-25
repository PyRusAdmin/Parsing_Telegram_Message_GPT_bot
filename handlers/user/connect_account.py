import random
from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger  # https://github.com/Delgan/loguru
from telethon.sessions import StringSession

from account_manager.auth import CheckingAccountsValidity, get_account_info
from database.database import User, AccountFree
from database.personal_tracking import write_account_to_db
from handlers.user_language import determines_user_language
from keyboards.keyboards import back_keyboard
from locales.locales import t
from states.states import MyStates

router = Router(name=__name__)


async def connect_account_free_internal(message: Message, user_tg, state: FSMContext):
    """Подключает случайный свободный аккаунт пользователю"""
    await state.clear()

    user, created = User.get_or_create(
        user_id=user_tg.id,
        defaults={
            "username": user_tg.username,
            "first_name": user_tg.first_name,
            "last_name": user_tg.last_name,
            "language": "unset"
        }
    )
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=message.from_user.id)

    free_accounts = list(AccountFree.select())
    if not free_accounts:
        logger.warning(f"Нет доступных свободных аккаунтов для пользователя {user.user_id}")
        await message.answer(
            text=t("no_free_accounts", lang=user_lang),
            reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
        )
        return

    selected_account = random.choice(free_accounts)
    session_string = selected_account.session_string
    phone_number = selected_account.phone_number

    logger.info(f"Подключаем свободный аккаунт {phone_number} пользователю {user.user_id}")

    write_account_to_db(
        session_string=session_string,
        user_id=user.user_id
    )

    selected_account.delete_instance()

    await message.answer(
        text=t("account_connected_free", lang=user_lang),
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
    )


# @router.message((F.text == t('connect_free_account_button', 'ru')) | (F.text == t('connect_free_account_button', 'en')))
# async def handle_connect_account_free(message: Message, state: FSMContext):
#     """
#     Обработчик команды "🔐 Подключить свободный аккаунт" (текст).
#     """
#     await connect_account_free_internal(message, message.from_user, state)


@router.callback_query(F.data == "account_connect_free")
async def handle_connect_account_free_cb(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн-кнопки "🔐 Подключить свободный аккаунт".
    """
    await callback.answer()
    await connect_account_free_internal(callback.message, callback.from_user, state)


def creates_temporary_folder_for_accounts():
    """
    Создание временной папки для аккаунтов пользователя.
    :return:
    """
    sessions_dir = Path("accounts")
    sessions_dir.mkdir(parents=True, exist_ok=True)
    return sessions_dir


def sanitization_file_name(document, sessions_dir):
    """
    Очистка имени файла от недопустимых символов (файлов сессии).
    :return:
    """
    safe_file_name = "".join(c for c in document.file_name if c.isalnum() or c in "._-")
    local_file_path = sessions_dir / safe_file_name
    return local_file_path, safe_file_name


async def connect_account_internal(message: Message, user_tg, state: FSMContext):
    """Запрашивает у пользователя файл сессии для подключения аккаунта"""
    await state.clear()
    user, created = User.get_or_create(
        user_id=user_tg.id,
        defaults={
            "username": user_tg.username,
            "first_name": user_tg.first_name,
            "last_name": user_tg.last_name,
            "language": "unset"
        }
    )
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=message.from_user.id)
    await message.answer(
        text=t("connect_account", lang=user_lang),
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
    )
    await state.set_state(MyStates.waiting_for_session_file_user)


@router.callback_query(F.data.in_({"settings_connect_account", "account_connect"}))
async def handle_connect_account_cb(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает команду подключения аккаунта (инлайн)"""
    await callback.answer()
    await connect_account_internal(callback.message, callback.from_user, state)


# ✅ Фильтр: только документы И только в нужном состоянии
@router.message(MyStates.waiting_for_session_file_user, F.document)
async def handle_account_file(message: Message, state: FSMContext):
    """Обработчик приёма файла сессии (.session) от пользователя"""
    local_file_path = None  # для безопасного удаления в finally

    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=message.from_user.id)

    try:
        logger.info(f"User {message.from_user.id} отправил файл: {message.document.file_name}")

        # ✅ Проверяем расширение — если не .session, остаёмся в состоянии
        if not message.document.file_name.endswith('.session'):
            await message.answer(t("invalid_session_file", lang=user_lang))
            return  # state НЕ сбрасываем — ждём правильный файл

        sessions_dir = creates_temporary_folder_for_accounts()
        local_file_path, safe_file_name = sanitization_file_name(message.document, sessions_dir)

        await message.bot.download(message.document, destination=local_file_path)
        logger.info(f"✅ Файл скачан: {local_file_path}")

        await message.answer(t("session_file_received", lang=user_lang, filename=safe_file_name))

        session_path_without_ext = str(local_file_path.with_suffix(""))

        checker = CheckingAccountsValidity(path=session_path_without_ext)
        client = await checker.connect_client()

        if client:
            account_info = await get_account_info(client)
            phone = account_info["phone"] or "unknown"
            first_name = account_info["first_name"] or ""

            session_string = StringSession.save(client.session)
            write_account_to_db(
                session_string=session_string,
                user_id=message.from_user.id
            )
            await client.disconnect()

            logger.success(f"✅ Сессия добавлена: {phone} | {first_name}")
            await message.answer(
                t("session_connected_success", lang=user_lang, filename=safe_file_name, phone=phone,
                  name=first_name),
                parse_mode="HTML"
            )
        else:
            logger.warning(f"❌ Сессия {safe_file_name} не валидна для пользователя {message.from_user.id}")
            await message.answer(
                t("session_validation_failed", lang=user_lang, filename=safe_file_name),
                parse_mode="HTML"
            )

    except Exception as e:
        logger.exception(f"Ошибка при обработке сессии пользователя {message.from_user.id}: {e}")
        await message.answer(t("session_check_error", lang=user_lang))

    finally:
        # ✅ Удаляем временный файл в любом случае
        if local_file_path and local_file_path.exists():
            try:
                local_file_path.unlink()
            except Exception as e:
                logger.warning(f"Could not delete session file {local_file_path}: {e}")
        # ✅ Сбрасываем состояние только в конце
        await state.clear()
