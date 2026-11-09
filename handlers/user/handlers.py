import os

from aiogram import F, Router
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, LabeledPrice, Message, LinkPreviewOptions
from loguru import logger  # https://github.com/Delgan/loguru

from account_manager.parser import filter_messages
from account_manager.session import find_session_file
from core.config import version
from database.database import (
    # User,  # Таблица User объединена с users_personal_trackings
    getting_number_records_database
)
from database.users_groups import get_group_count
from database.users_keywords import get_keywords_count
from database.users_personal_trackings import get_session_count, UsersPersonalTrackings
from handlers.user_language import determines_user_language
from keyboards.keyboards import (
    get_lang_keyboard, menu_launch_tracking_keyboard, connect_keyboard_account,
    get_stars_topup_inline_keyboard, menu_user_admin_keyboard
)
from locales.locales import t

router = Router(name=__name__)


def generate_welcome_message(user_language: str, user_tg_id: int) -> str:
    """
    Генерирует приветственное сообщение для пользователя с актуальной статистикой.

    :param user_language: (str) Код языка пользователя ('ru', 'en').
    :param user_tg_id: (int) Telegram ID пользователя.
    :return: (str) Сформированный текст приветственного сообщения.
    """
    groups_count = getting_number_records_database()  # Общее число найденных групп с помощью Ai.
    count = get_session_count(user_id=user_tg_id)  # Сессии пользователя дял отслеживания групп / каналов
    group_count = get_group_count(user_id=user_tg_id)  # Группы для для отслеживания
    keywords_count = get_keywords_count(user_id=user_tg_id)  # Ключевые слова

    return t(
        "welcome_message_template",
        lang=user_language,
        version=version,
        groups_count=groups_count,
        count=count,
        group_count=group_count,
        # get_groups=get_groups,
        keywords_count=keywords_count
    )


def get_or_create_user(user_tg):
    """
    Получает существующего пользователя из базы данных или создаёт нового.

    :param user_tg: Объект пользователя Telegram (aiogram.types.User).
    :return: (UsersPersonalTrackings) Экземпляр модели пользователя в БД.
    """
    user, created = UsersPersonalTrackings.get_or_create(
        user_id=user_tg.id,
        defaults={
            "user_username": user_tg.username,
            "user_firstname": user_tg.first_name,
            "user_last_name": user_tg.last_name,
            "language": "unset"  # ← ключевое: "unset" = язык не выбран
        }
    )
    if not created:
        user.user_username = user_tg.username
        user.user_firstname = user_tg.first_name
        user.user_last_name = user_tg.last_name
        user.save()

    logger.info(
        f"Пользователь {user_tg.id} {user_tg.username} {user_tg.first_name} {user_tg.last_name} начал работу с ботом.")

    return user


async def show_main_menu(message: Message, user_tg, state: FSMContext, edit: bool = False):
    """
    Универсальное отображение главного меню бота.

    :param message: (Message) Входящее сообщение или сообщение коллбэка.
    :param user_tg: Объект пользователя Telegram.
    :param state: (FSMContext) Контекст машины состояний FSM.
    :param edit: (bool) Флаг редактирования текущего сообщения вместо отправки нового.
    """
    await state.clear()
    user = get_or_create_user(user_tg)

    if user.language == "unset":
        text = t("welcome_choose_lang", lang="ru")
    else:
        text = generate_welcome_message(user_language=user.language, user_tg_id=user_tg.id)
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
    Обработчик команды /start от пользователя.

    :param message: (Message) Объект входящего сообщения Telegram.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    try:
        await show_main_menu(message, message.from_user, state, edit=False)
    except TelegramForbiddenError:
        logger.error(f"Пользователь {message.from_user.id, message.from_user.username} заблокировал бота")
    except Exception as e:
        logger.exception(e)


