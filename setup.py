# -*- coding: utf-8 -*-
import os

os.system("""pip install -r requirements.txt""")

# Создание .env файла, если он не существует
env_example = """
BOT_TOKEN=_____
ID=_____
HASH=_____
GROQ_API_KEY=_____
OPENROUTER_API_KEY=_____
USER=_____
PASSWORD=_____
IP=_____
PORT=_____
LANGUAGE=ru
""".strip()

env_file = ".env"

if not os.path.exists(env_file):
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(env_example)
    print(f"✅ Файл '{env_file}' успешно создан.")
else:
    print(f"ℹ️ Файл '{env_file}' уже существует.")
