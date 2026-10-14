from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger

from database.database import User, create_group_model
from keyboards.keyboards import back_keyboard
from locales.locales import t
from states.states import MyStates

router = Router(name=__name__)


@router.message(
    (F.text == t('connect_group_for_messages_button', 'ru')) | (F.text == t('connect_group_for_messages_button', 'en')))
async def handle_connect_message_group(message: Message, state: FSMContext):
    """
    Обработчик команды "📤 Подключить группу для сообщений" (текст).
    """
    await state.clear()  # Завершаем текущее состояние машины состояния
    user = User.get(User.user_id == message.from_user.id)

    logger.info(
        f"Пользователь {message.from_user.id} {message.from_user.username} {message.from_user.first_name} {message.from_user.last_name} перешел в меню 📤 Подключить группу для сообщений")

    await message.answer(
        t("enter_group", lang=user.language),
        reply_markup=back_keyboard(lang=user.language, callback_data="menu_settings")
    )
    await state.set_state(MyStates.entering_group)


@router.callback_query(F.data.in_({"settings_connect_group", "group_connect"}))
async def handle_connect_message_group_cb(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн-кнопки "📤 Подключить группу для сообщений".
    """
    await state.clear()
    user = User.get(User.user_id == callback.from_user.id)

    logger.info(
        f"Пользователь {callback.from_user.id} перешел в меню 📤 Подключить группу для сообщений через инлайн-кнопку")

    await callback.message.answer(
        t("enter_group", lang=user.language),
        reply_markup=back_keyboard(lang=user.language, callback_data="menu_settings")
    )
    await state.set_state(MyStates.entering_group)
    await callback.answer()


@router.message(MyStates.entering_group)
async def handle_group_username_submission(message: Message, state: FSMContext):
    """
    Обработчик ввода username технической группы пользователем.

    Получает username из текста сообщения, создаёт или получает модель базы данных
    для хранения технической группы пользователя, создаёт таблицу при необходимости,
    и сохраняет введённый username. Уведомляет пользователя об успешном добавлении
    или ошибке (например, дубликат).

    - Используется динамическая модель `create_group_model` для изоляции данных пользователей.
    - После успешной или неуспешной обработки состояние FSM очищается.

    :param message: (Message) Объект входящего сообщения с username группы.
    :param state: (FSMContext) Контекст машины состояний, используется для сброса состояния после обработки.
    :raise Exception: При ошибке добавления в БД (например, нарушение уникальности).
                      Обрабатывается локально с отправкой пользователю соответствующего сообщения.
    """

    group_username = message.text.strip()
    logger.info(f"Пользователь ввёл ссылку: {group_username}")

    user = User.get(User.user_id == message.from_user.id)

    # Создаём модель с таблицей, уникальной для конкретного пользователя
    GroupModel = create_group_model(user_id=message.from_user.id)  # Создаём таблицу для групп / ключевых слов
    GroupModel.create_table(safe=True)
    logger.info(f"Создана новая таблица для пользователя {message.from_user.id}")
    # Добавляем запись в таблицу
    try:
        # Удаляем старую запись, если есть
        GroupModel.delete().execute()
        # Вставляем новую
        GroupModel.create(user_group=group_username)
        await message.answer(t("group_added", lang=user.language, group=group_username))
        logger.info(f"username {group_username} добавлено пользователем {message.from_user.id}")
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            await message.answer(t("group_already_added", lang=user.language))
        else:
            await message.answer(t("group_add_error", lang=user.language))
        logger.error(f"Ошибка при добавлении ключевого слова: {e}")
    await state.clear()  # Завершаем текущее состояние машины состояния
