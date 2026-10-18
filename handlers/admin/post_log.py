from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, CallbackQuery

from handlers.user_language import determines_user_language
from keyboards.keyboards import back_keyboard
from locales.locales import t

router = Router(name=__name__)


@router.callback_query(F.data == "admin_get_log")
async def log_cb(callback: CallbackQuery, state: FSMContext):
    """Обработчик команды Получить лог файл (инлайн), отправляет лог файл администратору"""
    await callback.answer()

    await state.clear()
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    document = FSInputFile("logs/log.log")

    await message.answer_document(
        document=document,
        caption=t("log_file_caption", lang=user_lang),
        parse_mode="HTML",
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_admin_panel"),
    )
