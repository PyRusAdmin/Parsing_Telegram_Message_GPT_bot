# -*- coding: utf-8 -*-
import asyncio

from aiogram import F
from aiogram.types import Message
from loguru import logger  # https://github.com/Delgan/loguru

from database.database import TelegramGroup, db
from system.dispatcher import router


@router.message(F.text == "🏷️ Присвоить категорию")
async def checking_group_for_ai_db(message: Message):
    """Обработка групп в 10 параллельных задач"""

    status_msg = await message.answer("🧠 Запуск присвоения категорий с помощью ИИ...")

    try:
        if db.is_closed():
            db.connect()

        # Получаем группы без категории (ограничиваем батч для стабильности)
        groups_to_update = list(TelegramGroup.select().where(
            (TelegramGroup.username.is_null(False)) &
            (TelegramGroup.category == '')
        ).limit(200))  # ✅ Не более 200 за один запуск

        total_count = len(groups_to_update)
        if total_count == 0:
            await status_msg.edit_text("✅ Все группы уже имеют категории!")
            return

        logger.info(f"📦 Найдено {total_count} групп для обработки")
        await status_msg.edit_text(f"🔄 Обрабатываю {total_count} групп в 10 потоков...")

        # 🎯 Семафор: максимум 10 одновременных запросов к API
        semaphore = asyncio.Semaphore(10)

        # 📊 Счётчики (защищены asyncio.Lock для потокобезопасности)
        counters = {"processed": 0, "updated": 0, "errors": 0}
        lock = asyncio.Lock()

        # 🔄 Создаём задачи для всех групп
        tasks = [
            process_group_async(group, semaphore, counters, lock)
            for group in groups_to_update
        ]

        # 🚀 Запускаем все задачи параллельно
        await asyncio.gather(*tasks, return_exceptions=True)

        # 📋 Финальный отчёт
        await status_msg.edit_text(
            f"✅ Обработка завершена!\n\n"
            f"📊 Всего: {counters['processed']}/{total_count}\n"
            f"✅ Присвоено: {counters['updated']}\n"
            f"❌ Ошибок: {counters['errors']}\n\n"
            f"💡 Запустите ещё раз для следующей партии."
        )

    except Exception as e:
        logger.exception(f"❌ Критическая ошибка: {e}")
        await status_msg.edit_text(f"❌ Ошибка: {e}")
    finally:
        if not db.is_closed():
            db.close()


async def process_group_async(group, semaphore: asyncio.Semaphore, counters: dict, lock: asyncio.Lock):
    """
    Обрабатывает одну группу: получает категорию и обновляет БД.
    Вызывается внутри asyncio.gather().
    """
    from ai.ai import category_assignment_openrouter  # Локальный импорт для избежания циклов

    try:
        # 🧩 Собираем контекст
        context = (
            f"Название: {group.name or 'Без названия'}\n"
            f"Описание: {group.description or 'Без описания'}\n"
            f"Username: @{group.username}\n"
            f"Тип: {group.group_type or 'Неизвестен'}"
        )

        # 🤖 Получаем категорию (с семафором внутри)
        category = await category_assignment_openrouter(context, semaphore)
        category = category.strip().strip('".')

        # 💾 Обновляем БД (только если категория валидна)
        if category and category.lower() not in ["не определена", "undefined", ""]:
            TelegramGroup.update(category=category).where(
                TelegramGroup.telegram_id == group.telegram_id
            ).execute()
            success = True
        else:
            success = False

        # 🔒 Безопасное обновление счётчиков
        async with lock:
            counters["processed"] += 1
            if success:
                counters["updated"] += 1
            else:
                counters["errors"] += 1

            # 📈 Прогресс каждые 20 обработанных
            if counters["processed"] % 20 == 0:
                logger.info(f"📊 Прогресс: {counters['processed']}/{counters['total'] if 'total' in counters else '?'}")

        logger.debug(f"✅ {group.username}: {category if success else 'пропущено'}")

    except Exception as e:
        logger.exception(f"❌ Ошибка {group.username}: {e}")
        async with lock:
            counters["processed"] += 1
            counters["errors"] += 1


def register_handlers_checking_group_for_ai():
    """Регистрирует обработчики для проверки группы на наличие ключевых слов."""
    router.message.register(checking_group_for_ai_db, F.text == "🏷️ Присвоить категорию")
