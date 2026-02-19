# -*- coding: utf-8 -*-
import os

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger  # https://github.com/Delgan/loguru

from account_manager.auth import CheckingAccountsValidity
from account_manager.session import find_session_file
from account_manager.unsubscribe import unsubscribe
from database.database import create_groups_model, User
from keyboards.user.keyboards import back_keyboard, main_menu_keyboard, connect_keyboard_account
from states.states import MyStates
from system.dispatcher import router


@router.message(F.text == "Удалить группу из отслеживания")
async def delete_group_from_database(message: Message, state: FSMContext):
    """
    Удаление группы из базы данных
    """
    await state.clear()  # Сбрасываем текущее состояние FSM
    await message.answer(
        "Введите username группы/канала в формате @username для удаления из отслеживания:",
        reply_markup=back_keyboard()
    )
    await state.set_state(MyStates.del_username_groups)


@router.message(MyStates.del_username_groups)
async def del_user_in_db(message: Message, state: FSMContext) -> None:
    """
    Удаляем пользователя
    """
    group_username = message.text.strip()
    await state.clear()  # Завершаем текущее состояние машины состояния
    logger.info(f"Пользователь ввёл ссылку: {group_username}")

    # Создаём модель с таблицей, уникальной для конкретного пользователя
    logger.info(f"Создана новая таблица для пользователя {message.from_user.id}")

    # Удаляем группу по username (ищем с учётом @ и без)
    username_to_search = group_username.lstrip('@')  # Убираем @ если есть

    GroupModel = create_groups_model(user_id=message.from_user.id)

    # Попытка найти и удалить
    deleted_count = (GroupModel
                     .delete()
                     .where((GroupModel.username == username_to_search) |
                            (GroupModel.username == f"@{username_to_search}"))
                     .execute())

    if deleted_count > 0:
        await message.answer(
            f"✅ Группа @{username_to_search} успешно удалена из отслеживания.",
            reply_markup=main_menu_keyboard()
        )
        logger.info(f"Пользователь {message.from_user.id} удалил группу @{username_to_search}")
    else:
        await message.answer(
            f"❌ Группа @{username_to_search} не найдена в вашем списке отслеживаемых.",
            reply_markup=main_menu_keyboard()
        )
        logger.warning(f"Попытка удалить несуществующую группу @{username_to_search} "
                       f"пользователем {message.from_user.id}")

    user = User.get(User.user_id == message.from_user.id)

    # === Папка, где хранятся сессии ===
    session_dir = os.path.join("accounts", str(message.from_user.id))
    os.makedirs(session_dir, exist_ok=True)

    session_path = await find_session_file(session_dir, user, message)  # <-- ✅ ищем файл сессии

    logger.info(session_path)
    if session_path is None:
        logger.warning("Нет подключенного аккаунта")

        await message.answer(
            text="Нет подключенного аккаунта. Подключите аккаунт.",
            reply_markup=connect_keyboard_account()
        )
        return  # Правильный способ прервать выполнение обработчика

    checker = CheckingAccountsValidity(message=message, path="accounts/parsing")
    client = await checker.connect_client(
        session_name=session_path.replace(".session", ""),
    )  # <-- ✅ подключаемся к клиенту Telethon
    await unsubscribe(client, username_to_search, message)

    client.disconnect()


def register_handlers_delete():
    router.message.register(delete_group_from_database)
