import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from aiogram import F, Router
from asgiref.sync import sync_to_async
from loguru import logger
from openai import OpenAI

from database.database import TelegramGroup, db, User
from locales.locales import t

router = Router(name=__name__)

from core.config import OPENROUTER_API_KEY


def ai_llama_fri(group_data: dict):
    """Определение языка (ТОЛЬКО AI-запрос через OpenRouter Free, БЕЗ записи в БД)"""
    try:
        # from openai import OpenAI
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
            timeout=15
        )

        data_parts = []
        if group_data.get('name'):
            data_parts.append(f"Название: {group_data['name']}")
        if group_data.get('username'):
            data_parts.append(f"Username: @{group_data['username']}")
        if group_data.get('description'):
            data_parts.append(f"Описание: {group_data['description']}")

        user_input = "\n".join(data_parts) if data_parts else "Нет данных"

        prompt = (
            "Определи основной язык текста или описания сообщества.\n"
            "Ответь СТРОГО одним словом — кодом языка в формате ISO 639-1 (двухбуквенный код).\n"
            "Примеры корректных ответов: ru, en, es, zh, ar, hi, ja, ko, fr, de, pt, it, nl, sv, pl, tr, vi, th, id, fa, he, uk, cs, el, ro, hu, fi, da, no, sk, bg, hr, sr, sl, et, lv, lt, mk, sq, mt, cy, eu, gl, ga, is, ms, sw, tl, ur, bn, ta, te, mr, gu, kn, ml, si, km, lo, my, am, hy, ka, az, uz, kk, ky, tg, tk, mn, ps, ku, sd, ne, si, lo, km, my, dz, bo, ug, yi, ha, yo, ig, zu, xh, st, tn, ts, ve, nr, ss, ch, rw, rn, mg, ln, kg, sw, tn.\n"
            "Если язык невозможно определить однозначно или текст содержит смесь языков без доминирующего — ответь: unknown.\n"
            "НЕ добавляй никаких пояснений, пунктуации, пробелов или дополнительного текста. Только код языка или 'unknown'.\n\n"
            f"Текст для анализа:\n{user_input}"
        )

        completion = client.chat.completions.create(
            model="google/gemma-3n-e4b-it",  # Бесплатная модель OpenRouter
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=10
        )

        detected_lang = (
            completion.choices[0].message.content
            .strip()
            .lower()
            .split()[0]
        )

        ISO_639_1_CODES = {
            "aa", "ab", "ae", "af", "ak", "am", "an", "ar", "as", "av", "ay", "az", "ba", "be", "bg", "bh", "bi",
            "bm", "bn", "bo", "br", "bs", "ca", "ce", "ch", "co", "cr", "cs", "cu", "cv", "cy", "da", "de", "dv",
            "dz", "ee", "el", "en", "eo", "es", "et", "eu", "fa", "ff", "fi", "fj", "fo", "fr", "fy", "ga", "gd",
            "gl", "gn", "gu", "gv", "ha", "he", "hi", "ho", "hr", "ht", "hu", "hy", "hz", "ia", "id", "ie", "ig",
            "ii", "ik", "io", "is", "it", "iu", "ja", "jv", "ka", "kg", "ki", "kj", "kk", "kl", "km", "kn", "ko",
            "kr", "ks", "ku", "kv", "kw", "ky", "la", "lb", "lg", "li", "ln", "lo", "lt", "lu", "lv", "mg", "mh",
            "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", "na", "nb", "nd", "ne", "ng", "nl", "nn", "no", "nr",
            "nv", "ny", "oc", "oj", "om", "or", "os", "pa", "pi", "pl", "ps", "pt", "qu", "rm", "rn", "ro", "ru",
            "rw", "sa", "sc", "sd", "se", "sg", "si", "sk", "sl", "sm", "sn", "so", "sq", "sr", "ss", "st", "su",
            "sv", "sw", "ta", "te", "tg", "th", "ti", "tk", "tl", "tn", "to", "tr", "ts", "tt", "tw", "ty", "ug",
            "uk", "ur", "uz", "ve", "vi", "vo", "wa", "wo", "xh", "yi", "yo", "za", "zh", "zu"
        }

        if detected_lang not in ISO_639_1_CODES:
            detected_lang = "unknown"

        logger.debug(f"✅ AI определил: '{group_data.get('name')}' -> {detected_lang}")

        return {
            "group_hash": group_data["group_hash"],
            "name": group_data.get("name"),
            "language": detected_lang,
            "success": True
        }

    except Exception as e:
        logger.error(f"❌ Ошибка AI для {group_data.get('name')}: {e}")
        return {
            "group_hash": group_data["group_hash"],
            "name": group_data.get("name"),
            "language": None,
            "success": False,
            "error": str(e)
        }


