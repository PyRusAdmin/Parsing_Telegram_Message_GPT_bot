from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message, CallbackQuery

from database.database import User
from keyboards.keyboards import back_keyboard
from locales.locales import t

router = Router(name=__name__)


async def log_internal(message: Message, user_id: int, state: FSMContext):
    """Отправляет файл логов администратору"""
    await state.clear()
    user = User.get(User.user_id == user_id)
    document = FSInputFile("logs/log.log")

    await message.answer_document(
        document=document,
        caption=t("log_file_caption", lang=user.language),
        parse_mode="HTML",
        reply_markup=back_keyboard(lang=user.language, callback_data="menu_admin_panel"),
    )


@router.message((F.text == t('get_log_file_button', 'ru')) | (F.text == t('get_log_file_button', 'en')))
async def log(message: Message, state: FSMContext):
    """Обработчик команды Получить лог файл (текст)"""
    await log_internal(message, message.from_user.id, state)


@router.callback_query(F.data == "admin_get_log")
async def log_cb(callback: CallbackQuery, state: FSMContext):
    """Обработчик команды Получить лог файл (инлайн)"""
    await callback.answer()
    await log_internal(callback.message, callback.from_user.id, state)
