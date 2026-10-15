import os

from aiogram import F, Router
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, LabeledPrice, Message, LinkPreviewOptions
from loguru import logger

from account_manager.parser import filter_messages
from account_manager.session import find_session_file
from database.database import (
    User, getting_number_records_database, get_session_count, get_target_group_count, get_keywords_count,
    get_tracked_channels_count, Groups
)
from keyboards.keyboards import (
    get_lang_keyboard, settings_keyboard, back_keyboard, menu_launch_tracking_keyboard,
    connect_keyboard_account, get_stars_topup_inline_keyboard, menu_user_admin_keyboard
)
from locales.locales import t
from states.states import MyStates

router = Router(name=__name__)


def generate_welcome_message(user_language: str, user_tg_id: int) -> str:
    """
    Генерирует приветственное сообщение для пользователя с подставленными данными.
    """
    version = "0.1.0"
    groups_count = getting_number_records_database()  # Общее число найденных групп
    count = get_session_count(user_id=user_tg_id)  # Сессии пользователя
    group_count = get_target_group_count(user_id=user_tg_id)  # Группы для пересылки
    get_groups = get_tracked_channels_count(user_id=user_tg_id)  # Отслеживаемые каналы
    keywords_count = get_keywords_count(user_id=user_tg_id)  # Ключевые слова

    return t(
        "welcome_message_template",
        lang=user_language,
        version=version,
        groups_count=groups_count,
        count=count,
        group_count=group_count,
        get_groups=get_groups,
        keywords_count=keywords_count
    )


def get_or_create_user(user_tg):
    """
    Получает существующего пользователя из базы данных или создаёт нового, если он не существует.
    """
    user, created = User.get_or_create(
        user_id=user_tg.id,
        defaults={
            "username": user_tg.username,
            "first_name": user_tg.first_name,
            "last_name": user_tg.last_name,
            "language": "unset"  # ← ключевое: "unset" = язык не выбран
        }
    )
    if not created:
        user.username = user_tg.username
        user.first_name = user_tg.first_name
        user.last_name = user_tg.last_name
        user.save()

    logger.info(
        f"Пользователь {user_tg.id} {user_tg.username} {user_tg.first_name} {user_tg.last_name} начал работу с ботом.")

    return user


