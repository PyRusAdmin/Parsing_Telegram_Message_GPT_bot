from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from account_manager.utilit import normalize_telegram_link
from database.group_user_database import add_user_group
from handlers.user_language import determines_user_language
from keyboards.keyboards import back_keyboard
from states.states import PersonalTrackingStateGroupInput

router = Router(name=__name__)


@router.callback_query(F.data == "group_input")
async def process_target_link_input_group_input(callback: CallbackQuery, state: FSMContext):
    """Обработчик инлайн-кнопки Ввод группы, для отслеживания"""

    await state.clear()  # Очищаем состояние, что бы не получить случайное срабатывание
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    await state.set_state(PersonalTrackingStateGroupInput.waiting_for_target_link_group_input)
    await callback.message.edit_text(
        text="🔗 <b>Отправьте ссылку или username группы/канала для отслеживания</b>\n\n"
             "Например:\n"
             "<code>https://t.me/python_jobs</code>\n"
             "или <code>@python_jobs</code>\n\n"
             "Можно отправить несколько ссылок, каждую с новой строки.",
        parse_mode="HTML",
        reply_markup=back_keyboard(lang=user_lang)  # Кнопка назад
    )
    await callback.answer()  # И только потом подтверждаем callback (чтобы убрать «часики»)


@router.message(PersonalTrackingStateGroupInput.waiting_for_target_link_group_input, F.text)
async def process_target_link_input_group_input(message: Message, state: FSMContext):
    """Проверяет и сохраняет ссылки на группы и каналы. (F.text - принимает только текст от пользователя)"""
    target_input = message.text.strip()

    group_list = [
        group.strip()
        for group in target_input.split('\n')
        if group.strip()
    ]

    if not group_list:  # Если нет списка, то присылаем пользователю сообщение, что нет ссылки
        await message.answer("⚠️ Отправьте хотя бы одну ссылку или username.")
        return

    normalized_groups = []  # Список с группами / каналами пользователей

    for group in group_list:
        normalized_link = normalize_telegram_link(group)

        if normalized_link is None:
            await message.answer("⚠️ Проверьте правильность ссылок.")
            return

        normalized_groups.append(normalized_link)

    add_user_group(
        user_id=message.from_user.id,
        group=normalized_groups
    )

    await message.answer("✅ Группа / группы записаны в базу данных.")
    await state.clear()  # Очищаем состояние, что бы не получить случайное срабатывание


@router.message(PersonalTrackingStateGroupInput.waiting_for_target_link_group_input, ~F.text)
async def process_non_text_group_input(message: Message):
    """Обрабатывает сообщения, которые не содержат текст."""

    await message.answer(
        "⚠️ Отправьте ссылку или username группы/канала текстовым сообщением."
    )

# @router.callback_query(F.data == "settings_connect_group")
# async def handle_connect_message_group_cb(callback: CallbackQuery, state: FSMContext):
#     """
#     Обработчик инлайн-кнопки "📤 Подключить группу для сообщений".
#     """
#     await state.clear()
#
#     # Определяем язык пользователя, который пользователь выбрал при старте бота
#     user_lang = determines_user_language(message_or_callback=callback.from_user.id)
#
#     logger.info(
#         f"Пользователь {callback.from_user.id} перешел в меню 📤 Подключить группу для сообщений через инлайн-кнопку")
#
#     await callback.message.answer(
#         t("enter_group", lang=user_lang),
#         reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
#     )
#     await state.set_state(MyStates.entering_group)
#     await callback.answer()
#
#
# @router.message(MyStates.entering_group)
# async def handle_group_username_submission(message: Message, state: FSMContext):
#     """
#     Обработчик ввода username технической группы пользователем.
#
#     Получает username из текста сообщения, создаёт или получает модель базы данных
#     для хранения технической группы пользователя, создаёт таблицу при необходимости,
#     и сохраняет введённый username. Уведомляет пользователя об успешном добавлении
#     или ошибке (например, дубликат).
#
#     - Используется динамическая модель `create_group_model` для изоляции данных пользователей.
#     - После успешной или неуспешной обработки состояние FSM очищается.
#
#     :param message: (Message) Объект входящего сообщения с username группы.
#     :param state: (FSMContext) Контекст машины состояний, используется для сброса состояния после обработки.
#     :raise Exception: При ошибке добавления в БД (например, нарушение уникальности).
#                       Обрабатывается локально с отправкой пользователю соответствующего сообщения.
#     """
#     user_lang = determines_user_language(message_or_callback=message.from_user.id)
#
#     group_username = message.text.strip()
#
#     # Защита на случай, если прислали не текст (фото, стикер и т.д.)
#     if not message.text:
#         return
#
#     logger.info(f"Пользователь ввёл ссылку: {group_username}")
#
#     # user = User.get(User.user_id == message.from_user.id)
#     # Создаём модель с таблицей, уникальной для конкретного пользователя
#     # GroupModel = create_group_model(user_id=message.from_user.id)  # Создаём таблицу для групп / ключевых слов
#     # GroupModel.create_table(safe=True)
#
#     logger.info(f"Создана новая таблица для пользователя {message.from_user.id}")
#     # Добавляем запись в таблицу
#     try:
#         # Удаляем старую запись, если есть
#         # GroupModel.delete().execute()
#         # Вставляем новую
#         # GroupModel.create(user_group=group_username)
#
#         group_list = [
#             group.strip()
#             for group in group_username.split('\n')
#             if group.strip()
#         ]
#
#         add_user_group(user_id=message.from_user.id, group=group_list)
#
#         await message.answer(t("group_added", lang=user_lang, group=group_username))
#         logger.info(f"username {group_username} добавлено пользователем {message.from_user.id}")
#     except Exception as e:
#         if "UNIQUE constraint failed" in str(e):
#             await message.answer(t("group_already_added", lang=user_lang))
#         else:
#             await message.answer(t("group_add_error", lang=user_lang))
#         logger.error(f"Ошибка при добавлении ключевого слова: {e}")
#     await state.clear()  # Завершаем текущее состояние машины состояния
