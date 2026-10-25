from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger  # https://github.com/Delgan/loguru

from account_manager.utilit import normalize_telegram_link
from database.group_user_database import add_user_group
from handlers.user_language import determines_user_language
from keyboards.keyboards import back_keyboard
from locales.locales import t
from states.states import MyStates
from states.states import PersonalTrackingStateGroupInput

router = Router(name=__name__)

"""
Добавляет одну или несколько групп/каналов для отслеживания ключевых слов.

Принимает username или ссылку на группу/канал (одну или список через перенос строки),
проверяет валидность и сохраняет в таблицу `Groups` базы данных `data/bot.db`.
"""


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

    group_list = [group.strip() for group in target_input.split('\n') if group.strip()]

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


"""
Загружает список групп/каналов из .txt файла и сохраняет валидные ссылки в базу данных.

Пользователь отправляет боту файл с расширением .txt, где каждая строка содержит
username или ссылку на группу/канал. Бот проверяет формат каждой записи и сохраняет
валидные данные в таблицу `Groups` базы данных `data/bot.db`.
"""


@router.callback_query(F.data == "settings_update_list")
async def handle_refresh_groups_list_cb(callback: CallbackQuery, state: FSMContext):
    """Обработчик команды Обновить список (инлайн)"""
    await callback.answer()

    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)

    logger.info(f"Пользователь {callback.from_user.id} перешел в меню 🔁 Обновить список")

    await state.set_state(MyStates.waiting_username_group)
    await callback.message.answer(
        text=t("update_list", lang=user_lang),
        reply_markup=back_keyboard(lang=user_lang, callback_data="settings_section_channels"),
        parse_mode="HTML"
    )
    await callback.answer()  # И только потом подтверждаем callback (чтобы убрать «часики»)


@router.message(MyStates.waiting_username_group, F.document)
async def handle_group_usernames_file(message: Message, state: FSMContext, bot):
    """
    Принимает TXT-файл со списком групп и каналов.
    """

    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=message.from_user.id)

    document = message.document
    file_name = document.file_name or ""

    # Проверяем расширение файла
    if not file_name.lower().endswith(".txt"):
        await message.answer(
            t("only_txt_files_supported", lang=user_lang),
            reply_markup=back_keyboard(lang=user_lang)
        )
        return
    # Получаем файл Telegram
    file = await bot.get_file(document.file_id)
    # Скачиваем содержимое
    file_bytes = await bot.download_file(file.file_path)
    # Читаем текст, поддерживая UTF-8 с BOM
    content = file_bytes.read().decode("utf-8-sig")
    # Получаем непустые строки
    group_list = [line.strip() for line in content.splitlines() if line.strip()]

    if not group_list:  # Если нет ссылок, то пишем пользователю, о том, что нет ссылок
        await message.answer(t("empty_file_no_usernames", lang=user_lang))
        await state.clear()
        return
    # Проверяем и нормализуем ссылки
    normalized_groups = []  # Список с группами / каналами пользователей

    for group in group_list:
        normalized_link = normalize_telegram_link(group)

        if normalized_link is None:
            await message.answer(
                text="⚠️ Проверьте правильность ссылок в файле.",
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


@router.message(MyStates.waiting_username_group, ~F.document)
async def process_non_text_group_input(message: Message, state: FSMContext):
    """Просит пользователя отправить TXT-файл."""
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=message.from_user.id)
    await message.answer(
        text="⚠️ Отправьте TXT-файл со ссылками или username групп и каналов.",
        parse_mode="HTML",
        reply_markup=back_keyboard(lang=user_lang)  # Кнопка назад
    )
    await state.clear()  # Очищаем состояние, что бы не получить случайное срабатывание
