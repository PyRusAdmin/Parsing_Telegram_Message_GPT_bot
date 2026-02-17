# -*- coding: utf-8 -*-
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_admin_keyboard():
    """
    Клавиатура администратора
    :return:
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏯ Запуск отслеживания")],
            [KeyboardButton(text="🔍 Проверка группы на наличие ключевых слов")],
            [KeyboardButton(text="🤖 AI поиск"), KeyboardButton(text="📥 Получить базу")],
            [KeyboardButton(text="📘 Инструкция по использованию")],
            [KeyboardButton(text="⚙ Настройки")],
            [KeyboardButton(text="Панель администратора")]
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
