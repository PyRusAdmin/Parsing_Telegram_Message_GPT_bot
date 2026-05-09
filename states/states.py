# -*- coding: utf-8 -*-
from aiogram.fsm.state import StatesGroup, State


class MyStates(StatesGroup):
    # ... (existing states)
    waiting_for_instruction_question = State()
    """
    Группа состояний машины состояний (FSM) для бота AutoParseAlertBot.

    Содержит все пользовательские состояния, используемые при взаимодействии с ботом.
    Каждое состояние соответствует определённому этапу ввода данных.
    """
    waiting_username_group = State()  # Ожидание ввода одного или нескольких @username групп для отслеживания
    entering_keyword = State()  # Ожидание ввода одного или нескольких ключевых слов для поиска
    entering_group = State()  # Ожидание ввода @username технической группы для пересылки сообщений
    entering_keyword_ai_search = State()  # Ожидание ввода темы/ключевого слова для AI-поиска групп и каналов
    del_username_groups = State()

    entering_keyword_ai_search_global = State()  # Глобальный поиск с помощью AI

    waiting_for_session_file = State()  # Ждем файл в формате session
    processing_sessions = State()  # Обработка очереди файлов (внутреннее)

    waiting_for_session_file_user = State()  # Ждем файл в формате session


class MyStatesParsing(StatesGroup):
    get_url = State()  # Ожидание ввода URL для парсинга
    get_keyword = State()  # Ожидание ввода ключевого слова для поиска


class ExportStates(StatesGroup):
    """
    Группа состояний для процесса экспорта данных в боте.

    Содержит состояния, используемые при взаимодействии пользователя
    с функцией экспорта, например, ожидание выбора категории.
    """
    waiting_for_category = State()  # Ожидание выбора категории для экспорта


class CategoryMethod(StatesGroup):
    """Состояния для выбора метода присвоения категорий"""
    waiting_for_method = State()
