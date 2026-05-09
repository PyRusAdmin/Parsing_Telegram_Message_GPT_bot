from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

'''
🔴 danger — красная кнопка (идеально для «Удалить», «Отмена», «Бан»).
🟢 success — зелёная кнопка («Подтвердить», «Оплатить», «Принять»).
🔵 primary — синяя кнопка (для основных целевых действий).
⚪️ Стандартный — привычный прозрачно-серый цвет.
'''


def menu_user_admin_keyboard():
    """Клавиатура админа и пользователя"""
    return [[
        KeyboardButton(text="🚀 Запуск отслеживания")
    ],
        [
            KeyboardButton(text="🔍 Проверка группы на наличие ключевых слов")
        ],
        [
            KeyboardButton(text="🤖 AI поиск"),
            KeyboardButton(text="📥 Получить базу")
        ],

        [
            KeyboardButton(text="🌐 Глобальный AI поиск")
        ],

        [
            KeyboardButton(text="📖 Инструкция по использованию")
        ],
        [
            KeyboardButton(text="⚙️ Настройки")
        ]]

def main_admin_keyboard():
    """
    Клавиатура администратора
    :return: ReplyKeyboardMarkup
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            *menu_user_admin_keyboard(),
            [
                KeyboardButton(text="🛡️ Панель администратора")
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
                KeyboardButton(text="📄 Получить лог файл"),
                KeyboardButton(text="🔄 Актуализация базы данных")
            ],
            [
                KeyboardButton(text="🏷️ Присвоить категорию"),
                KeyboardButton(text="✅ Проверка аккаунтов")
            ],
            [
                KeyboardButton(text="🌐 Присвоить язык"),
                KeyboardButton(text="🔐 Подключение аккаунта")
            ],
            [
                KeyboardButton(text="⬅️ Назад")
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
                KeyboardButton(text="⚡️ Быстро (g4f.free)")
            ],
            [
                KeyboardButton(text="🚀 Мощно (Openrouter API)")
            ],
            [
                KeyboardButton(text="🚀 Мощно (GROQ API)")
            ],
            [
                KeyboardButton(text="⬅️ Назад")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
