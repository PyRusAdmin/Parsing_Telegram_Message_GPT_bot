# -*- coding: utf-8 -*-
import os
import random
import shutil
from pathlib import Path

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger
from telethon.sessions import StringSession

from account_manager.auth import CheckingAccountsValidity, get_account_info
from database.database import User
from keyboards.user.keyboards import back_keyboard
from locales.locales import get_text
from states.states import MyStates
from system.dispatcher import router
from database.database import write_account_to_user_table


@router.message(F.text == "🔐 Подключить свободный аккаунт")
async def handle_connect_account_free(message: Message, state: FSMContext):
    """
    Обработчик команды "🔐 Подключить свободный аккаунт".

    Очищает текущее состояние FSM, регистрирует пользователя в базе данных (если его ещё нет)
    с языком по умолчанию "unset", и отправляет пользователю сообщение с приглашением
    🔐 Подключить свободный аккаунт через автоматическое подключение свободного аккаунта.

    :param message: (Message) Объект входящего сообщения от пользователя.
    :param state: (FSMContext) Контекст машины состояний, используется для сброса текущего состояния.
    :return: None
    """
    await state.clear()  # Завершаем текущее состояние машины состояния

    # Создаём пользователя с language = "unset", если его нет
    user, created = User.get_or_create(
        user_id=message.from_user.id,
        defaults={
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "language": "unset"  # ← ключевое: "unset" = язык не выбран
        }
    )
    available_sessions = await CheckingAccountsValidity(message=message, path='accounts/free').get_available_sessions()
    logger.info(f"Подключаем аккаунт {available_sessions}")
    random_session = random.choice(available_sessions)
    logger.info(f"Подключаем аккаунт {random_session}")

    shutil.move(
        os.path.join('accounts/free', f'{random_session}.session'),
        os.path.join(f'accounts/{user.user_id}', f'{random_session}.session')
    )

    await message.answer(
        text="✅ Аккаунт успешно подключен",
        reply_markup=back_keyboard()
    )


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


@router.message(F.text == "🔐 Подключить аккаунт")
async def handle_connect_account(message: Message, state: FSMContext):
    await state.clear()
    user, created = User.get_or_create(
        user_id=message.from_user.id,
        defaults={
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "language": "unset"
        }
    )
    await message.answer(get_text(user.language, "connect_account"), reply_markup=back_keyboard())
    await state.set_state(MyStates.waiting_for_session_file_user)


# ✅ Фильтр: только документы И только в нужном состоянии
@router.message(MyStates.waiting_for_session_file_user, F.document)
async def handle_account_file(message: Message, state: FSMContext):
    """Обработчик приёма файла сессии (.session) от пользователя"""
    user_id = message.from_user.id
    document = message.document
    local_file_path = None  # для безопасного удаления в finally

    try:
        logger.info(f"User {user_id} отправил файл: {document.file_name}")

        # ✅ Проверяем расширение — если не .session, остаёмся в состоянии
        if not document.file_name.endswith('.session'):
            await message.answer("❌ Это не файл сессии! Отправьте файл с расширением `.session`")
            return  # state НЕ сбрасываем — ждём правильный файл

        sessions_dir = creates_temporary_folder_for_accounts()
        local_file_path, safe_file_name = sanitization_file_name(document, sessions_dir)

        await message.bot.download(document, destination=local_file_path)
        logger.info(f"✅ Файл скачан: {local_file_path}")

        await message.answer(f"📥 Файл получен: `{safe_file_name}`\n\n🔍 Проверяю аккаунт...")

        session_path_without_ext = str(local_file_path.with_suffix(""))
        checker = CheckingAccountsValidity(message=message, path=session_path_without_ext)
        client = await checker.connect_client()

        if client:
            account_info = await get_account_info(client)
            phone = account_info["phone"] or "unknown"
            first_name = account_info["first_name"] or ""

            session_string = StringSession.save(client.session)
            write_account_to_user_table(
                user_id=user_id,
                session_string=session_string,
                phone_number=phone
            )
            await client.disconnect()

            logger.success(f"✅ Сессия добавлена: {phone} | {first_name}")
            await message.answer(
                f"✅ <b>{safe_file_name}</b> — успешно!\n"
                f"📱 {phone} | 👤 {first_name}\n"
                f"💾 Сохранено в вашу персональную базу.",
                parse_mode="HTML"
            )
        else:
            logger.warning(f"❌ Сессия {safe_file_name} не валидна для пользователя {user_id}")
            await message.answer(
                f"❌ <b>{safe_file_name}</b> — не прошёл проверку.\n"
                f"Проверьте, что файл сессии актуален и не используется в другом месте.",
                parse_mode="HTML"
            )

    except Exception as e:
        logger.exception(f"Ошибка при обработке сессии пользователя {user_id}: {e}")
        await message.answer("⚠️ Произошла ошибка при проверке аккаунта. Попробуйте позже.")

    finally:
        # ✅ Удаляем временный файл в любом случае
        if local_file_path and local_file_path.exists():
            local_file_path.unlink()
        # ✅ Сбрасываем состояние только в конце
        await state.clear()


def register_connect_account_handler():
    """
    Регистрирует обработчики для подключения аккаунта.

    Добавляет в маршрутизатор (router) два обработчика:
        1. handle_connect_account — для обработки нажатия кнопки "🔐 Подключить аккаунт".
        2. handle_account_file — для приёма файла сессии (.session) от пользователя.

    Обработчики реагируют на текстовые сообщения и документы соответственно.
    """
    router.message.register(handle_connect_account)  # обработчик для кнопки "🔐 Подключить аккаунт"
    router.message.register(handle_account_file)  # обработчик приема аккаунта в формате .session
