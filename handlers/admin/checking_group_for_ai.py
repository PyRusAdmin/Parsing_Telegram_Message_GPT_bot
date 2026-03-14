# -*- coding: utf-8 -*-
import asyncio

from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from asgiref.sync import sync_to_async
from loguru import logger

from ai.ai import category_assignment_sync, category_assignment_free
from database.database import TelegramGroup, db, get_groups_without_category
from keyboards.admin.keyboards import category_method_keyboard, admin_keyboard
from states.states import CategoryMethod
from system.dispatcher import router


async def batch_update_categories(updates: list[dict]):
    """Массовое обновление категорий в БД (в одном потоке, транзакцией)"""

    def _update():
        if db.is_closed():
            db.connect(reuse_if_open=True)

        try:
            with db.atomic():  # ✅ Одна транзакция для всех обновлений
                for item in updates:
                    try:
                        TelegramGroup.update(category=item['category']).where(
                            TelegramGroup.telegram_id == item['telegram_id']).execute()
                        logger.debug(f"✅ Обновлено: {item.get('name')} → {item['category']}")
                    except Exception as e:
                        logger.exception(f"❌ Ошибка обновления {item.get('name')}: {e}")

        except Exception as e:
            logger.exception(f"❌ Критическая ошибка транзакции: {e}")

    return await sync_to_async(_update, thread_sensitive=True)()


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
        await assign_categories_free(message)
    elif message.text == "🚀 Мощно (Openrouter API)":
        await state.clear()
        await assign_categories_groq(message)
    else:
        await message.answer(
            "Пожалуйста, выберите метод из клавиатуры ниже:",
            reply_markup=category_method_keyboard()
        )


async def assign_categories_free(message: Message):
    """Присвоение категорий через g4f (бесплатно, последовательно)"""

    status_msg = await message.answer("⚡️ Запуск бесплатного AI (g4f)...")

    try:
        # 1️⃣ Получаем группы для обработки (без категорий)
        groups_to_process = await get_groups_without_category()

        if not groups_to_process:
            await status_msg.edit_text("✅ Все группы уже имеют категории!")
            return

        total = len(groups_to_process)
        logger.info(f"📦 Найдено {total} групп для обработки (g4f.free)")

        await status_msg.edit_text(
            f"🔄 Обрабатываю {total} групп (последовательно)...\n"
        )

        # 2️⃣ Обрабатываем последовательно
        for group_data in groups_to_process:
            try:
                # AI запрос
                result = await category_assignment_free(group_data)

                if result.get("success") and result.get("category"):
                    # Обновляем БД
                    (TelegramGroup
                     .update(category=result["category"])
                     .where(TelegramGroup.telegram_id == result["telegram_id"])
                     .execute())
                    # successful += 1
                    logger.debug(f"✅ Обновлено: {group_data.get('name')} → {result['category']}")
                # else:
                #     failed += 1
                #     logger.debug(f"⚪ Не удалось определить категорию: {group_data.get('name')}")

                # processed += 1

                # Прогресс каждые 10 групп
                # if processed % 10 == 0:
                #     await status_msg.edit_text(
                #         f"🔄 Прогресс: {processed}/{total}\n"
                #         f"✅ Успешно: {successful}\n"
                #         f"⚪ Не определено: {failed}"
                #     )

                # Пауза между запросами (чтобы не блокировали)
                await asyncio.sleep(0.5)

            except Exception as e:
                # failed += 1
                logger.error(f"❌ Ошибка обработки {group_data.get('name')}: {e}")
                continue

        # Финальный отчёт
        await status_msg.edit_text(
            f"✅ <b>Готово!</b>\n\n"
            # f"📊 Всего обработано: {total}\n"
            # f"✅ Успешно: {successful}\n"
            # f"⚪ Не определено: {failed}\n\n"
            f"🤖 Метод: g4f.free (бесплатный)",
            parse_mode="HTML"
        )

    except Exception as e:
        logger.exception(e)
        await status_msg.edit_text(f"❌ Ошибка: {e}")


async def assign_categories_groq(message: Message):
    """Присвоение категорий через Groq API (потоки, быстро)"""

    status_msg = await message.answer("🚀 Запуск мощного AI (Groq API)...")

    try:
        # 1️⃣ Получаем группы для обработки
        groups_to_process = await get_groups_without_category()

        if not groups_to_process:
            await status_msg.edit_text("✅ Все группы уже имеют категории!")
            return

        total = len(groups_to_process)
        logger.info(f"📦 Найдено {total} групп для обработки (Groq API)")

        await status_msg.edit_text(
            f"🔄 Обрабатываю {total} групп (последовательно)...\n"
        )

        # 2️⃣ Запускаем AI-запросы
        # successful_results = []
        for group_data in groups_to_process:
            try:
                result = category_assignment_sync(group_data)
                # if result.get("success") and result.get("category"):
                #     successful_results.append({
                #         "telegram_id": result["telegram_id"],
                #         "category": result["category"],
                #         "name": next((g["name"] for g in groups_to_process if g["telegram_id"] == result["telegram_id"]),
                #                      "Unknown")
                #     })
                if result.get("success") and result.get("category"):
                    # Обновляем БД
                    (TelegramGroup
                     .update(category=result["category"])
                     .where(TelegramGroup.telegram_id == result["telegram_id"])
                     .execute())
                    # successful += 1
                    logger.debug(f"✅ Обновлено: {group_data.get('name')} → {result['category']}")

                await asyncio.sleep(0.5)

            except Exception as e:
                # failed += 1
                logger.error(f"❌ Ошибка обработки {group_data.get('name')}: {e}")
                continue

        # 3️⃣ Обновляем БД одним батчем
        # if successful_results:
        #     await batch_update_categories(successful_results)

        # 5️⃣ Финальный отчёт
        # await status_msg.edit_text(
        #     f"✅ <b>Готово!</b>\n\n"
        #     f"🚀 Метод: Openrouter API",
        #     parse_mode='HTML'
        # )
        await status_msg.edit_text(
            f"✅ <b>Готово!</b>\n\n"
            # f"📊 Всего обработано: {total}\n"
            # f"✅ Успешно: {successful}\n"
            # f"⚪ Не определено: {failed}\n\n"
            f"🤖 Метод: OPENROUTER",
            parse_mode='HTML'
        )

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
