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
    :return:
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="Запуск отслеживания",
                    icon_custom_emoji_id="5438489737125975601",
                    style='primary'
                )
            ],
            [
                KeyboardButton(
                    text="Проверка группы на наличие ключевых слов",
                    icon_custom_emoji_id="5247057031789040703",
                    style='primary'
                )
            ],
            [
                KeyboardButton(
                    text="AI поиск",
                    icon_custom_emoji_id="5357314052072692864",
                    style='primary'
                ),
                KeyboardButton(
                    text="Получить базу",
                    icon_custom_emoji_id="5443127283898405358",
                    style='primary'
                )
            ],

            [
                KeyboardButton(
                    text="Глобальный AI поиск",
                    icon_custom_emoji_id="5357314052072692864",
                    style='primary'
                )
            ],

            [
                KeyboardButton(
                    text="Инструкция по использованию",
                    icon_custom_emoji_id="5332724926216428039",
                    style='primary'
                )
            ],
            [
                KeyboardButton(
                    text="Настройки",
                    icon_custom_emoji_id="5341715473882955310",
                    style='primary'
                )
            ],
            [
                KeyboardButton(
                    text="Панель администратора",
                    icon_custom_emoji_id="5368461927452258024",
                    style='success'
                )
            ]
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
            [KeyboardButton(text="📄 Получить лог файл"), KeyboardButton(text="🔄 Актуализация базы данных")],
            [KeyboardButton(text="🏷️ Присвоить категорию"), KeyboardButton(text="✅ Проверка аккаунтов")],
            [KeyboardButton(text="🌐 Присвоить язык"), KeyboardButton(text="Подключение аккаунта")],
            [KeyboardButton(text="Назад", icon_custom_emoji_id="5352759161945867747", style="danger")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )
