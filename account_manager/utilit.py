import json
import random
import re
from typing import Optional


def normalize_telegram_link(input_link: str) -> Optional[str]:
    """
    Приводит ссылку или username к виду https://t.me/<username>.

    Поддерживает:
      - @username
      - username
      - t.me/username
      - https://t.me/username
      - https://telegram.dog/username

    Возвращает нормализованную ссылку или None.
    """
    if not isinstance(input_link, str) or not input_link:
        return None

    link = input_link.strip()

    if not link:
        return None

    username_pattern = r"[a-zA-Z][a-zA-Z0-9_]{4,31}"

    # @username
    match = re.fullmatch(rf"@({username_pattern})", link)
    if match:
        return f"https://t.me/{match.group(1)}"

    # username без @ и ссылки
    match = re.fullmatch(username_pattern, link)
    if match:
        return f"https://t.me/{match.group(0)}"

    # Ссылка на Telegram
    match = re.fullmatch(
        rf"(?:https?://)?(?:www\.)?(?:t\.me|telegram\.dog)/"
        rf"({username_pattern})/?",
        link,
        flags=re.IGNORECASE
    )

    if match:
        return f"https://t.me/{match.group(1)}"

    return None


def read_json(file_name):
    """Читаем json файл"""
    with open(file_name, "r") as f:
        return json.load(f)


def choosing_random_ai_model():
    """Выбираем рандомную модель AI из файла model.json"""
    data = read_json(file_name="data/model.json")
    models = data["model"]
    model = random.choice(models)
    return model

# def preliminary_verification_of_the_link(input_link: str) -> bool:
#     normalized = normalize_telegram_link(input_link)
#     if normalized:
#         print(f"Исходная: {input_link!r}")
#         print(f"Нормализованная: {normalized}")
#         print("Валидная ссылка")
#         return True
#     else:
#         print(f"Исходная: {input_link!r}")
#         print("Невалидная ссылка")
#         return False


# if __name__ == "__main__":
#     test_cases = [
#         "@https://t.me/promokod_skidki_tlt",
#         "@username",
#         "username",  # новый кейс: просто имя
#         "t.me/another_user",
#         "https://telegram.dog/user_xyz",
#         "not_a_link",  # теперь тоже невалидно, потому что не подходит под правила
#         "@",
#         "",
#         "  @valid_name  ",
#         "Some text with @my_channel and other stuff",  # будет невалидно: не вся строка — это ссылка
#         "https://t.me/test_bot",
#         "@user12345",
#         "user12345",  # валидный «голый» username
#         "t.me/short",
#         "https://t.me/a",
#     ]
#
#     for case in test_cases:
#         preliminary_verification_of_the_link(case)
#         print("-" * 40)
