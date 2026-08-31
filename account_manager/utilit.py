import re
from typing import Optional

MIN_USERNAME_LENGTH = 5
MAX_USERNAME_LENGTH = 64

# Формируем часть шаблона с длиной один раз, чтобы не дублировать
len_pattern = f"{{{MIN_USERNAME_LENGTH},{MAX_USERNAME_LENGTH}}}"


def normalize_telegram_link(input_link: str) -> Optional[str]:
    """
    Приводит ссылку/юзернейм к единому виду: https://t.me/<username>
    Поддерживает:
      - @username
      - username (без @ и без ссылки)
      - t.me/username
      - https://t.me/username
      - https://telegram.dog/username
    Возвращает:
      - Нормализованную ссылку https://t.me/<username>, если удалось извлечь username
      - None, если валидный username не найден
    """
    if not input_link or not isinstance(input_link, str):
        return None

    link = input_link.strip()
    if not link:
        return None

    # 1. Вариант: @username (строка целиком)
    match_at = re.fullmatch(rf'^@([a-zA-Z0-9_]{len_pattern})$', link)
    if match_at:
        return f"https://t.me/{match_at.group(1)}"

    # 2. Вариант: просто username (без @, без URL)
    # Важно: не должно быть в строке http/t.me и т.п., иначе это не «голый» юзернейм
    if not re.search(r'https?://|t\.me|telegram\.dog', link, flags=re.IGNORECASE):
        match_bare = re.fullmatch(rf'^([a-zA-Z0-9_]{len_pattern})$', link)
        if match_bare:
            return f"https://t.me/{match_bare.group(1)}"

    # 3. Вариант: URL (t.me или telegram.dog)
    match_url = re.search((
        rf'(?:https?://)?(?:t\.me|telegram\.dog)/'
        rf'([a-zA-Z0-9_]{len_pattern})'
        r'(?:[/?#].*)?$'
    ), link, flags=re.IGNORECASE)
    if match_url:
        return f"https://t.me/{match_url.group(1)}"

    return None

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
