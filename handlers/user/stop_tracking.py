from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger

from database.database import User
from keyboards.keyboards import menu_launch_tracking_keyboard
from account_manager.parser import stop_tracking
from locales.locales import t

router = Router(name=__name__)


async def stop_tracking_internal(message: Message, user_id: int, state: FSMContext):
    await state.clear()
    user = User.get(User.user_id == user_id)
    user_lang = user.language if user.language != "unset" else "ru"

    logger.info(f"Пользователь {user_id} нажал кнопку остановки отслеживания")
    await stop_tracking(user_id=user_id, message=message)

    await message.answer(
        text=t("tracking_stopped", lang=user_lang),
        reply_markup=menu_launch_tracking_keyboard(lang=user_lang)
    )


@router.message((F.text == t('stop_tracking_button', 'ru')) | (F.text == t('stop_tracking_button', 'en')))
async def handle_stop_tracking(message: Message, state: FSMContext):
    """Обработчик команды Остановить отслеживание (текст)"""
    await stop_tracking_internal(message, message.from_user.id, state)


@router.callback_query(F.data == "tracking_stop")
async def handle_stop_tracking_cb(callback: CallbackQuery, state: FSMContext):
    """Обработчик команды Остановить отслеживание (инлайн)"""
    await callback.answer()
    await stop_tracking_internal(callback.message, callback.from_user.id, state)