def ai_llama(group_data: dict) -> dict:
    """Определение языка (ТОЛЬКО AI-запрос, БЕЗ записи в БД)"""
    api_key = os.getenv("POLZA_AI_API_KEY")
    try:
        client = OpenAI(
            base_url="https://api.polza.ai/api/v1",
            api_key=api_key,
        )

        data_parts = []
        if group_data.get('name'):
            data_parts.append(f"Название: {group_data['name']}")
        if group_data.get('username'):
            data_parts.append(f"Username: @{group_data['username']}")
        if group_data.get('description'):
            data_parts.append(f"Описание: {group_data['description']}")

        user_input = "\n".join(data_parts) if data_parts else "Нет данных"

        prompt = (
            "Определи основной язык текста или описания сообщества.\n"
            "Ответь СТРОГО одним словом — кодом языка в формате ISO 639-1 (двухбуквенный код).\n"
            "Примеры корректных ответов: ru, en, es, zh, ar, hi, ja, ko, fr, de, pt, it, nl, sv, pl, tr, vi, th, id, fa, he, uk, cs, el, ro, hu, fi, da, no, sk, bg, hr, sr, sl, et, lv, lt, mk, sq, mt, cy, eu, gl, ga, is, ms, sw, tl, ur, bn, ta, te, mr, gu, kn, ml, si, km, lo, my, am, hy, ka, az, uz, kk, ky, tg, tk, mn, ps, ku, sd, ne, si, lo, km, my, dz, bo, ug, yi, ha, yo, ig, zu, xh, st, tn, ts, ve, nr, ss, ch, rw, rn, mg, ln, kg, sw, tn.\n"
            "Если язык невозможно определить однозначно или текст содержит смесь языков без доминирующего — ответь: unknown.\n"
            "НЕ добавляй никаких пояснений, пунктуации, пробелов или дополнительного текста. Только код языка или 'unknown'.\n\n"
            f"Текст для анализа:\n{user_input}"
        )

        completion = client.chat.completions.create(
            model="google/gemma-3-12b:free",  # Бесплатная модель OpenRouter для определения языка
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=10
        )

        detected_lang = (
            completion.choices[0].message.content
            .strip()
            .lower()
            .split()[0]
        )

        ISO_639_1_CODES = {
            "aa", "ab", "ae", "af", "ak", "am", "an", "ar", "as", "av", "ay", "az", "ba", "be", "bg", "bh", "bi",
            "bm", "bn", "bo", "br", "bs", "ca", "ce", "ch", "co", "cr", "cs", "cu", "cv", "cy", "da", "de", "dv",
            "dz", "ee", "el", "en", "eo", "es", "et", "eu", "fa", "ff", "fi", "fj", "fo", "fr", "fy", "ga", "gd",
            "gl", "gn", "gu", "gv", "ha", "he", "hi", "ho", "hr", "ht", "hu", "hy", "hz", "ia", "id", "ie", "ig",
            "ii", "ik", "io", "is", "it", "iu", "ja", "jv", "ka", "kg", "ki", "kj", "kk", "kl", "km", "kn", "ko",
            "kr", "ks", "ku", "kv", "kw", "ky", "la", "lb", "lg", "li", "ln", "lo", "lt", "lu", "lv", "mg", "mh",
            "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", "na", "nb", "nd", "ne", "ng", "nl", "nn", "no", "nr",
            "nv", "ny", "oc", "oj", "om", "or", "os", "pa", "pi", "pl", "ps", "pt", "qu", "rm", "rn", "ro", "ru",
            "rw", "sa", "sc", "sd", "se", "sg", "si", "sk", "sl", "sm", "sn", "so", "sq", "sr", "ss", "st", "su",
            "sv", "sw", "ta", "te", "tg", "th", "ti", "tk", "tl", "tn", "to", "tr", "ts", "tt", "tw", "ty", "ug",
            "uk", "ur", "uz", "ve", "vi", "vo", "wa", "wo", "xh", "yi", "yo", "za", "zh", "zu"
        }

        if detected_lang not in ISO_639_1_CODES:
            detected_lang = "unknown"

        logger.debug(f"✅ AI определил: '{group_data.get('name')}' -> {detected_lang}")

        return {
            "group_hash": group_data["group_hash"],
            "name": group_data.get("name"),
            "language": detected_lang,
            "success": True
        }

    except Exception as e:
        logger.error(f"❌ Ошибка AI для {group_data.get('name')}: {e}")
        return {
            "group_hash": group_data["group_hash"],
            "name": group_data.get("name"),
            "language": None,
            "success": False,
            "error": str(e)
        }


