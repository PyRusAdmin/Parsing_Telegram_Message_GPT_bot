from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger

from database.database import User
from handlers.user_language import determines_user_language
from keyboards.keyboards import back_keyboard
from locales.locales import t
from states.states import MyStates

router = Router(name=__name__)


@router.message((F.text == t('enter_keyword_button', 'ru')) | (F.text == t('enter_keyword_button', 'en')))
async def handle_enter_keyword_menu(message: Message, state: FSMContext):
    """
    Обработчик команды "🔍 Ввод ключевого слова" (текст).
    """
    await state.clear()  # Завершаем текущее состояние машины состояния
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=message.from_user.id)

    logger.info(
        f"Пользователь {message.from_user.id} {message.from_user.username} {message.from_user.first_name} {message.from_user.last_name} перешел в меню 🔍 Ввод ключевого слова"
    )

    await message.answer(
        t("enter_keyword", lang=user_lang),
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
    )
    await state.set_state(MyStates.entering_keyword)


@router.callback_query(F.data == "settings_enter_keyword")
async def handle_enter_keyword_menu_cb(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн-кнопки "🔍 Ввод ключевого слова".
    """
    await state.clear()
    telegram_user = callback.from_user
    user = User.get(User.user_id == telegram_user.id)

    logger.info(
        f"Пользователь {telegram_user.id} перешел в меню 🔍 Ввод ключевого слова через инлайн-кнопку"
    )

    await callback.message.answer(
        t("enter_keyword", lang=user.language),
        reply_markup=back_keyboard(lang=user.language, callback_data="menu_settings")
    )
    await state.set_state(MyStates.entering_keyword)
    await callback.answer()


@router.message(MyStates.entering_keyword)
async def handle_keywords_submission(message: Message, state: FSMContext):
    """
    Обработчик ввода ключевых слов пользователем.

    Принимает одно или несколько ключевых слов/фраз, разделённых переносами строк,
    и добавляет их в пользовательскую таблицу базы данных. Поддерживает массовую загрузку.

    Обрабатывает дубликаты и ошибки, формирует детализированный отчёт о результате операции.

    После обработки сбрасывает состояние FSM.

    - Используется динамическая модель `create_keywords_model` для изоляции данных пользователей.
    - В ответе показываются превью списков (первые N элементов), чтобы избежать спама.
    - Все действия логируются для аудита и отладки.

    :param message: (Message) Объект входящего сообщения с ключевыми словами.
    :param state: (FSMContext) Контекст машины состояний, используется для сброса состояния после обработки.
    :return: None
    :raise Exception: При ошибке добавления в БД (например, нарушение уникальности или другие DB-ошибки).
                      Обрабатывается локально с учётом типа ошибки и отправкой детализированного отчёта пользователю.
    """

    raw_input = message.text.strip()
    telegram_user = message.from_user
    user = User.get(User.user_id == telegram_user.id)
    logger.info(f"Пользователь ввёл ключевое слово: {raw_input}")

    keywords_list = [
        keyword.strip()
        for keyword in raw_input.split('\n')
        if keyword.strip()
    ]

    if not keywords_list:
        await message.answer(t("no_keywords_entered", lang=user.language))
        await state.clear()
        return

    # Создаём модель с таблицей, уникальной для конкретного пользователя
    keywords_model = create_keywords_model(user_id=telegram_user.id)  # Создаём таблицу для групп / ключевых слов

    # Проверяем, существует ли таблица (если нет — создаём)
    if not keywords_model.table_exists():
        keywords_model.create_table()
        logger.info(f"Создана новая таблица для пользователя {telegram_user.id}")

    added_keywords = []
    skipped_keywords = []
    error_keywords = []

    # Добавляйте каждое ключевое слово по очереди
    for keyword in keywords_list:
        try:
            keywords_model.create(user_keyword=keyword)
            added_keywords.append(keyword)
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                skipped_keywords.append(keyword)
            else:
                error_keywords.append((keyword, str(e)))
                logger.error(f"Error adding keyword {keyword}: {e}")

    # Форматирование ответного сообщения
    response_parts = []

    if added_keywords:
        keywords_preview = added_keywords[:10]  # Show first 10
        keywords_text = "\n\n".join(f"• {kw}" for kw in keywords_preview)
        if len(added_keywords) > 10:
            keywords_text += f"\n...\n{t('keywords_and_more', lang=user.language, count=len(added_keywords) - 10)}\n"
        response_parts.append(
            f"✅ {t('keywords_added_count', lang=user.language, count=len(added_keywords))}\n{keywords_text}\n"
        )

    if skipped_keywords:
        skipped_preview = skipped_keywords[:5]  # Show first 5
        skipped_text = "\n".join(f"• {kw}" for kw in skipped_preview)
        if len(skipped_keywords) > 5:
            skipped_text += f"\n...\n{t('keywords_and_more', lang=user.language, count=len(skipped_keywords) - 5)}\n"
        response_parts.append(
            f"⚠️ {t('keywords_already_added', lang=user.language, count=len(skipped_keywords))}:\n{skipped_text}\n"
        )

    if error_keywords:
        error_text = "\n".join(f"• {kw}: {err}" for kw, err in error_keywords[:3])
        if len(error_keywords) > 3:
            error_text += f"\n...\n{t('keywords_and_more_errors', lang=user.language, count=len(error_keywords) - 3)}\n"
        response_parts.append(f"❌ {t('keywords_add_errors', lang=user.language)}:\n{error_text}\n")

    # Резюме
    response_parts.append(
        (
            f"\n📊 {t('keywords_summary', lang=user.language)}\n"
            f"• {t('keywords_added', lang=user.language)}: {len(added_keywords)}\n"
            f"• {t('keywords_skipped', lang=user.language)}: {len(skipped_keywords)}\n"
            f"• {t('keywords_errors', lang=user.language)}: {len(error_keywords)}"
        )
    )

    await message.answer("\n\n".join(response_parts))

    # Регистрация статистики
    logger.info(
        f"Keywords import for user {telegram_user.id}: "
        f"added={len(added_keywords)}, skipped={len(skipped_keywords)}, errors={len(error_keywords)}"
    )

    await state.clear()  # Завершаем текущее состояние машины состояния
