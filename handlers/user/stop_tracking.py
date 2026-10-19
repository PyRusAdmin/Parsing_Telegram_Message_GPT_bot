from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from loguru import logger  # https://github.com/Delgan/loguru

from account_manager.parser import stop_tracking
from handlers.user_language import determines_user_language
from keyboards.keyboards import menu_launch_tracking_keyboard
from locales.locales import t

router = Router(name=__name__)


# async def stop_tracking_internal(message: Message, user_id: int, state: FSMContext):
#     """Выполняет остановку процесса отслеживания сообщений для пользователя"""
#     await state.clear()
#     # Определяем язык пользователя, который пользователь выбрал при старте бота
#     user_lang = determines_user_language(message_or_callback=message.from_user.id)
#
#     logger.info(f"Пользователь {user_id} нажал кнопку остановки отслеживания")
#     await stop_tracking(user_id=user_id, message=message)
#
#     await message.answer(
#         text=t("tracking_stopped", lang=user_lang),
#         reply_markup=menu_launch_tracking_keyboard(lang=user_lang)
#     )


@router.callback_query(F.data == "tracking_stop")
async def handle_stop_tracking_cb(callback: CallbackQuery, state: FSMContext):
    """Обработчик команды Остановить отслеживание (инлайн)"""
    await callback.answer()
    # await stop_tracking_internal(callback.message, callback.from_user.id, state)
    await state.clear()
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)

    logger.info(f"Пользователь {callback.from_user.id} нажал кнопку остановки отслеживания")
    await stop_tracking(user_id=callback.from_user.id, message=message)

    await message.answer(
        text=t("tracking_stopped", lang=user_lang),
        reply_markup=menu_launch_tracking_keyboard(lang=user_lang)
    )
