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
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=message.from_user.id)

    target_input = message.text.strip()

    group_list = [
        group.strip()
        for group in target_input.split('\n')
        if group.strip()
    ]

    if not group_list:  # Если нет списка, то присылаем пользователю сообщение, что нет ссылки
        await message.answer(
            text="⚠️ Отправьте хотя бы одну ссылку или username.",
            parse_mode="HTML",
            reply_markup=back_keyboard(lang=user_lang)  # Кнопка назад
        )
        return

    normalized_groups = []  # Список с группами / каналами пользователей

    for group in group_list:
        normalized_link = normalize_telegram_link(group)

        if normalized_link is None:
            await message.answer(
                text="⚠️ Проверьте правильность ссылок.",
                parse_mode="HTML",
                reply_markup=back_keyboard(lang=user_lang)  # Кнопка назад
            )
            return

        normalized_groups.append(normalized_link)

    # Безопасно добавляет список групп/каналов в базу данных data/bot.db в таблицу user_groups (Groups)
    add_user_group(
        user_id=message.from_user.id,
        group=normalized_groups
    )

    await message.answer(
        text="✅ Группа / группы записаны в базу данных.",
        parse_mode="HTML",
        reply_markup=back_keyboard(lang=user_lang)  # Кнопка назад
    )
    await state.clear()  # Очищаем состояние, что бы не получить случайное срабатывание


@router.message(PersonalTrackingStateGroupInput.waiting_for_target_link_group_input, ~F.text)
async def process_non_text_group_input(message: Message, state: FSMContext):
    """Обрабатывает сообщения, которые не содержат текст."""
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=message.from_user.id)
    await message.answer(
        text="⚠️ Отправьте ссылку или username группы/канала текстовым сообщением.",
        parse_mode="HTML",
        reply_markup=back_keyboard(lang=user_lang)  # Кнопка назад
    )
    await state.clear()  # Очищаем состояние, что бы не получить случайное срабатывание