async def get_groups_without_language() -> list[dict]:
    """Получить ВСЕ группы, но отфильтровать те, где язык не определён"""

    def _get_groups():
        if db.is_closed():
            db.connect(reuse_if_open=True)

        # Берём ВСЕ записи
        groups = TelegramGroup.select()

        # Фильтруем только те, где language пустой
        return [{
            "group_hash": group.group_hash,
            "name": group.name,
            "username": group.username,
            "description": group.description,
        } for group in groups if not group.language or group.language.strip() == '']

    try:
        groups_data = await sync_to_async(_get_groups)()
        logger.info(f"📊 Найдено {len(groups_data)} групп без языка")
        return groups_data
    except Exception as e:
        logger.error(f"❌ Ошибка получения групп: {e}")
        return []


async def batch_update_languages(updates: list[dict]) -> tuple[int, int]:
    """Массовое обновление языков в БД (в основном потоке)"""

    def _batch_update():
        if db.is_closed():
            db.connect(reuse_if_open=True)

        updated = 0
        failed = 0

        try:
            with db.atomic():  # Одна транзакция для всех обновлений
                for item in updates:
                    try:
                        rows = (
                            TelegramGroup
                            .update(language=item['language'])
                            .where(TelegramGroup.group_hash == item['group_hash'])
                            .execute()
                        )

                        if rows > 0:
                            updated += 1
                            logger.debug(f"✅ Обновлено: {item['name']} -> {item['language']}")
                        else:
                            failed += 1
                            logger.warning(f"⚠️ Группа не найдена: {item['group_hash']}")

                    except Exception as e:
                        failed += 1
                        logger.error(f"❌ Ошибка обновления {item['name']}: {e}")

            return updated, failed

        except Exception as e:
            logger.error(f"❌ Критическая ошибка транзакции: {e}")
            return 0, len(updates)

    return await sync_to_async(_batch_update, thread_sensitive=True)()


@router.message(F.text == "🌐 Присвоить язык")
async def language_detection(message):
    """Присвоение языка группам"""
    user = User.get(User.user_id == message.from_user.id)

    # 1️⃣ Получаем группы для обработки
    groups_to_process = await get_groups_without_language()
    if not groups_to_process:
        await message.answer(t("lang_detect_no_groups", lang=user.language))
        return

    total = len(groups_to_process)
    await message.answer(t("lang_detect_starting", lang=user.language, total=total))

    # 2️⃣ Определяем языки параллельно (ТОЛЬКО AI, БЕЗ БД)
    loop = asyncio.get_event_loop()

    try:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                loop.run_in_executor(executor, ai_llama_fri, group_data)
                for group_data in groups_to_process
            ]
            results = await asyncio.gather(*futures, return_exceptions=True)

    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        await message.answer(t("lang_detect_error", lang=user.language, error=str(e)))
        return

    # 3️⃣ Собираем успешные результаты для обновления
    successful_results = []
    ai_failed = 0

    for result in results:
        if isinstance(result, Exception):
            logger.error(f"❌ Исключение: {result}")
            ai_failed += 1
            continue

        if result.get("success") and result.get("language"):
            successful_results.append({
                "group_hash": result["group_hash"],
                "name": result["name"],
                "language": result["language"]
            })
        else:
            ai_failed += 1

    # 4️⃣ Обновляем БД одним батчем (в основном потоке)
    if successful_results:
        await message.answer(t("lang_detect_saving", lang=user.language, count=len(successful_results)))
        updated, db_failed = await batch_update_languages(successful_results)
    else:
        updated = 0
        db_failed = 0

    # 5️⃣ Итоговая статистика
    total_failed = ai_failed + db_failed

    await message.answer(
        t("lang_detect_complete", lang=user.language) + "\n\n"
                                                        f"📊 {t('lang_detect_stats_title', lang=user.language)}:\n"
                                                        f"• {t('lang_detect_stats_total', lang=user.language)}: {total}\n"
                                                        f"• {t('lang_detect_stats_ai_success', lang=user.language)}: {len(successful_results)}\n"
                                                        f"• {t('lang_detect_stats_db_success', lang=user.language)}: {updated}\n"
                                                        f"• {t('lang_detect_stats_ai_fail', lang=user.language)}: {ai_failed}\n"
                                                        f"• {t('lang_detect_stats_db_fail', lang=user.language)}: {db_failed}\n"
                                                        f"• {t('lang_detect_stats_total_fail', lang=user.language)}: {total_failed}"
    )
