# -*- coding: utf-8 -*-
import os

from dotenv import load_dotenv

# def read_config_file():
#     """
#     Чтение данных из config.ini
#
#     Функция считывает данные из файла конфигурации 'config.ini', который находится в директории 'user_data'.
#     Файл конфигурации должен быть в кодировке 'utf-8'.
#
#     :return: Объект ConfigParser, содержащий данные из файла конфигурации.
#     """
#     config = configparser.ConfigParser()
#     config.read('data/config.ini', encoding='utf-8')
#     return config


# Загружаем конфигурацию из файла
# config = read_config_file()

# Параметры Telegram аккаунта
# username = config['telegram_settings']['username']


# session_dir: str = 'accounts/parsing'  # Указываем путь к папкам с данными пользователей и их чатами
# Загружаем переменные окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
api_id = os.getenv("ID")
api_hash = os.getenv("HASH")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# OPENROUTER_API_KEY = config['OPENROUTER_API_KEY']['OPENROUTER_API_KEY']
# Ключ API для сервиса Groq (используется в AI-модели)
# GROQ_API_KEY = config['API_Groq']['GROQ_API_KEY']
GROQ_API_KEY = os.getenv("groq_api_key")

# Данные прокси-сервера для обхода блокировок
# proxy_user = config['proxy_data']['user']
# proxy_password = config['proxy_data']['password']
# proxy_port = config['proxy_data']['port']
# proxy_ip = config['proxy_data']['ip']

# Язык локализации интерфейса бота
# language = config['localization']['language']

proxy_user = os.getenv("user")
proxy_password = os.getenv("password")
proxy_port = os.getenv("port")
proxy_ip = os.getenv("ip")

language = os.getenv("language")
