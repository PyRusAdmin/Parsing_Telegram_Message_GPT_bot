# -*- coding: utf-8 -*-
import asyncio

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from asgiref.sync import sync_to_async
from g4f.client import Client
from groq import AsyncGroq
from loguru import logger
from openai import AsyncOpenAI

from ai.ai import category_assignment
from core.config import GROQ_API_KEY
from core.config import OPENROUTER_API_KEY
from database.database import TelegramGroup, db, get_groups_without_category, User
from keyboards.admin.keyboards import category_method_keyboard, admin_keyboard
from locales.locales import t
from states.states import CategoryMethod

router = Router(name=__name__)


@router.message(F.text == "🏷️ Присвоить категорию")
async def checking_group_for_ai_db(message: Message, state: FSMContext):
    """Предлагает выбор метода присвоения категорий"""
    await state.set_state(CategoryMethod.waiting_for_method)

    user = User.get(User.user_id == message.from_user.id)

    await message.answer(
        t("ai_category_select_method", lang=user.language),
        reply_markup=category_method_keyboard(),
        parse_mode="HTML"
    )


async def get_best_g4f_model(client: Client) -> str:
    """
    Проверяет доступность моделей g4f и возвращает первую рабочую.
    Приоритет: llama-3.1-8b-instant → gpt-4o-mini → llama-3.2-3b → mistral-7b
    """
    # Список моделей по приоритету (от быстрой к медленной)
    models_to_check = [
        "llama-3.1-8b-instant",
        "gpt-4o-mini",
        "llama-3.2-3b",
        "mistral-7b",
        "llama-3.2-1b",
    ]

    test_prompt = [{"role": "user", "content": "Hi"}]

    for model in models_to_check:
        try:
            # Пробуем сделать быстрый тестовый запрос
            await asyncio.wait_for(
                asyncio.to_thread(
                    client.chat.completions.create,
                    model=model,
                    messages=test_prompt,
                    timeout=5
                ),
                timeout=7
            )
            logger.info(f"✅ Модель {model} доступна")
            return model
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Таймаут модели {model}, пробуем следующую...")
        except Exception as e:
            logger.warning(f"❌ Модель {model} не работает: {type(e).__name__}")
            continue

    # Если ничего не работает, возвращаем последнюю надежду
    logger.warning("⚠️ Ни одна модель не доступна, используем gpt-4o-mini по умолчанию")
    return "gpt-4o-mini"


@router.message(StateFilter(CategoryMethod.waiting_for_method))
async def process_category_method_choice(message: Message, state: FSMContext):
    """Обрабатывает выбор метода присвоения категорий"""
    user = User.get(User.user_id == message.from_user.id)

    if message.text == "⬅️ Назад":
        await state.clear()
        await message.answer(
            t("ai_category_back", lang=user.language),
            reply_markup=admin_keyboard()
        )
        return

    if message.text == "⚡️ Быстро (g4f.free)":
        await state.clear()
        client = Client()

        # 🔍 Определяем лучшую доступную модель
        status_msg = await message.answer(t("ai_category_checking_models", lang=user.language))
        model = await get_best_g4f_model(client)
        await status_msg.edit_text(t("ai_category_model_selected", lang=user.language, model=model))
        await asyncio.sleep(1)
        await status_msg.delete()

        await assign_categories(message, client, model)

    elif message.text == "🚀 Мощно (Openrouter API)":
        await state.clear()
        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
            timeout=30
        )
        # Лучшие бесплатные модели для классификации (выберите нужную):
        # 🏆 Лучшая для русского языка:
        model = "google/gemma-3-27b:free"
        # 🔥 Самая умная (уровень GPT-4):
        # model = "meta-llama/llama-3.3-70b-instruct:free"
        # ⚖️ Баланс скорости и качества:
        # model = "google/gemma-3-12b:free"
        # 🌐 Многоязычная:
        # model = "z-ai/glm-4.5-air:free"
        # 📊 Лёгкая и быстрая:
        # model = "meta-llama/llama-3.2-3b:free"
        await assign_categories(message, client, model="google/gemma-3n-e4b-it")

    elif message.text == "🚀 Мощно (GROQ API)":
        await state.clear()
        client = AsyncGroq(api_key=GROQ_API_KEY)
        model = "llama-3.1-8b-instant"
        await assign_categories(message, client, model)
    else:
        await message.answer(
            t("ai_category_select_from_keyboard", lang=user.language),
            reply_markup=category_method_keyboard()
        )


async def assign_categories(message: Message, client, model):
    """Универсальная функция присвоения категорий (любой AI клиент)"""
    user = User.get(User.user_id == message.from_user.id)

    status_msg = await message.answer(t("ai_category_processing", lang=user.language, total=0))

    try:
        # 1️⃣ Получаем группы для обработки
        groups_to_process = await get_groups_without_category()

        if not groups_to_process:
            await status_msg.edit_text(t("ai_category_all_have_categories", lang=user.language))
            return

        total = len(groups_to_process)
        logger.info(f"📦 Найдено {total} групп для обработки")

        await status_msg.edit_text(t("ai_category_processing", lang=user.language, total=total))

        # 2️⃣ Обрабатываем последовательно с немедленной записью в БД
        for i, group_data in enumerate(groups_to_process, 1):
            try:
                # AI запрос
                result = await category_assignment(group_data, client, model)

                if result.get("success") and result.get("category"):
                    # ✅ Сразу пишем в БД (в нижнем регистре)
                    category_lower = result["category"].lower()
                    await sync_to_async(lambda: TelegramGroup.update(category=category_lower)
                                        .where(TelegramGroup.telegram_id == result["telegram_id"])
                                        .execute(), thread_sensitive=True)()
                    logger.info(f"[{i}/{total}] ✅ {group_data['name']} → {category_lower}")
                else:
                    logger.warning(f"[{i}/{total}] ❌ {group_data['name']} — AI не определил")

                # Пауза только для g4f (чтобы не блокировали)
                if type(client).__name__ == 'Client':  # g4f клиент
                    await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"❌ Ошибка {group_data.get('name')}: {e}")
                continue

        # 3️⃣ Финал
        await status_msg.edit_text(t("ai_category_done", lang=user.language), parse_mode="HTML")

    except Exception as e:
        logger.exception(e)
        await status_msg.edit_text(t("ai_category_error", lang=user.language, error=str(e)))


@router.message(F.text == "📥 Получить группы без категории")
async def get_groups_without_category_message(message: Message):
    """Информация о группах без категории"""
    user = User.get(User.user_id == message.from_user.id)

    def _count():
        if db.is_closed():
            db.connect(reuse_if_open=True)
        return TelegramGroup.select().where(
            (TelegramGroup.username.is_null(False)) &
            (TelegramGroup.category == '')
        ).count()

    count = await sync_to_async(_count)()

    await message.answer(
        t("ai_category_stats_title", lang=user.language) + "\n\n" +
        t("ai_category_no_category_count", lang=user.language, count=count) + "\n\n" +
        t("ai_category_run_ai", lang=user.language)
    )
