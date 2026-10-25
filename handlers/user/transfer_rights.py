from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from database.database import User
from database.group_user_database import Group
from database.keywords_user_database import Keywords
from handlers.user_language import determines_user_language
from keyboards.keyboards import back_keyboard
from states.states import MyStates

router = Router(name=__name__)


def transfer_user_settings(from_user_id: int, to_user_id: int) -> tuple[int, int]:
    """
    Копирует каналы и ключевые слова от одного пользователя к другому в единых таблицах БД.
    Возвращает (добавлено_каналов, добавлено_ключевых_слов).
    """
    added_groups = 0
    added_keywords = 0

    # 1. Перенос групп/каналов
    existing_groups = list(Group.select(Group.username_group).where(Group.user_id == from_user_id))
    for g in existing_groups:
        _, created = Group.get_or_create(user_id=to_user_id, username_group=g.username_group)
        if created:
            added_groups += 1

    # 2. Перенос ключевых слов
    existing_kw = list(Keywords.select(Keywords.user_keyword).where(Keywords.user_id == from_user_id))
    for kw in existing_kw:
        _, created = Keywords.get_or_create(user_id=to_user_id, user_keyword=kw.user_keyword)
        if created:
            added_keywords += 1

    logger.info(f"Настройки переданы от {from_user_id} к {to_user_id}: +{added_groups} групп, +{added_keywords} слов")
    return added_groups, added_keywords


@router.callback_query(F.data == "settings_transfer_rights")
async def transfer_settings_cb(callback: CallbackQuery, state: FSMContext) -> None:
    """Запрашивает ID пользователя для передачи настроек"""
    await state.clear()
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    await callback.message.edit_text(
        text=(
            "🔄 <b>Передача настроек другому пользователю</b>\n\n"
            "Отправьте Telegram ID пользователя, которому хотите скопировать свои каналы и ключевые слова.\n\n"
            "<i>Пример: <code>1234567890</code></i>"
        ),
        parse_mode="HTML",
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
    )
    await state.set_state(MyStates.get_id_user_transfer)
    await callback.answer()


@router.message(MyStates.get_id_user_transfer)
async def get_id_for_transferring(message: Message, state: FSMContext):
    """Принимает ID пользователя и выполняет копирование настроек"""
    user_lang = determines_user_language(message_or_callback=message.from_user.id)
    raw_id = message.text.strip()
    await state.clear()

    if not raw_id.isdigit():
        await message.answer(
            "⚠️ Некорректный ID. ID должен содержать только цифры.\n\nПопробуйте снова через меню настроек.",
            reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
        )
        return

    target_user_id = int(raw_id)

    if target_user_id == message.from_user.id:
        await message.answer(
            "⚠️ Нельзя передать настройки самому себе.",
            reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
        )
        return

    # Проверяем, существует ли целевой пользователь в боте
    target_user = User.get_or_none(User.user_id == target_user_id)
    if not target_user:
        await message.answer(
            f"⚠️ Пользователь с ID <code>{target_user_id}</code> ещё не запускал этого бота.",
            parse_mode="HTML",
            reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
        )
        return

    added_groups, added_keywords = transfer_user_settings(
        from_user_id=message.from_user.id,
        to_user_id=target_user_id
    )

    await message.answer(
        text=(
            f"✅ <b>Настройки успешно переданы пользователю {target_user_id}!</b>\n\n"
            f"• Скопировано каналов: <b>{added_groups}</b>\n"
            f"• Скопировано ключевых слов: <b>{added_keywords}</b>"
        ),
        parse_mode="HTML",
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
    )