@router.callback_query(F.data == "menu_main")
async def handle_back_to_main_menu_cb(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн-кнопки "Назад" для возврата в главное меню.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    await state.clear()  # Сбрасываем состояние пользователя, для не допущения ошибки, если действие не было завершено
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    await callback.message.edit_text(
        text=generate_welcome_message(user_language=user_lang, user_tg_id=callback.from_user.id),
        reply_markup=menu_user_admin_keyboard(lang=user_lang, user_id=callback.from_user.id),
        parse_mode="HTML",
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )


@router.callback_query(F.data.in_({"lang_ru", "lang_en"}))
async def handle_language_selection_cb(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн-выбора языка интерфейса (русский / английский).

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    try:
        await state.clear()
        user = get_or_create_user(callback.from_user)
        selected_lang = "ru" if callback.data == "lang_ru" else "en"
        user.language = selected_lang
        user.save()
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


@router.message((F.text == t('change_language_button', 'ru')) | (F.text == t('change_language_button', 'en')))
async def handle_change_language(message: Message, state: FSMContext):
    """
    Обработчик текстовой команды смены языка интерфейса.

    :param message: (Message) Объект входящего сообщения Telegram.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    await state.clear()
    user_lang = determines_user_language(message_or_callback=message.from_user.id)
    await message.answer(
        t("welcome_ask_language", lang=user_lang),
        reply_markup=get_lang_keyboard(lang=user_lang)
    )


@router.callback_query(F.data == "settings_change_language")
async def handle_change_language_cb(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн-кнопки смены языка интерфейса.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    try:
        await state.clear()
        user_lang = determines_user_language(message_or_callback=callback.from_user.id)
        try:
            await callback.message.edit_text(
                text=t("welcome_ask_language", lang=user_lang),
                reply_markup=get_lang_keyboard(lang=user_lang)
            )
        except Exception:
            await callback.message.answer(
                text=t("welcome_ask_language", lang=user_lang),
                reply_markup=get_lang_keyboard(lang=user_lang)
            )
        await callback.answer()
    except Exception as e:
        logger.exception(e)


@router.callback_query(F.data == "menu_launch_tracking")
async def handle_start_tracking_cb(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн-команды запуска отслеживания сообщений.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    await callback.answer()
    # await start_tracking_internal(callback.message, callback.from_user, state)
    await state.clear()
    try:
        # Определяем язык пользователя, который пользователь выбрал при старте бота
        user_lang = determines_user_language(message_or_callback=callback.from_user.id)
        # user = User.get(User.user_id == callback.from_user.id)
        user = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == callback.from_user.id)
        logger.info(
            f"Пользователь {callback.from_user.id} {callback.from_user.username} {callback.from_user.first_name} перешел в меню запуска парсинга.")

        session_dir = os.path.join("accounts", str(callback.from_user.id))
        os.makedirs(session_dir, exist_ok=True)

        session_path = await find_session_file(
            user_id=callback.from_user.id,
            message=callback.message
        )

        logger.info(session_path)
        if session_path is None:
            logger.warning("Нет подключенного аккаунта")
            await callback.message.answer(
                text=t("no_connected_account", lang=user_lang),
                reply_markup=connect_keyboard_account(lang=user_lang)
            )
            return

        await callback.message.answer(
            t("launching_tracking", lang=user_lang),
            reply_markup=menu_launch_tracking_keyboard(lang=user_lang)
        )

        await filter_messages(
            message=callback.message,
            user_id=callback.from_user.id,
        )
    except Exception as e:
        logger.exception(e)


@router.callback_query(F.data == "settings_topup_stars")
async def handle_stars_balance_cb(callback: CallbackQuery, state: FSMContext):
    """
    Отображает баланс Telegram Stars и инлайн-кнопки для пополнения.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    await state.clear()
    # user = User.get(User.user_id == callback.from_user.id)
    user = UsersPersonalTrackings.get(UsersPersonalTrackings.user_id == callback.from_user.id)
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)

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
    """
    Обрабатывает выбор количества Telegram Stars для покупки через Invoice.

    :param callback: (CallbackQuery) Объект входящего callback-запроса с количеством звёзд.
    """

    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)

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
