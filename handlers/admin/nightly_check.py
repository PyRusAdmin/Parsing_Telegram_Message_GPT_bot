import asyncio
import json
import os
from datetime import datetime
from typing import Optional

from loguru import logger

from account_manager.utilit import detect_language
from ai.ai import category_assignment
from core.config import ADMIN_USER_ID
from database.database import TelegramGroups
from system.dispatcher import bot

SETTINGS_PATH = "data/settings.json"

DEFAULT_SETTINGS = {
    "nightly_check_enabled": True,
    "nightly_check_time": "01:00",
    "batch_size": 150,
    "last_run_date": None,
    "last_report": None,
}


def get_nightly_check_settings() -> dict:
    """
    Получает настройки ночной проверки базы данных из data/settings.json.

    :return: (dict) Словарь с настройками планировщика.
    """
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULT_SETTINGS, **data}
        except Exception as e:
            logger.warning(f"⚠️ Ошибка чтения {SETTINGS_PATH}: {e}")
    return DEFAULT_SETTINGS.copy()


def save_nightly_check_settings(settings: dict) -> None:
    """
    Сохраняет настройки ночной проверки базы данных в data/settings.json.

    :param settings: (dict) Настройки для сохранения.
    """
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"❌ Не удалось сохранить настройки в {SETTINGS_PATH}: {e}")


def toggle_nightly_check() -> bool:
    """
    Переключает состояние автоматической ночной проверки базы данных (ВКЛ / ВЫКЛ).

    :return: (bool) Новое состояние активности (True — включена, False — выключена).
    """
    settings = get_nightly_check_settings()
    new_state = not settings.get("nightly_check_enabled", True)
    settings["nightly_check_enabled"] = new_state
    save_nightly_check_settings(settings)
    logger.info(f"⚙️ Ночная проверка базы данных: {'ВКЛЮЧЕНА' if new_state else 'ВЫКЛЮЧЕНА'}")
    return new_state


async def run_database_integrity_check(manual: bool = False) -> dict:
    """
    Выполняет фоновую актуализацию категорий и языков групп в TelegramGroups
    и отправляет отчёт администратору в Telegram.

    :param manual: (bool) Флаг ручного запуска из интерфейса администратора.
    :return: (dict) Итоговая статистика проверки.
    """
    settings = get_nightly_check_settings()
    batch_size = settings.get("batch_size", 150)

    logger.info(f"🚀 Запуск проверки базы данных групп (пакет: {batch_size})...")

    # Ищем записи без категории или без языка
    query = TelegramGroups.select().where(
        (TelegramGroups.category.is_null()) | (TelegramGroups.category == '') |
        (TelegramGroups.language.is_null()) | (TelegramGroups.language == '')
    ).order_by(TelegramGroups.id.asc()).limit(batch_size)

    records = list(query)
    processed = len(records)
    categories_assigned = 0
    languages_assigned = 0
    errors = 0

    for group in records:
        try:
            updated = False

            # 1. Проверяем и определяем язык, если отсутствует
            if not group.language:
                sample_text = f"{group.name or ''} {group.description or ''}".strip()
                if sample_text:
                    detected_lang = detect_language(sample_text)
                    if detected_lang:
                        group.language = detected_lang
                        languages_assigned += 1
                        updated = True

            # 2. Проверяем и присваиваем категорию через AI, если отсутствует
            if not group.category:
                group_data = {
                    "name": group.name,
                    "description": group.description,
                    "username": group.username,
                    "group_type": group.group_type,
                    "telegram_id": group.telegram_id,
                }
                cat_result = await category_assignment(group_data)
                if cat_result.get("success") and cat_result.get("category"):
                    cat_name = cat_result["category"].lower()
                    if cat_name and cat_name != "не определена":
                        group.category = cat_name
                        categories_assigned += 1
                        updated = True

                # Пауза для предотвращения превышения RPM/TPM лимитов AI API
                await asyncio.sleep(0.5)

            if updated:
                group.save()

        except Exception as e:
            errors += 1
            logger.warning(f"⚠️ Ошибка обработки группы ID={group.id}: {e}")

    # Подсчитываем текущие остатки по всей базе
    total_groups = TelegramGroups.select().count()
    remaining_no_cat = TelegramGroups.select().where(
        (TelegramGroups.category.is_null()) | (TelegramGroups.category == '')
    ).count()
    remaining_no_lang = TelegramGroups.select().where(
        (TelegramGroups.language.is_null()) | (TelegramGroups.language == '')
    ).count()

    current_time_str = datetime.now().strftime("%H:%M")
    header = (
        "🛠️ <b>Ручная проверка базы данных завершена</b>"
        if manual else
        f"🌙 <b>Ночная проверка базы данных завершена ({current_time_str})</b>"
    )

    report_text = (
        f"{header}\n\n"
        f"📊 <b>Результаты актуализации:</b>\n"
        f"• Обработано записей: <b>{processed}</b>\n"
        f"• Категорий присвоено: <b>{categories_assigned}</b>\n"
        f"• Языков определено: <b>{languages_assigned}</b>\n"
        f"• Ошибок / пропущено: <b>{errors}</b>\n\n"
        f"📈 <b>Текущее состояние базы данных:</b>\n"
        f"• Без категории: <b>{remaining_no_cat}</b>\n"
        f"• Без языка: <b>{remaining_no_lang}</b>\n"
        f"• Всего групп в базе: <b>{total_groups}</b>"
    )

    # Сохраняем дату последнего запуска и текст отчёта
    settings["last_run_date"] = datetime.now().strftime("%Y-%m-%d")
    settings["last_report"] = report_text
    save_nightly_check_settings(settings)

    # Оповещаем администратора через Telegram бота
    if ADMIN_USER_ID:
        try:
            await bot.send_message(
                chat_id=int(ADMIN_USER_ID),
                text=report_text,
                parse_mode="HTML"
            )
            logger.info("✅ Отчёт о проверке базы данных успешно отправлен администратору в Telegram.")
        except Exception as send_err:
            logger.warning(f"⚠️ Не удалось отправить отчёт администратору в Telegram: {send_err}")

    return {
        "processed": processed,
        "categories_assigned": categories_assigned,
        "languages_assigned": languages_assigned,
        "errors": errors,
        "remaining_no_cat": remaining_no_cat,
        "remaining_no_lang": remaining_no_lang,
        "total_groups": total_groups,
    }


async def nightly_scheduler_loop() -> None:
    """
    Фоновый асинхронный цикл планировщика.
    Проверяет время каждые 30 секунд. Если наступило время 01:00 ночи
    и проверка включена, запускает ночную проверку базы данных.
    """
    logger.info("⏰ Планировщик ночной проверки базы данных запущен.")
    while True:
        try:
            await asyncio.sleep(30)
            settings = get_nightly_check_settings()
            if not settings.get("nightly_check_enabled", True):
                continue

            target_time = settings.get("nightly_check_time", "01:00")
            now = datetime.now()
            current_hm = now.strftime("%H:%M")
            current_date = now.strftime("%Y-%m-%d")

            if current_hm == target_time and settings.get("last_run_date") != current_date:
                logger.info(f"🌙 [Scheduler] Время {current_hm}. Запуск запланированной ночной проверки...")
                await run_database_integrity_check(manual=False)

        except asyncio.CancelledError:
            logger.info("🛑 Планировщик ночной проверки остановлен.")
            break
        except Exception as e:
            logger.exception(f"❌ Ошибка в цикле планировщика: {e}")
            await asyncio.sleep(10)