async def show_main_menu(message: Message, user_tg, state: FSMContext, edit: bool = False):
    """
    Универсальное отображение главного меню бота.
    """
    await state.clear()
    user = get_or_create_user(user_tg)
    # is_admin = user_tg.id in ADMIN_USER_ID

    if user.language == "unset":
        text = "👋 Привет! Пожалуйста, выберите язык / Please choose your language:"
        # reply_markup = get_lang_keyboard()
    else:
        text = generate_welcome_message(user_language=user.language, user_tg_id=user_tg.id)
        # reply_markup = main_admin_keyboard(lang=user.language) if is_admin else main_menu_keyboard(lang=user.language)

    if edit:
        try:
            await message.edit_text(
                text=text,
                reply_markup=menu_user_admin_keyboard(lang=user.language, user_id=user_tg.id),
                parse_mode="HTML",
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
            return
        except Exception:
            pass

    await message.answer(
        text=text,
        reply_markup=menu_user_admin_keyboard(lang=user.language, user_id=user_tg.id),
        parse_mode="HTML",
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )


@router.message(CommandStart())
async def handle_start_command(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /start.
    """
    try:
        await show_main_menu(message, message.from_user, state, edit=False)
    except TelegramForbiddenError:
        logger.error(f"Пользователь {message.from_user.id, message.from_user.username} заблокировал бота")
    except Exception as e:
        logger.exception(e)


@router.message((F.text == t('back_button', 'ru')) | (F.text == t('back_button', 'en')))
async def handle_back_to_main_menu(message: Message, state: FSMContext):
    """
    Обработчик текстовой кнопки "Назад".
    """
    try:
        await show_main_menu(message, message.from_user, state, edit=False)
    except Exception as e:
        logger.exception(e)


@router.callback_query(F.data == "menu_main")
async def handle_back_to_main_menu_cb(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн-кнопки "Назад в главное меню".
    """
    try:
        await show_main_menu(callback.message, callback.from_user, state, edit=True)
        await callback.answer()
    except Exception as e:
        logger.exception(e)


@router.callback_query(F.data.in_({"lang_ru", "lang_en"}))
async def handle_language_selection_cb(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн-выбора языка.
    """
    try:
        await state.clear()
        user = get_or_create_user(callback.from_user)
        selected_lang = "ru" if callback.data == "lang_ru" else "en"
        user.language = selected_lang
        user.save()

        # is_admin = callback.from_user.id in ADMIN_USER_ID
        # reply_markup = main_admin_keyboard(lang=user.language) if is_admin else main_menu_keyboard(lang=user.language)
        welcome_text = generate_welcome_message(user_language=user.language, user_tg_id=callback.from_user.id)
        confirmation_text = t("lang_selected", lang=user.language)

        full_text = f"{confirmation_text}\n\n{welcome_text}"
        try:
            await callback.message.edit_text(
                text=full_text,
                reply_markup=menu_user_admin_keyboard(lang=user.language, user_id=callback.from_user.id),
                parse_mode="HTML",
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
        except Exception:
            await callback.message.answer(
                text=full_text,
                reply_markup=menu_user_admin_keyboard(lang=user.language, user_id=callback.from_user.id),
                parse_mode="HTML",
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
        await callback.answer()
    except Exception as e:
        logger.exception(e)


@router.message((F.text == t('russian_language_button', 'ru')) | (F.text == t('english_language_button', 'en')))
async def handle_language_selection(message: Message, state: FSMContext):
    """
    Обработчик текстового выбора языка.
    """
    try:
        await state.clear()
        user = get_or_create_user(message.from_user)
        if message.text == t('russian_language_button', 'ru'):
            user.language = "ru"
            confirmation_text = t("lang_selected", lang="ru")
        else:
            user.language = "en"
            confirmation_text = t("lang_selected", lang="en")
        user.save()

        # is_admin = message.from_user.id in ADMIN_USER_ID
        # reply_markup = main_admin_keyboard(lang=user.language) if is_admin else main_menu_keyboard(lang=user.language)
        await message.answer(
            confirmation_text,
            reply_markup=menu_user_admin_keyboard(lang=user.language, user_id=message.from_user.id)
        )
    except Exception as e:
        logger.exception(e)


async def show_settings_menu(message: Message, user_tg, state: FSMContext):
    """Отображение меню настроек"""
    await state.clear()
    user = User.get(User.user_id == user_tg.id)
    # text = t("settings_message", lang=user.language)
    # kb = settings_keyboard(lang=user.language)
    # if edit:
    #     try:
    #         await message.edit_text(text, reply_markup=kb)
    #         return
    #     except Exception:
    #         pass
    await message.edit_text(
        text=t("settings_message", lang=user.language),  # Текст меню настройки
        reply_markup=settings_keyboard(lang=user.language)
    )


@router.message((F.text == t('settings_button', 'ru')) | (F.text == t('settings_button', 'en')))
async def handle_settings_menu(message: Message, state: FSMContext):
    """Обработчик команды Настройки (текст)"""
    try:
        await show_settings_menu(message, message.from_user, state)
    except Exception as e:
        logger.exception(e)


@router.callback_query(F.data == "menu_settings")
async def handle_settings_menu_cb(callback: CallbackQuery, state: FSMContext):
    """Обработчик инлайн-кнопки Настройки"""
    try:
        await show_settings_menu(callback.message, callback.from_user, state)
        await callback.answer()
    except Exception as e:
        logger.exception(e)


@router.message((F.text == t('change_language_button', 'ru')) | (F.text == t('change_language_button', 'en')))
async def handle_change_language(message: Message, state: FSMContext):
    """Обработчик смены языка (текст)"""
    try:
        await state.clear()
        await message.answer(
            t("welcome_ask_language", lang="ru"),
            reply_markup=get_lang_keyboard()
        )
    except Exception as e:
        logger.exception(e)


@router.callback_query(F.data == "settings_change_language")
async def handle_change_language_cb(callback: CallbackQuery, state: FSMContext):
    """Обработчик инлайн-кнопки смены языка"""
    try:
        await state.clear()
        text = t("welcome_ask_language", lang="ru")
        kb = get_lang_keyboard()
        try:
            await callback.message.edit_text(text=text, reply_markup=kb)
        except Exception:
            await callback.message.answer(text=text, reply_markup=kb)
        await callback.answer()
    except Exception as e:
        logger.exception(e)


async def start_tracking_internal(message: Message, user_tg, state: FSMContext):
    """Внутренняя логика запуска отслеживания"""
    await state.clear()
    try:
        user = User.get(User.user_id == user_tg.id)
        logger.info(
            f"Пользователь {user_tg.id} {user_tg.username} {user_tg.first_name} перешел в меню запуска парсинга.")

        session_dir = os.path.join("accounts", str(user_tg.id))
        os.makedirs(session_dir, exist_ok=True)

        session_path = await find_session_file(
            user_id=user_tg.id,
            user=user,
            message=message
        )

        logger.info(session_path)
        if session_path is None:
            logger.warning("Нет подключенного аккаунта")
            await message.answer(
                text="Нет подключенного аккаунта. Подключите аккаунт.",
                reply_markup=connect_keyboard_account(lang=user.language)
            )
            return

        await message.answer(
            t("launching_tracking", lang=user.language),
            reply_markup=menu_launch_tracking_keyboard(lang=user.language)
        )

        await filter_messages(
            message=message,
            user_id=user_tg.id,
            user=user,
        )
    except Exception as e:
        logger.exception(e)


@router.message((F.text == t('launch_tracking_button', 'ru')) | (F.text == t('launch_tracking_button', 'en')))
async def handle_start_tracking(message: Message, state: FSMContext):
    """Обработчик команды Запуск отслеживания (текст)"""
    await start_tracking_internal(message, message.from_user, state)


@router.callback_query(F.data == "menu_launch_tracking")
async def handle_start_tracking_cb(callback: CallbackQuery, state: FSMContext):
    """Обработчик команды Запуск отслеживания (инлайн)"""
    await callback.answer()
    await start_tracking_internal(callback.message, callback.from_user, state)


@router.message((F.text == t('update_list_button', 'ru')) | (F.text == t('update_list_button', 'en')))
async def handle_refresh_groups_list(message: Message, state: FSMContext):
    """Обработчик команды Обновить список (текст)"""
    user = User.get(User.user_id == message.from_user.id)
    logger.info(f"Пользователь {message.from_user.id} перешел в меню 🔁 Обновить список")
    await message.answer(
        text=t("update_list", lang=user.language),
        reply_markup=back_keyboard(lang=user.language, callback_data="menu_settings"),
        parse_mode="HTML"
    )
    await state.set_state(MyStates.waiting_username_group)


@router.callback_query(F.data == "settings_update_list")
async def handle_refresh_groups_list_cb(callback: CallbackQuery, state: FSMContext):
    """Обработчик команды Обновить список (инлайн)"""
    await callback.answer()
    user = User.get(User.user_id == callback.from_user.id)
    logger.info(f"Пользователь {callback.from_user.id} перешел в меню 🔁 Обновить список")
    await callback.message.answer(
        text=t("update_list", lang=user.language),
        reply_markup=back_keyboard(lang=user.language, callback_data="menu_settings"),
        parse_mode="HTML"
    )
    await state.set_state(MyStates.waiting_username_group)


@router.message(MyStates.waiting_username_group, F.document)
async def handle_group_usernames_file(message: Message, state: FSMContext, bot):
    """
    Обработчик загрузки .txt файла со списком групп/каналов.
    """
    user = User.get(User.user_id == message.from_user.id)
    document = message.document

    if not document.file_name.endswith(".txt"):
        await message.answer(t("only_txt_files_supported", lang=user.language))
        return

    file = await bot.get_file(document.file_id)
    file_bytes = await bot.download_file(file.file_path)
    content = file_bytes.read().decode("utf-8")

    usernames = [line.strip() for line in content.splitlines() if line.strip()]

    if not usernames:
        await message.answer(t("empty_file_no_usernames", lang=user.language))
        await state.clear()
        return

    added_count = 0
    skipped_count = 0
    errors_count = 0

    for username in usernames:
        username = username if username.startswith("@") else f"@{username}"
        try:
            Groups.create(
                user_id=message.from_user.id,
                username=username
            )
            added_count += 1
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                skipped_count += 1
            else:
                errors_count += 1
                logger.error(f"Ошибка при добавлении {username}: {e}")

    response = t(
        "groups_upload_summary",
        lang=user.language,
        added=added_count,
        skipped=skipped_count,
        errors=errors_count
    )
    await message.answer(response, reply_markup=settings_keyboard(lang=user.language))
    await state.clear()


@router.message((F.text == t('topup_stars_button', 'ru')) | (F.text == t('topup_stars_button', 'en')))
async def handle_stars_balance(message: Message, state: FSMContext):
    """Профиль и пополнение звезд (текст)"""
    await state.clear()
    user = User.get(User.user_id == message.from_user.id)
    user_lang = user.language if user.language != "unset" else "ru"

    keyboard = get_stars_topup_inline_keyboard(user_lang)
    msg_text = t("stars_balance_msg", lang=user_lang, stars=user.stars)

    await message.answer(text=msg_text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data == "settings_topup_stars")
async def handle_stars_balance_cb(callback: CallbackQuery, state: FSMContext):
    """Профиль и пополнение звезд (инлайн)"""
    await state.clear()
    user = User.get(User.user_id == callback.from_user.id)
    user_lang = user.language if user.language != "unset" else "ru"
    # keyboard = get_stars_topup_inline_keyboard(user_lang)
    # msg_text = t("stars_balance_msg", lang=user_lang, stars=user.stars)
    try:
        await callback.message.edit_text(
            text=t("stars_balance_msg", lang=user_lang, stars=user.stars),
            reply_markup=get_stars_topup_inline_keyboard(user_lang),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.answer(
            text=t("stars_balance_msg", lang=user_lang, stars=user.stars),
            reply_markup=get_stars_topup_inline_keyboard(user_lang),
            parse_mode="HTML"
        )
    await callback.answer()


@router.callback_query(F.data.startswith("buy_stars_"))
async def handle_buy_stars_callback(callback: CallbackQuery):
    """Обрабатывает выбор количества звезд для покупки через Telegram Stars"""
    user = User.get(User.user_id == callback.from_user.id)
    user_lang = user.language if user.language != "unset" else "ru"

    action = callback.data.split("_")[2]

    if action == "cancel":
        await callback.message.delete()
        await callback.answer()
        return

    try:
        amount = int(action)
    except ValueError:
        await callback.answer("Error", show_alert=True)
        return

    await callback.message.answer_invoice(
        title=t("stars_invoice_title", lang=user_lang),
        description=t("stars_invoice_desc", lang=user_lang, amount=amount),
        payload=f"topup_stars_{amount}",
        provider_token="",  # must be empty for Telegram Stars
        currency="XTR",
        prices=[LabeledPrice(label="Stars", amount=amount)]
    )
    await callback.answer()
