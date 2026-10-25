from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger  # https://github.com/Delgan/loguru
from telethon import TelegramClient

from account_manager.auth import CheckingAccountsValidity
from account_manager.unsubscribe import unsubscribe
from account_manager.utilit import normalize_telegram_link
from database.group_user_database import dell_group
from database.database import PersonalTracking
from handlers.user_language import determines_user_language
from keyboards.keyboards import back_keyboard, main_menu_keyboard, menu_launch_tracking_keyboard
from locales.locales import t
from states.states import MyStates

router = Router(name=__name__)


@router.message(
    (F.text == t('delete_group_from_tracking_button', 'ru')) | (F.text == t('delete_group_from_tracking_button', 'en')))
async def delete_group_from_database(message: Message, state: FSMContext):
    """
    Удаление группы из базы данных (текст-кнопка Reply-клавиатуры)
    """
    await state.clear()  # Сбрасываем текущее состояние FSM
    user_lang = determines_user_language(message_or_callback=message.from_user.id)
    await message.answer(
        t("delete_group_prompt", lang=user_lang),
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
    )
    await state.set_state(MyStates.del_username_groups)


@router.callback_query(F.data == "settings_delete_group")
async def delete_group_from_database_cb(callback: CallbackQuery, state: FSMContext):
    """
    Удаление группы из базы данных (инлайн-кнопка)
    """
    await state.clear()
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    await callback.message.answer(
        t("delete_group_prompt", lang=user_lang),
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
    )
    await state.set_state(MyStates.del_username_groups)
    await callback.answer()


@router.message(MyStates.del_username_groups)
async def del_user_in_db(message: Message, state: FSMContext) -> None:
    """
    Удаляем группу из отслеживания.

    Перед поиском в БД нормализует ввод пользователя через normalize_telegram_link,
    чтобы формат совпадал с форматом хранения (https://t.me/<username>).
    Приватные инвайт-ссылки (joinchat/+hash) также поддерживаются.
    """
    user_lang = determines_user_language(message_or_callback=message.from_user.id)

    raw_input = message.text.strip()
    await state.clear()
    logger.info(f"Пользователь {message.from_user.id} ввёл для удаления: {raw_input!r}")

    # ── Нормализуем ввод пользователя к тому же формату, что хранится в БД ──
    normalized = normalize_telegram_link(raw_input)

    if normalized is None:
        # Ввод не распознан — сообщаем об ошибке формата
        await message.answer(
            text=(
                "⚠️ <b>Не удалось распознать ссылку.</b>\n\n"
                "Допустимые форматы:\n"
                "• <code>@channel_name</code>\n"
                "• <code>https://t.me/channel_name</code>\n"
                "• <code>https://t.me/+PrivateHash</code>\n"
                "• <code>https://t.me/joinchat/Hash</code>"
            ),
            reply_markup=main_menu_keyboard(lang=user_lang),
            parse_mode="HTML"
        )
        logger.warning(
            f"Пользователь {message.from_user.id} ввёл нераспознанный формат: {raw_input!r}"
        )
        return

    logger.info(f"Нормализованная ссылка для удаления: {normalized!r}")

    deletion_result = dell_group(user_id=message.from_user.id, username_group=normalized)

    if deletion_result:
        await message.answer(
            text=t("group_deleted", lang=user_lang, group=normalized),
            reply_markup=main_menu_keyboard(lang=user_lang)
        )
        logger.info(f"Пользователь {message.from_user.id} удалил канал {normalized!r}")
    else:
        await message.answer(
            text=t("group_not_found", lang=user_lang, group=normalized),
            reply_markup=main_menu_keyboard(lang=user_lang)
        )
        logger.warning(
            f"Пользователь {message.from_user.id}: канал {normalized!r} не найден в БД"
        )
        return  # Нечего отписываться — канала нет в БД, выходим

    # ── Отписка через Telethon-клиент ────────────────────────────────────────
    # Получаем сессию пользователя из таблицы personal_tracking
    rec = PersonalTracking.get_or_none(PersonalTracking.user_id == message.from_user.id)
    session_string = rec.personal_account if rec else None

    if not session_string:
        logger.warning(
            f"⚠️ У пользователя {message.from_user.id} нет подключённого аккаунта — отписка пропущена"
        )
        return None

    checker = CheckingAccountsValidity(message=message)
    client: TelegramClient | None = await checker.client_connect_string_session(session_string)

    if client is None:
        return None

    await unsubscribe(client, raw_input)  # unsubscribe принимает оригинальный ввод (username/@/url)

    await client.disconnect()
