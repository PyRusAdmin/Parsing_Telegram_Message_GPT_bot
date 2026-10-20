from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from handlers.user_language import determines_user_language
from keyboards.keyboards import (
    settings_keyboard
)
from locales.locales import t

router = Router(name=__name__)


@router.callback_query(F.data == "menu_settings")
async def handle_settings_menu_cb(callback: CallbackQuery, state: FSMContext):
    """Обработчик инлайн-кнопки Настройки"""
    await state.clear()
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)

    await callback.message.edit_text(
        text=t("settings_message", lang=user_lang),  # Текст меню настройки
        reply_markup=settings_keyboard(lang=user_lang),
        parse_mode="HTML"
    )
