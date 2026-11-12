import json
import random
import re
from functools import cache
from typing import Optional


def normalize_telegram_link(input_link: str) -> Optional[str]:
    """
    Приводит ссылку или username к каноническому виду https://t.me/<username>.

    Поддерживает:
      - @username
      - username (bare)
      - t.me/username
      - https://t.me/username
      - https://telegram.dog/username
      - https://t.me/joinchat/<hash>   — приватная инвайт-ссылка (старый формат)
      - https://t.me/+<hash>           — приватная инвайт-ссылка (новый формат)

    :param input_link: (str) Исходная ссылка или username для нормализации.
    :return: (Optional[str]) Нормализованная ссылка в формате https://t.me/... или None, если формат не распознан.
    """
    if not isinstance(input_link, str) or not input_link:
        return None

    link = input_link.strip()

    if not link:
        return None

    username_pattern = r"[a-zA-Z][a-zA-Z0-9_]{4,31}"

    # ── @username ────────────────────────────────────────────────────────────
    match = re.fullmatch(rf"@({username_pattern})", link)
    if match:
        return f"https://t.me/{match.group(1)}"

    # ── bare username (без @ и протокола) ────────────────────────────────────
    match = re.fullmatch(username_pattern, link)
    if match:
        return f"https://t.me/{match.group(0)}"

    # ── Публичная ссылка t.me/username ───────────────────────────────────────
    match = re.fullmatch(
        rf"(?:https?://)?(?:www\.)?(?:t\.me|telegram\.dog)/"
        rf"({username_pattern})/?",
        link,
        flags=re.IGNORECASE,
    )
    if match:
        return f"https://t.me/{match.group(1)}"

    # ── Приватная инвайт-ссылка: t.me/joinchat/<hash> (старый формат) ───────
    match = re.fullmatch(
        r"(?:https?://)?(?:www\.)?(?:t\.me|telegram\.dog)/joinchat/([A-Za-z0-9_\-]+)/?",
        link,
        flags=re.IGNORECASE,
    )
    if match:
        return f"https://t.me/joinchat/{match.group(1)}"

    # ── Приватная инвайт-ссылка: t.me/+<hash> (новый формат) ────────────────
    match = re.fullmatch(
        r"(?:https?://)?(?:www\.)?(?:t\.me|telegram\.dog)/\+([A-Za-z0-9_\-]+)/?",
        link,
        flags=re.IGNORECASE,
    )
    if match:
        return f"https://t.me/+{match.group(1)}"

    # ── Голый хэш приватного инвайта (начинается с +) ────────────────────────
    match = re.fullmatch(r"\+([A-Za-z0-9_\-]{10,})", link)
    if match:
        return f"https://t.me/+{match.group(1)}"

    return None


def read_json(file_name):
    """
    Чтение данных из JSON файла.

    :param file_name: (str) Путь к файлу JSON.
    :return: (Any) Данные, распарсенные из JSON.
    """
    with open(file_name, "r", encoding="utf-8") as f:
        return json.load(f)


def choosing_random_ai_model():
    """
    Выбирает случайную модель AI из конфигурационного файла data/model.json.

    :return: (str) Название выбранной AI модели.
    """
    data = read_json(file_name="data/model.json")
    models = data["model"]
    model = random.choice(models)
    return model





@cache
def _get_language_detector():
    """
    Ленивая инициализация детектора языка (кэшируется в памяти).
    """
    from lingua import LanguageDetectorBuilder
    return LanguageDetectorBuilder.from_all_spoken_languages().build()


def detect_language(text: str) -> Optional[str]:
    """
    Ленивая детекция языка текста с помощью lingua-py.

    :param text: (str) Анализируемый текст.
    :return: (Optional[str]) Двухбуквенный ISO 639-1 код языка (например, 'ru', 'en') или None.
    """
    if not text or not isinstance(text, str) or not text.strip():
        return None

    try:
        detector = _get_language_detector()
        result = detector.detect_language_of(text.strip())
        if result is not None:
            code = result.iso_code_639_1.name.lower()
            from core.config import ISO_639_1_CODES
            if code in ISO_639_1_CODES:
                return code
    except Exception as e:
        from loguru import logger
        logger.warning(f"Ошибка при определении языка текста: {e}")

    return None


if __name__ == "__main__":
    choosing_random_ai_model()
