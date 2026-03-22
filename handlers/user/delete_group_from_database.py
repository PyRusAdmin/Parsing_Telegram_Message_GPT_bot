# -*- coding: utf-8 -*-
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger  # https://github.com/Delgan/loguru

from account_manager.auth import CheckingAccountsValidity
from account_manager.unsubscribe import unsubscribe
from database.database import dell_group, get_user_accounts
from keyboards.user.keyboards import back_keyboard, main_menu_keyboard, menu_launch_tracking_keyboard
from states.states import MyStates

# from system.dispatcher import router
router = Router(name=__name__)


@router.message(F.text == "Удалить группу из отслеживания")
async def delete_group_from_database(message: Message, state: FSMContext):
    """
    Удаление группы из базы данных
    """
    await state.clear()  # Сбрасываем текущее состояние FSM
    await message.answer(
        "Введите username группы / канала в формате @username для удаления из отслеживания:",
        reply_markup=back_keyboard()
    )
    await state.set_state(MyStates.del_username_groups)


@router.message(MyStates.del_username_groups)
async def del_user_in_db(message: Message, state: FSMContext) -> None:
    """
    Удаляем группу из отслеживания
    """
    group_username = message.text.strip()
    await state.clear()  # Завершаем текущее состояние машины состояния
    logger.info(f"Пользователь ввёл ссылку для удаления: {group_username}")

    deletion_result = dell_group(user_id=message.from_user.id, username=group_username)

    if deletion_result:
        await message.answer(
            text=f"✅ Группа {group_username} успешно удалена из отслеживания.",
            reply_markup=main_menu_keyboard()
        )
        logger.info(f"Пользователь {message.from_user.id} удалил группу @{group_username}")
    else:
        await message.answer(
            text=f"❌ Группа @{group_username} не найдена в вашем списке отслеживаемых.",
            reply_markup=main_menu_keyboard()
        )
        logger.warning(f"Попытка удалить несуществующую группу @{group_username} "
                       f"пользователем {message.from_user.id}")

    # Получаем все аккаунты пользователя из его персональной таблицы
    accounts = get_user_accounts(message.from_user.id)

    if not accounts:
        logger.warning(f"⚠️ У пользователя {message.from_user.id} нет подключённых аккаунтов в БД")
        await message.answer(
            "❌ У вас нет подключённых аккаунтов.\n\n"
            "Отправьте файл сессии `.session` или нажмите «Подключение аккаунта» в меню.",
            reply_markup=menu_launch_tracking_keyboard()
        )
        return None
    logger.info(f"📦 Найдено {len(accounts)} аккаунтов в БД для пользователя {message.from_user.id}")

    checker = CheckingAccountsValidity(message=message)  # ✅ Сохраняем активный клиент
    client = await checker.client_connect_string_session(accounts[0]['session_string'])

    await unsubscribe(client, group_username)  # Отписываемся от группы или канала по username

    client.disconnect()

# def register_handlers_delete():
#     router.message.register(delete_group_from_database)
