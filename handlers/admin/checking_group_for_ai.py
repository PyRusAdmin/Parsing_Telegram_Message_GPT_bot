# handlers/admin/checking_group_for_ai.py
import asyncio
from concurrent.futures import ThreadPoolExecutor

from aiogram import F
from aiogram.types import Message
from asgiref.sync import sync_to_async
from loguru import logger

from ai.ai import category_assignment_sync  # ✅ Синхронная функция
from database.database import TelegramGroup, db
from system.dispatcher import router


async def get_groups_without_category(limit: int = 200) -> list[dict]:
    """Получает группы без категории (в отдельном потоке для БД)"""

    def _fetch():
        if db.is_closed():
            db.connect(reuse_if_open=True)

        groups = TelegramGroup.select().where(
            (TelegramGroup.username.is_null(False)) &
            (TelegramGroup.category == '')
        ).limit(limit)

        return [{
            "telegram_id": group.telegram_id,
            "name": group.name,
            "username": group.username,
            "description": group.description,
            "group_type": group.group_type,
        } for group in groups]

    try:
        return await sync_to_async(_fetch, thread_sensitive=True)()
    except Exception as e:
        logger.error(f"❌ Ошибка получения групп: {e}")
        return []


async def batch_update_categories(updates: list[dict]) -> tuple[int, int]:
    """Массовое обновление категорий в БД (в одном потоке, транзакцией)"""

    def _update():
        if db.is_closed():
            db.connect(reuse_if_open=True)

        updated = 0
        failed = 0

        try:
            with db.atomic():  # ✅ Одна транзакция для всех обновлений
                for item in updates:
                    try:
                        rows = (
                            TelegramGroup
                            .update(category=item['category'])
                            .where(TelegramGroup.telegram_id == item['telegram_id'])
                            .execute()
                        )
                        if rows > 0:
                            updated += 1
                            logger.debug(f"✅ Обновлено: {item.get('name')} → {item['category']}")
                        else:
                            failed += 1
                    except Exception as e:
                        failed += 1
                        logger.error(f"❌ Ошибка обновления {item.get('name')}: {e}")
            return updated, failed
        except Exception as e:
            logger.error(f"❌ Критическая ошибка транзакции: {e}")
            return 0, len(updates)

    return await sync_to_async(_update, thread_sensitive=True)()


@router.message(F.text == "🏷️ Присвоить категорию")
async def checking_group_for_ai_db(message: Message):
    """Присвоение категорий группам с параллельной обработкой (10 потоков)"""

    status_msg = await message.answer("🧠 Запуск присвоения категорий с помощью ИИ...")

    try:
        # 1️⃣ Получаем группы для обработки
        groups_to_process = await get_groups_without_category(limit=100)

        if not groups_to_process:
            await status_msg.edit_text("✅ Все группы уже имеют категории!")
            return

        total = len(groups_to_process)
        logger.info(f"📦 Найдено {total} групп для обработки")
        await status_msg.edit_text(f"🔄 Обрабатываю {total} групп в 10 потоков...")

        # 2️⃣ Запускаем AI-запросы параллельно в ThreadPoolExecutor
        loop = asyncio.get_event_loop()

        with ThreadPoolExecutor(max_workers=10) as executor:  # ✅ 10 параллельных запросов
            futures = [
                loop.run_in_executor(executor, category_assignment_sync, group_data)
                for group_data in groups_to_process
            ]
            results = await asyncio.gather(*futures, return_exceptions=True)

        # 3️⃣ Собираем успешные результаты
        successful_results = []
        ai_errors = 0

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"❌ Исключение в потоке: {result}")
                ai_errors += 1
                continue

            if result.get("success") and result.get("category"):
                successful_results.append({
                    "telegram_id": result["telegram_id"],
                    "category": result["category"],
                    "name": next((g["name"] for g in groups_to_process if g["telegram_id"] == result["telegram_id"]),
                                 "Unknown")
                })
            else:
                ai_errors += 1

        # 4️⃣ Обновляем БД одним батчем
        db_updated = 0
        db_errors = 0

        if successful_results:
            await message.answer(f"💾 Сохранение {len(successful_results)} результатов в БД...")
            db_updated, db_errors = await batch_update_categories(successful_results)

        # 5️⃣ Итоговая статистика
        total_errors = ai_errors + db_errors

        await status_msg.edit_text(
            f"✅ Обработка завершена!\n\n"
            f"📊 Статистика:\n"
            f"• Всего групп: {total}\n"
            f"• AI определил: {len(successful_results)}\n"
            f"• Сохранено в БД: {db_updated}\n"
            f"• Ошибок AI: {ai_errors}\n"
            f"• Ошибок БД: {db_errors}\n"
            f"• Всего ошибок: {total_errors}\n\n"
            f"💡 Запустите ещё раз для следующей партии."
        )

    except Exception as e:
        logger.exception(f"❌ Критическая ошибка: {e}")
        await status_msg.edit_text(f"❌ Ошибка: {e}")
    finally:
        if not db.is_closed():
            db.close()


def register_handlers_checking_group_for_ai():
    """Регистрирует обработчики"""
    router.message.register(checking_group_for_ai_db, F.text == "🏷️ Присвоить категорию")
