# -*- coding: utf-8 -*-
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

'''
🔴 danger — красная кнопка (идеально для «Удалить», «Отмена», «Бан»).
🟢 success — зелёная кнопка («Подтвердить», «Оплатить», «Принять»).
🔵 primary — синяя кнопка (для основных целевых действий).
⚪️ Стандартный — привычный прозрачно-серый цвет.
'''


def main_admin_keyboard():
    """
    Клавиатура администратора
    :return: ReplyKeyboardMarkup
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🚀 Запуск отслеживания", style='primary')
            ],
            [
                KeyboardButton(text="🔍 Проверка группы на наличие ключевых слов", style='primary')
            ],
            [
                KeyboardButton(text="🤖 AI поиск", style='primary'),
                KeyboardButton(text="📥 Получить базу", style='primary')
            ],

            [
                KeyboardButton(text="🌐 Глобальный AI поиск", style='primary')
            ],

            [
                KeyboardButton(text="📖 Инструкция по использованию", style='primary')
            ],
            [
                KeyboardButton(text="⚙️ Настройки", style='primary')
            ],
            [
                KeyboardButton(text="🛡️ Панель администратора", style='success')
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def admin_keyboard():
    """
    Клавиатура панели администратора
    :return: (ReplyKeyboardMarkup) Объект клавиатуры с кнопками и эмодзи.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📄 Получить лог файл", style='primary'),
                KeyboardButton(text="🔄 Актуализация базы данных", style='primary')
            ],
            [
                KeyboardButton(text="🏷️ Присвоить категорию", style='primary'
                               ),
                KeyboardButton(text="✅ Проверка аккаунтов", style='success')
            ],
            [
                KeyboardButton(text="🌐 Присвоить язык", style='primary'),
                KeyboardButton(text="🔐 Подключение аккаунта", style='primary')
            ],
            [
                KeyboardButton(text="⬅️ Назад", style='danger')
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def category_method_keyboard():
    """
    Клавиатура для выбора метода присвоения категорий
    :return: (ReplyKeyboardMarkup) Объект клавиатуры с выбором метода
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="⚡️ Быстро (g4f.free)", style='primary')
            ],
            [
                KeyboardButton(text="🚀 Мощно (Openrouter API)", style='success')
            ],
            [
                KeyboardButton(text="🚀 Мощно (GROQ API)", style='success')
            ],
            [
                KeyboardButton(text="⬅️ Назад", style='danger')
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
