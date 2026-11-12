import os
import sys

# Создание .env файла, если он не существует
env_example = """
BOT_TOKEN=_____
ID=_____
HASH=_____
ADMIN_USER_ID=0
GROQ_API_KEY=_____
OPENROUTER_API_KEY=_____
POLZA_AI_API_KEY=_____
USER=_____
PASSWORD=_____
IP=_____
PORT=3000
LANGUAGE=ru
PROXY_USER=_____
PROXY_PASSWORD=_____
PROXY_PORT=_____
PROXY_IP=_____
MT_PROXY_IP=103.59.42.72
MT_PROXY_PORT=443
MT_PROXY_SECRET=_____
""".strip()

env_file = ".env"


def main():
    os.system(f'"{sys.executable}" -m pip install -r requirements.txt')

    if not os.path.exists(env_file):
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_example)
        print(f"[OK] Файл '{env_file}' успешно создан.")
    else:
        print(f"[INFO] Файл '{env_file}' уже существует.")


if __name__ == "__main__":
    main()
