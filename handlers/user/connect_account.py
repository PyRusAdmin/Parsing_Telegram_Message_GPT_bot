# -*- coding: utf-8 -*-
import os
import random
import shutil

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger  # https://github.com/Delgan/loguru

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


@router.message(F.document)
async def handle_account_file(message: Message, state: FSMContext):
    """
    Обработчик приёма файла сессии (.session) от пользователя для подключения аккаунта Telegram.

    Функция выполняет следующие действия:
    1. Сбрасывает текущее состояние FSM.
    2. Проверяет, что присланный файл имеет расширение .session.
    3. Создаёт папку пользователя в директории 'accounts/' если её нет.
    4. Удаляет старые файлы сессий (.session и .session-journal) в папке пользователя.
    5. Скачивает и сохраняет новый .session-файл.
    6. Уведомляет пользователя об успешной загрузке (и удалении старых файлов, если было).

    - Принимаются только файлы с расширением '.session'.
    - Старые сессии удаляются для предотвращения конфликтов.
    - Файлы хранятся по пути 'accounts/{user_id}/'.
    - Используется бот API для скачивания файла.

    :param message: (Message) Входящее сообщение с документом от пользователя.
    :param state: (FSMContext) Контекст машины состояний, используется для сброса состояния.
    :return: None
    """
    await state.clear()  # Завершаем текущее состояние машины состояния

    logger.info(f"User {message.from_user.id} отправил аккаунт {message.document.file_name}")

    # Проверяем расширение файла
    if not message.document.file_name.endswith(".session"):
        await message.answer("⚠️ Пожалуйста, отправьте корректный файл сессии (.session).")
        return

    # Папка пользователя
    user_folder = os.path.join(os.getcwd(), f"accounts/{message.from_user.id}")
    os.makedirs(user_folder, exist_ok=True)

    # 🧹 Удаляем старые файлы .session и .session-journal
    deleted_files = []
    for file_name in os.listdir(user_folder):
        if file_name.endswith(".session") or file_name.endswith(".session-journal"):
            try:
                os.remove(os.path.join(user_folder, file_name))
                deleted_files.append(file_name)
            except Exception as e:
                logger.error(f"Ошибка при удалении {file_name}: {e}")

    if deleted_files:
        logger.info(f"Удалены старые файлы: {', '.join(deleted_files)}")

    # Скачиваем новый файл
    file = await message.bot.get_file(message.document.file_id)
    await message.bot.download_file(file.file_path, os.path.join(user_folder, message.document.file_name))

    # Ответ пользователю
    msg = f"✅ Аккаунт {message.document.file_name} успешно загружен."
    if deleted_files:
        msg += f"\n♻️ Старые файлы ({', '.join(deleted_files)}) были удалены. Аккаунт обновлен"
    await message.answer(msg)


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
