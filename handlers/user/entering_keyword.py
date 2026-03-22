# -*- coding: utf-8 -*-
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger

from database.database import User, create_keywords_model
from keyboards.user.keyboards import back_keyboard
from locales.locales import get_text
from states.states import MyStates
from aiogram import Router

router = Router(name=__name__)


@router.message(F.text == "🔍 Ввод ключевого слова")
async def handle_enter_keyword_menu(message: Message, state: FSMContext):
    """
    Обработчик команды "🔍 Ввод ключевого слова".

    Очищает текущее состояние FSM, получает данные пользователя из базы,
    логирует переход в меню и отправляет приглашение ввести ключевые слова.
    Поддерживает ввод нескольких слов, разделённых переносами строк.

    Переводит пользователя в состояние ожидания ввода (MyStates.entering_keyword).

    :param message: (Message) Объект входящего сообщения от пользователя.
    :param state: (FSMContext) Контекст машины состояний, используется для сброса и установки состояния.
    :return: None
    """
    await state.clear()  # Завершаем текущее состояние машины состояния
    telegram_user = message.from_user
    user = User.get(User.user_id == telegram_user.id)

    logger.info(
        f"Пользователь {telegram_user.id} {telegram_user.username} {telegram_user.first_name} {telegram_user.last_name} перешел в меню 🔍 Ввод ключевого слова")

    await message.answer(
        get_text(user.language, "enter_keyword"),
        reply_markup=back_keyboard()  # клавиатура назад
    )
    await state.set_state(MyStates.entering_keyword)


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
    logger.info(f"Пользователь ввёл ключевое слово: {raw_input}")

    keywords_list = [
        keyword.strip()
        for keyword in raw_input.split('\n')
        if keyword.strip()
    ]

    if not keywords_list:
        await message.answer("⚠️ Вы не указали ни одного ключевого слова.")
        await state.clear()  # Завершаем текущее состояние машины состояния
        return

    # Создаём модель с таблицей, уникальной для конкретного пользователя
    KeywordsModel = create_keywords_model(user_id=telegram_user.id)  # Создаём таблицу для групп / ключевых слов

    # Проверяем, существует ли таблица (если нет — создаём)
    if not KeywordsModel.table_exists():
        KeywordsModel.create_table()
        logger.info(f"Создана новая таблица для пользователя {telegram_user.id}")

    added_keywords = []
    skipped_keywords = []
    error_keywords = []

    # Add each keyword one by one
    for keyword in keywords_list:
        try:
            KeywordsModel.create(user_keyword=keyword)
            added_keywords.append(keyword)
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                skipped_keywords.append(keyword)
            else:
                error_keywords.append((keyword, str(e)))
                logger.error(f"Error adding keyword {keyword}: {e}")

    # Format response message
    response_parts = []

    if added_keywords:
        keywords_preview = added_keywords[:10]  # Show first 10
        keywords_text = "\n".join(f"• {kw}" for kw in keywords_preview)
        if len(added_keywords) > 10:
            keywords_text += f"\n... и ещё {len(added_keywords) - 10}"
        response_parts.append(
            f"✅ Добавлено ключевых слов: {len(added_keywords)}\n{keywords_text}"
        )

    if skipped_keywords:
        skipped_preview = skipped_keywords[:5]  # Show first 5
        skipped_text = "\n".join(f"• {kw}" for kw in skipped_preview)
        if len(skipped_keywords) > 5:
            skipped_text += f"\n... и ещё {len(skipped_keywords) - 5}"
        response_parts.append(
            f"⚠️ Уже были добавлены ({len(skipped_keywords)}):\n{skipped_text}"
        )

    if error_keywords:
        error_text = "\n".join(f"• {kw}: {err}" for kw, err in error_keywords[:3])
        if len(error_keywords) > 3:
            error_text += f"\n... и ещё {len(error_keywords) - 3} ошибок"
        response_parts.append(f"❌ Ошибки при добавлении:\n{error_text}")

    # Summary
    summary = (
        f"\n📊 Итого:\n"
        f"• Добавлено: {len(added_keywords)}\n"
        f"• Пропущено (дубликаты): {len(skipped_keywords)}\n"
        f"• Ошибки: {len(error_keywords)}"
    )
    response_parts.append(summary)

    await message.answer("\n\n".join(response_parts))

    # Log statistics
    logger.info(
        f"Keywords import for user {telegram_user.id}: "
        f"added={len(added_keywords)}, skipped={len(skipped_keywords)}, errors={len(error_keywords)}"
    )

    await state.clear()  # Завершаем текущее состояние машины состояния


