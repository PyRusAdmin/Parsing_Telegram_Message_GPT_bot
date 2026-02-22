# -*- coding: utf-8 -*-
import os
import random
import shutil
from pathlib import Path

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger

from account_manager.auth import CheckingAccountsValidity
from database.database import User
from keyboards.user.keyboards import back_keyboard
from locales.locales import get_text
from system.dispatcher import router


@router.message(F.text == "🔐 Подключить аккаунт")
async def handle_connect_account(message: Message, state: FSMContext):
    """
    Обработчик команды "🔐 Подключить аккаунт".

    Очищает текущее состояние FSM, регистрирует пользователя в базе данных (если его ещё нет)
    с языком по умолчанию "unset", и отправляет пользователю сообщение с приглашением
    🔐 Подключить аккаунт через отправку .session-файла.

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
    await message.answer(get_text(user.language, "connect_account"), reply_markup=back_keyboard())


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


@router.message(F.document)
async def handle_account_file(message: Message, state: FSMContext):
    """
    Обработчик приёма файла сессии (.session) от пользователя.

    ✅ Правильный порядок:
    1. Проверяем расширение .session
    2. Создаём папку accounts/{user_id}/
    3. Скачиваем файл на диск через message.bot.download()
    4. Передаём ЛОКАЛЬНЫЙ путь (без .session) в CheckingAccountsValidity
    5. Обрабатываем и сохраняем StringSession в БД
    """
    try:
        await state.clear()
        user_id = message.from_user.id  # получаем id пользователя
        document = message.document  # получаем файл сессии
        logger.info(f"User {user_id} отправил файл: {document.file_name}")

        # ✅ Проверяем расширение
        if not document.file_name.endswith('.session'):
            await message.answer("❌ Это не файл сессии! Отправьте файл с расширением `.session`")
            return

        # ✅ 2. Создаём папку для сессий пользователя
        sessions_dir = creates_temporary_folder_for_accounts()

        # ✅ Санитизация имени файла (убираем опасные символы)
        # safe_name = "".join(c for c in document.file_name if c.isalnum() or c in "._-")
        # local_file_path = sessions_dir / safe_name
        local_file_path, safe_file_name = sanitization_file_name(document, sessions_dir)

        # ✅ 4. Скачиваем файл НА ЛОКАЛЬНЫЙ ДИСК
        # ⚠️ file.file_path — это путь на серверах Telegram, его нельзя использовать напрямую!
        await message.bot.download(document, destination=local_file_path)
        logger.info(f"✅ Файл скачан: {local_file_path}")

        await message.answer(f"📥 Файл получен: `{safe_file_name}`\n\n🔍 Проверяю аккаунт...")

        # ✅ 5. Передаём путь БЕЗ расширения .session (Telethon добавит его сам)
        session_path_without_ext = str(local_file_path.with_suffix(""))

        # ✅ 6. Создаем checker и обрабатываем сессию
        checker = CheckingAccountsValidity(message=message, path=session_path_without_ext, user_id=user_id)
        result = await checker.validate_and_save_session()

        # ✅ 7. Обрабатываем результат
        if result.get("success"):
            # Удаляем временный .session файл (он больше не нужен, т.к. есть StringSession в БД)
            if local_file_path.exists():
                local_file_path.unlink()
                # Также удаляем возможный .session-journal
                journal_path = local_file_path.with_suffix(".session-journal")
                if journal_path.exists():
                    journal_path.unlink()

            await message.answer(
                f"✅ Аккаунт успешно подключён!\n"
                f"📱 Номер: `{result['phone']}`\n"
                f"👤 Имя: `{result['first_name'] or ''}`\n"
                f"🔐 Сессия сохранена в базе данных."
            )
            logger.success(f"✅ Сессия добавлена в БД: {result['phone']} | User: {user_id}")
        else:
            # ❌ Если ошибка — удаляем файл и сообщаем пользователю
            if local_file_path.exists():
                local_file_path.unlink()

            error_msg = result.get("error", "Неизвестная ошибка")
            await message.answer(f"❌ Аккаунт не прошёл проверку:\n`{error_msg}`")
            logger.warning(f"❌ Сессия {safe_file_name} не валидна: {error_msg}")

    except Exception as e:
        logger.exception(f"Ошибка при обработке сессии пользователя {user_id}: {e}")
        await message.answer("⚠️ Произошла ошибка при проверке аккаунта. Попробуйте позже.")
    finally:
        # ✅ Очищаем состояние FSM
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
