from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message, CallbackQuery

from handlers.user_language import determines_user_language
from keyboards.keyboards import back_keyboard
from locales.locales import t

router = Router(name=__name__)


async def log_internal(message: Message, state: FSMContext):
    """Отправляет файл логов администратору"""
    await state.clear()
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=message.from_user.id)
    document = FSInputFile("logs/log.log")

    await message.answer_document(
        document=document,
        caption=t("log_file_caption", lang=user_lang),
        parse_mode="HTML",
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_admin_panel"),
    )


# @router.message((F.text == t('get_log_file_button', 'ru')) | (F.text == t('get_log_file_button', 'en')))
# async def log(message: Message, state: FSMContext):
#     """Обработчик команды Получить лог файл (текст)"""
#     await log_internal(message, state)


@router.callback_query(F.data == "admin_get_log")
async def log_cb(callback: CallbackQuery, state: FSMContext):
    """Обработчик команды Получить лог файл (инлайн)"""
    await callback.answer()
    await log_internal(callback.message, state)
