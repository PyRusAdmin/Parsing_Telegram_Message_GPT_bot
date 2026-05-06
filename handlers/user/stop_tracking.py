from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger

from database.database import User
from keyboards.user.keyboards import menu_launch_tracking_keyboard
from account_manager.parser import stop_tracking
from locales.locales import t

router = Router(name=__name__)


@router.message(F.text == "🛑 Остановить отслеживание")
async def handle_stop_tracking(message: Message, state: FSMContext):
    """
    Обработчик команды "🛑 Остановить отслеживание".

    Очищает состояние FSM, получает данные пользователя и вызывает функцию `stop_tracking`
    для прекращения фонового парсинга сообщений в отслеживаемых группах.
    После остановки отправляет подтверждение пользователю.

    - Команда доступна только во время активного отслеживания.
    - Использует глобальный механизм управления задачами в `parsing/parser.py`.

    :param message: (Message) Входящее сообщение от пользователя.
    :param state: (FSMContext) Контекст машины состояний, сбрасывается перед остановкой.
    :raise Exception: Передаётся в `stop_tracking`, где обрабатывается.
    """
    await state.clear()  # Завершаем текущее состояние машины состояния
    user = User.get(User.user_id == message.from_user.id)

    logger.info(
        f"Пользователь {message.from_user.id} {message.from_user.username} {message.from_user.first_name} {message.from_user.last_name} нажал кнопку остановки отслеживания")

    await stop_tracking(user_id=message.from_user.id, message=message)

    await message.answer(
        text=t("tracking_stopped", lang=user.language),
        reply_markup=menu_launch_tracking_keyboard()  # клавиатура выбора языка
    )
