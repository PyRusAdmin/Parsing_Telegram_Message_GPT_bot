# -*- coding: utf-8 -*-
import configparser


def read_config_file():
    """
    Чтение данных из config.ini

    Функция считывает данные из файла конфигурации 'config.ini', который находится в директории 'user_data'.
    Файл конфигурации должен быть в кодировке 'utf-8'.

    :return: Объект ConfigParser, содержащий данные из файла конфигурации.
    """
    config = configparser.ConfigParser()
    config.read('data/config.ini', encoding='utf-8')
    return config


# Загружаем конфигурацию из файла
config = read_config_file()

# Параметры Telegram аккаунта
username = config['telegram_settings']['username']

# Ключ API для сервиса Groq (используется в AI-модели)
GROQ_API_KEY = config['API_Groq']['GROQ_API_KEY']

# Данные прокси-сервера для обхода блокировок
proxy_user = config['proxy_data']['user']
proxy_password = config['proxy_data']['password']
proxy_port = config['proxy_data']['port']
proxy_ip = config['proxy_data']['ip']

# Язык локализации интерфейса бота
language = config['localization']['language']

session_dir: str = 'accounts/parsing'  # Указываем путь к папкам с данными пользователей и их чатами
