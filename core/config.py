import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
API_ID = os.getenv("ID")
API_HASH = os.getenv("HASH")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")
PROXY_PORT = os.getenv("PROXY_PORT")
PROXY_IP = os.getenv("PROXY_IP")


class AdminId(int):
    """
    Класс-обёртка для ID администратора:
    - Ведёт себя как int (проходит валидацию Pydantic для chat_id в aiogram)
    - Поддерживает оператор in: user_id in ADMIN_USER_ID
    - Итерируем: for admin_id in ADMIN_USER_ID
    """

    def __new__(cls, val, all_ids=None):
        instance = super().__new__(cls, val)
        instance._ids = set(all_ids) if all_ids else {int(val)}
        return instance

    def __contains__(self, item):
        try:
            return int(item) in self._ids
        except (ValueError, TypeError):
            return False

    def __iter__(self):
        return iter(self._ids)

    def __len__(self):
        return len(self._ids)


_raw_admin_id = os.getenv("ADMIN_USER_ID", "0").strip()
_admin_ids = [int(x.strip()) for x in _raw_admin_id.split(",") if x.strip().isdigit()]
ADMIN_USER_ID = AdminId(_admin_ids[0] if _admin_ids else 0, _admin_ids)

MIN_USERNAME_LENGTH = 5  # Минимальная длина username
MAX_USERNAME_LENGTH = 64  # Максимальная длина username

# Формируем часть шаблона с длиной один раз, чтобы не дублировать
len_pattern = f"{{{MIN_USERNAME_LENGTH},{MAX_USERNAME_LENGTH}}}"

mobile_device = {
    "device_model": "Pixel 5",
    "system_version": "11",
    "app_version": "8.4.1",
    "lang_code": "en",
    "system_lang_code": "en-US",
}

# 🧠 Простейший трекер сообщений (в памяти)
forwarded_messages = set()

# 🛑 Словарь активных клиентов и флагов остановки
active_clients = {}  # {user_id: client}
stop_flags = {}  # {user_id: asyncio.Event}

MAX_SESSIONS_PER_BATCH = 10  # Максимум файлов за одну сессию

"""
Коды ISO 639-1 для языков
"""

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

version = "0.1.0"
