import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = os.getenv("ID")
API_HASH = os.getenv("HASH")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")
PROXY_PORT = os.getenv("PROXY_PORT")
PROXY_IP = os.getenv("PROXY_IP")

ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID"))  # ID администратора Telegram

MIN_USERNAME_LENGTH = 5  # Минимальная длина username
MAX_USERNAME_LENGTH = 64  # Максимальная длина username

# Формируем часть шаблона с длиной один раз, чтобы не дублировать
len_pattern = f"{{{MIN_USERNAME_LENGTH},{MAX_USERNAME_LENGTH}}}"
