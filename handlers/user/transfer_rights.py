from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from database.users_personal_trackings import UsersPersonalTrackings
from database.users_groups import UsersGroups
from database.users_keywords import UsersKeywords
from handlers.user_language import determines_user_language
from keyboards.keyboards import back_keyboard
from locales.locales import t
from states.states import MyStates

router = Router(name=__name__)


def transfer_user_settings(from_user_id: int, to_user_id: int) -> tuple[int, int]:
    """
    Копирует каналы и ключевые слова от одного пользователя к другому в единых таблицах БД.

    :param from_user_id: (int) ID пользователя-источника в Telegram.
    :param to_user_id: (int) ID пользователя-получателя в Telegram.
    :return: (tuple[int, int]) Кортеж из количества добавленных каналов и ключевых слов.
    """
    added_groups = 0
    added_keywords = 0

    # 1. Перенос групп/каналов
    existing_groups = list(UsersGroups.select(UsersGroups.username_group).where(UsersGroups.user_id == from_user_id))
    for g in existing_groups:
        _, created = UsersGroups.get_or_create(user_id=to_user_id, username_group=g.username_group)
        if created:
            added_groups += 1

    # 2. Перенос ключевых слов
    existing_kw = list(UsersKeywords.select(UsersKeywords.user_keyword).where(UsersKeywords.user_id == from_user_id))
    for kw in existing_kw:
        _, created = UsersKeywords.get_or_create(user_id=to_user_id, user_keyword=kw.user_keyword)
        if created:
            added_keywords += 1

    logger.info(f"Настройки переданы от {from_user_id} к {to_user_id}: +{added_groups} групп, +{added_keywords} слов")
    return added_groups, added_keywords


@router.callback_query(F.data == "settings_transfer_rights")
async def transfer_settings_cb(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Запрашивает ID пользователя для передачи настроек отслеживания.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    :return: (None)
    """
    await state.clear()
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    await callback.message.edit_text(
        text=t("transfer_rights_prompt", lang=user_lang),
        parse_mode="HTML",
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
    )
    await state.set_state(MyStates.get_id_user_transfer)
    await callback.answer()


@router.message(MyStates.get_id_user_transfer)
async def get_id_for_transferring(message: Message, state: FSMContext):
    """
    Принимает ID целевого пользователя и выполняет копирование настроек отслеживания.

    :param message: (Message) Входящее сообщение Telegram с целевым ID.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    user_lang = determines_user_language(message_or_callback=message.from_user.id)
    raw_id = message.text.strip()
    await state.clear()

    if not raw_id.isdigit():
        await message.answer(
            t("transfer_rights_invalid_id", lang=user_lang),
            reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
        )
        return

    target_user_id = int(raw_id)

    if target_user_id == message.from_user.id:
        await message.answer(
            t("transfer_rights_self", lang=user_lang),
            reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
        )
        return

    # Проверяем, существует ли целевой пользователь в боте
    target_user = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == target_user_id)
    if not target_user:
        await message.answer(
            t("transfer_rights_not_found", lang=user_lang, target_user_id=target_user_id),
            parse_mode="HTML",
            reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
        )
        return

    added_groups, added_keywords = transfer_user_settings(
        from_user_id=message.from_user.id,
        to_user_id=target_user_id
    )

    await message.answer(
        text=t("transfer_rights_success", lang=user_lang, target_user_id=target_user_id, groups=added_groups,
               keywords=added_keywords),
        parse_mode="HTML",
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
    )
