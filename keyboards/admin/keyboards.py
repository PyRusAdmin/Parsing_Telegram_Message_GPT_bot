# -*- coding: utf-8 -*-
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_admin_keyboard():
    """
    Клавиатура администратора
    :return:
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Запуск отслеживания", icon_custom_emoji_id="5438489737125975601")],
            [KeyboardButton(text="Проверка группы на наличие ключевых слов", icon_custom_emoji_id="5247057031789040703")],
            [KeyboardButton(text="AI поиск", icon_custom_emoji_id="5357314052072692864"),
             KeyboardButton(text="Получить базу", icon_custom_emoji_id="5443127283898405358")],
            [KeyboardButton(text="Инструкция по использованию", icon_custom_emoji_id="5332724926216428039")],
            [KeyboardButton(text="Настройки", icon_custom_emoji_id="5341715473882955310")],
            [KeyboardButton(text="Панель администратора", icon_custom_emoji_id="5368461927452258024")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def admin_keyboard():
    """
    Подключает группу для сообщений, в которую будут отправляться уведомления о новых найденных группах.
    :return: (ReplyKeyboardMarkup) Объект клавиатуры с кнопками и эмодзи."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📄 Получить лог файл")],
            [KeyboardButton(text="🔄 Актуализация базы данных")],
            [KeyboardButton(text="🏷️ Присвоить категорию")],
            [KeyboardButton(text="✅ Проверка аккаунтов")],
            [KeyboardButton(text="🌐 Присвоить язык")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )
