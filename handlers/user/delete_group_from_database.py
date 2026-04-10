# -*- coding: utf-8 -*-
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger

from account_manager.auth import CheckingAccountsValidity
from account_manager.unsubscribe import unsubscribe
from database.database import dell_group, get_user_accounts
from keyboards.user.keyboards import back_keyboard, main_menu_keyboard, menu_launch_tracking_keyboard
from locales.locales import t
from states.states import MyStates

router = Router(name=__name__)


@router.message(F.text == "🗑️ Удалить группу из отслеживания")
async def delete_group_from_database(message: Message, state: FSMContext):
    """
    Удаление группы из базы данных
    """
    await state.clear()  # Сбрасываем текущее состояние FSM
    user = User.get(User.user_id == message.from_user.id)
    await message.answer(
        t("delete_group_prompt", lang=user.language),
        reply_markup=back_keyboard()
    )
    await state.set_state(MyStates.del_username_groups)


@router.message(MyStates.del_username_groups)
async def del_user_in_db(message: Message, state: FSMContext) -> None:
    """
    Удаляем группу из отслеживания
    """
    user = User.get(User.user_id == message.from_user.id)
    group_username = message.text.strip()
    await state.clear()  # Завершаем текущее состояние машины состояния
    logger.info(f"Пользователь ввёл ссылку для удаления: {group_username}")

    deletion_result = dell_group(user_id=message.from_user.id, username=group_username)

    if deletion_result:
        await message.answer(
            text=t("group_deleted", lang=user.language, group=group_username),
            reply_markup=main_menu_keyboard()
        )
        logger.info(f"Пользователь {message.from_user.id} удалил группу @{group_username}")
    else:
        await message.answer(
            text=t("group_not_found", lang=user.language, group=group_username),
            reply_markup=main_menu_keyboard()
        )
        logger.warning(f"Попытка удалить несуществующую группу @{group_username} "
                       f"пользователем {message.from_user.id}")

    # Получаем все аккаунты пользователя из его персональной таблицы
    accounts = get_user_accounts(message.from_user.id)

    if not accounts:
        logger.warning(f"⚠️ У пользователя {message.from_user.id} нет подключённых аккаунтов в БД")
        await message.answer(
            t("no_accounts", lang=user.language),
            reply_markup=menu_launch_tracking_keyboard()
        )
        return None
    logger.info(f"📦 Найдено {len(accounts)} аккаунтов в БД для пользователя {message.from_user.id}")

    checker = CheckingAccountsValidity(message=message)  # ✅ Сохраняем активный клиент
    client = await checker.client_connect_string_session(accounts[0]['session_string'])

    await unsubscribe(client, group_username)  # Отписываемся от группы или канала по username

    client.disconnect()
