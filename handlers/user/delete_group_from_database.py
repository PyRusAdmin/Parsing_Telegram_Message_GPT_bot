from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger  # https://github.com/Delgan/loguru

from account_manager.auth import CheckingAccountsValidity
from account_manager.unsubscribe import unsubscribe
from database.group_user_database import dell_group
from handlers.user_language import determines_user_language
from keyboards.keyboards import back_keyboard, main_menu_keyboard, menu_launch_tracking_keyboard
from locales.locales import t
from states.states import MyStates

router = Router(name=__name__)


@router.message(
    (F.text == t('delete_group_from_tracking_button', 'ru')) | (F.text == t('delete_group_from_tracking_button', 'en')))
async def delete_group_from_database(message: Message, state: FSMContext):
    """
    Удаление группы из базы данных (текст)
    """
    await state.clear()  # Сбрасываем текущее состояние FSM
    # TODO Сделать единое определение языка пользователя во всем проекте
    # user = User.get(User.user_id == message.from_user.id)
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=message.from_user.id)
    await message.answer(
        t("delete_group_prompt", lang=user_lang),
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
    )
    await state.set_state(MyStates.del_username_groups)


@router.callback_query(F.data == "settings_delete_group")
async def delete_group_from_database_cb(callback: CallbackQuery, state: FSMContext):
    """
    Удаление группы из базы данных (инлайн)
    """
    await state.clear()
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    # TODO Сделать единое определение языка пользователя во всем проекте
    # user = User.get(User.user_id == callback.from_user.id)
    await callback.message.answer(
        t("delete_group_prompt", lang=user_lang),
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
    )
    await state.set_state(MyStates.del_username_groups)
    await callback.answer()


@router.message(MyStates.del_username_groups)
async def del_user_in_db(message: Message, state: FSMContext) -> None:
    """
    Удаляем группу из отслеживания
    """
    # user = User.get(User.user_id == message.from_user.id)
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=message.from_user.id)

    group_username = message.text.strip()
    await state.clear()  # Завершаем текущее состояние машины состояния
    logger.info(f"Пользователь ввёл ссылку для удаления: {group_username}")

    deletion_result = dell_group(user_id=message.from_user.id, username=group_username)

    if deletion_result:
        await message.answer(
            text=t("group_deleted", lang=user_lang, group=group_username),
            reply_markup=main_menu_keyboard(lang=user_lang)
        )
        logger.info(f"Пользователь {message.from_user.id} удалил группу @{group_username}")
    else:
        await message.answer(
            text=t("group_not_found", lang=user_lang, group=group_username),
            reply_markup=main_menu_keyboard(lang=user_lang)
        )
        logger.warning(f"Попытка удалить несуществующую группу @{group_username} пользователем {message.from_user.id}")

    # Получаем все аккаунты пользователя из его персональной таблицы
    accounts = get_user_accounts(message.from_user.id)

    if not accounts:
        logger.warning(f"⚠️ У пользователя {message.from_user.id} нет подключённых аккаунтов в БД")
        await message.answer(
            t("no_accounts", lang=user_lang),
            reply_markup=menu_launch_tracking_keyboard(lang=user_lang)
        )
        return None
    logger.info(f"📦 Найдено {len(accounts)} аккаунтов в БД для пользователя {message.from_user.id}")

    checker = CheckingAccountsValidity(message=message)  # ✅ Сохраняем активный клиент
    client = await checker.client_connect_string_session(accounts[0]['session_string'])

    await unsubscribe(client, group_username)  # Отписываемся от группы или канала по username

    client.disconnect()
