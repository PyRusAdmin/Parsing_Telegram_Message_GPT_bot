# -*- coding: utf-8 -*-
import asyncio

from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from asgiref.sync import sync_to_async
from g4f.client import Client  # https://github.com/xtekky/gpt4free
from groq import AsyncGroq
from loguru import logger  # https://loguru.readthedocs.io/en/stable/overview.html
from openai import AsyncOpenAI

from ai.ai import category_assignment
from core.config import GROQ_API_KEY
from core.config import OPENROUTER_API_KEY
from database.database import TelegramGroup, db, get_groups_without_category
from keyboards.admin.keyboards import category_method_keyboard, admin_keyboard
from states.states import CategoryMethod
from system.dispatcher import router


@router.message(F.text == "🏷️ Присвоить категорию")
async def checking_group_for_ai_db(message: Message, state: FSMContext):
    """Предлагает выбор метода присвоения категорий"""
    await state.set_state(CategoryMethod.waiting_for_method)

    await message.answer(
        "🤖 <b>Выберите метод присвоения категорий:</b>\n\n"
        "⚡️ <b>Быстро (g4f.free)</b>\n"
        "• Бесплатно, без API ключей\n"
        "• Последовательная обработка (медленнее)\n"
        "• Подходит для небольших объёмов\n"
        "• Может возвращать неточные результаты\n\n"
        "🚀 <b>Мощно (Groq API)</b>\n"
        "• Требует API ключ Groq\n"
        "• Параллельная обработка в 10 потоков (быстрее)\n"
        "• Подходит для больших объёмов\n"
        "• Более точные результаты\n\n"
        "Выберите метод:",
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

    if message.text == "Назад":
        await state.clear()
        await message.answer(
            "↩️ Возврат в панель администратора",
            reply_markup=admin_keyboard()
        )
        return

    if message.text == "⚡️ Быстро (g4f.free)":
        await state.clear()
        client = Client()

        # 🔍 Определяем лучшую доступную модель
        status_msg = await message.answer("🔍 Проверка доступных моделей...")
        model = await get_best_g4f_model(client)
        await status_msg.edit_text(f"✅ Выбрана модель: {model}")
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
        model = "meta-llama/llama-3.2-3b-instruct"
        await assign_categories(message, client, model)
    elif message.text == "🚀 Мощно (GROQ API)":
        await state.clear()
        client = AsyncGroq(api_key=GROQ_API_KEY)
        model = "llama-3.1-8b-instant"
        await assign_categories(message, client, model)
    else:
        await message.answer(
            "Пожалуйста, выберите метод из клавиатуры ниже:",
            reply_markup=category_method_keyboard()
        )


async def assign_categories(message: Message, client, model):
    """Универсальная функция присвоения категорий (любой AI клиент)"""

    status_msg = await message.answer("🤖 Запуск AI...")

    try:
        # 1️⃣ Получаем группы для обработки
        groups_to_process = await get_groups_without_category()

        if not groups_to_process:
            await status_msg.edit_text("✅ Все группы уже имеют категории!")
            return

        total = len(groups_to_process)
        logger.info(f"📦 Найдено {total} групп для обработки")

        await status_msg.edit_text(f"🔄 Обрабатываю {total} групп...")

        # 2️⃣ Обрабатываем последовательно с немедленной записью в БД
        for i, group_data in enumerate(groups_to_process, 1):
            try:
                # AI запрос
                result = await category_assignment(group_data, client, model)

                if result.get("success") and result.get("category"):
                    # ✅ Сразу пишем в БД
                    await sync_to_async(lambda: TelegramGroup.update(category=result["category"])
                                        .where(TelegramGroup.telegram_id == result["telegram_id"])
                                        .execute(), thread_sensitive=True)()
                    logger.info(f"[{i}/{total}] ✅ {group_data['name']} → {result['category']}")
                else:
                    logger.warning(f"[{i}/{total}] ❌ {group_data['name']} — AI не определил")

                # Пауза только для g4f (чтобы не блокировали)
                if type(client).__name__ == 'Client':  # g4f клиент
                    await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"❌ Ошибка {group_data.get('name')}: {e}")
                continue

        # 3️⃣ Финал
        await status_msg.edit_text("✅ <b>Готово!</b>", parse_mode="HTML")

    except Exception as e:
        logger.exception(e)
        await status_msg.edit_text(f"❌ Ошибка: {e}")


@router.message(F.text == "📥 Получить группы без категории")
async def get_groups_without_category_message(message: Message):
    """Информация о группах без категории"""

    def _count():
        if db.is_closed():
            db.connect(reuse_if_open=True)
        return TelegramGroup.select().where(
            (TelegramGroup.username.is_null(False)) &
            (TelegramGroup.category == '')
        ).count()

    count = await sync_to_async(_count)()

    await message.answer(
        f"📊 <b>Статистика категорий:</b>\n\n"
        f"🗃️ Групп без категории: {count}\n\n"
        "Нажмите '🏷️ Присвоить категорию' для запуска AI"
    )


def register_handlers_checking_group_for_ai():
    """Регистрация обработчиков для присвоения категорий"""
    pass  # Обработчики регистрируются через router автоматически
