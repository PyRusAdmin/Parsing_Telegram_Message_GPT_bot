import asyncio
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from loguru import logger  # https://github.com/Delgan/loguru

from account_manager.parser import stop_tracking
from handlers.user.personal_tracking import get_personal_tracking_text_and_kb
from handlers.user_language import determines_user_language

router = Router(name=__name__)


@router.callback_query(F.data == "tracking_stop")
async def handle_stop_tracking_cb(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн-команды "Остановить отслеживание" из единого меню.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    await state.clear()
    user_id = callback.from_user.id
    user_lang = determines_user_language(message_or_callback=user_id)

    logger.info(f"Пользователь {user_id} нажал кнопку остановки отслеживания")
    await stop_tracking(user_id=user_id, message=callback.message)
    await callback.answer(
        "🛑 Отслеживание остановлено" if user_lang == "ru" else "🛑 Tracking stopped",
        show_alert=False
    )

    await asyncio.sleep(0.3)
    text, kb = get_personal_tracking_text_and_kb(user_id=user_id, lang=user_lang)
    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=kb,
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.answer(
            text=text,
            reply_markup=kb,
            parse_mode="HTML"
        )
