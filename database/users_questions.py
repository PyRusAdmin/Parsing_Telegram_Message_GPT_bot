from datetime import datetime
from loguru import logger  # https://github.com/Delgan/loguru
from peewee import (
    BigIntegerField, AutoField, TextField, CharField, DateTimeField, IntegerField, fn
)

from database.database import database

"""
Запись в базу данных вопросов пользователей, чтобы расширить базу знаний.
Таблица: users_questions

В таблице users_questions будут храниться вопросы от пользователей, которые они задавали боту по поводу работы с ботом.
Отвечать на вопросы будет бот с помощью ИИ и на основе базы знаний.
Работа с таблицей users_questions находится в файле users_questions.py для быстрого ориентирования в проекте.
"""


class UsersQuestions(database.Model):
    """
    Модель для хранения вопросов пользователей и ответов базы знаний.
    Таблица users_questions.

    Структура users_questions:
    - id - ID записи в базе данных
    - question_number - Номер вопроса, для удобной обработки администратором
    - user_id - id пользователя Telegram
    - user_username - username пользователя Telegram
    - user_firstname - firstname пользователя Telegram
    - user_question - Вопрос пользователя
    - answer_ai - Ответ пользователю от ИИ
    - status_question - статус обработки вопроса администратором ('Соответствует', 'Не соответствует')
    - date_added - Дата добавления в базу данных
    """
    id = AutoField()  # ID записи в базе данных
    question_number = IntegerField(null=True)  # Номер вопроса, для удобной обработки администратором
    user_id = BigIntegerField()  # id пользователя Telegram
    user_username = CharField(max_length=255, null=True)  # username пользователя Telegram
    user_firstname = CharField(max_length=255, null=True)  # firstname пользователя Telegram
    user_question = TextField()  # Вопрос пользователя
    answer_ai = TextField(null=True)  # Ответ пользователю от ИИ.
    status_question = CharField(max_length=100, default="Не проверен")  # статус обработки вопроса администратором
    date_added = DateTimeField(default=datetime.now)  # Дата добавления в базу данных

    class Meta:
        """Метаданные таблицы с вопросами от пользователей"""
        table_name = 'users_questions'


def add_question(user_id: int, user_question: str = None, answer_ai: str = None, user_username: str = None,
                 user_firstname: str = None, status_question: str = "Не проверен", question: str = None,
                 answer: str = None, status: str = None):
    """
    Добавляет вопрос пользователя и ответ ИИ в базу данных users_questions.

    :param user_id: (int) Telegram ID пользователя.
    :param user_question: (str | None) Вопрос пользователя.
    :param answer_ai: (str | None) Ответ пользователю от ИИ.
    :param user_username: (str | None) Username пользователя в Telegram.
    :param user_firstname: (str | None) Имя пользователя в Telegram.
    :param status_question: (str) Статус обработки вопроса администратором ('Соответствует', 'Не соответствует' и др.).
    :param question: (str | None) Алиас для параметра user_question.
    :param answer: (str | None) Алиас для параметра answer_ai.
    :param status: (str | None) Алиас для параметра status_question.
    :return: (UsersQuestions | None) Созданный объект UsersQuestions или None при ошибке.
    """
    try:
        # Определяем следующий порядковый номер вопроса
        max_num = UsersQuestions.select(fn.MAX(UsersQuestions.question_number)).scalar()
        next_num = (max_num or 0) + 1

        rec = UsersQuestions.create(
            question_number=next_num,
            user_id=user_id,
            user_username=user_username,
            user_firstname=user_firstname,
            user_question=user_question or question or "",
            answer_ai=answer_ai if answer_ai is not None else answer,
            status_question=status_question if status_question != "Не проверен" or status is None else status,
            date_added=datetime.now()
        )
        logger.info(f"Вопрос №{next_num} от user_id={user_id} сохранён в users_questions")
        return rec
    except Exception as e:
        logger.exception(f"❌ Ошибка добавления вопроса в users_questions: {e}")
        return None


def update_question_status(question_id: int, status_question: str) -> bool:
    """
    Обновляет статус обработки вопроса администратором ('Соответствует', 'Не соответствует').

    :param question_id: (int) ID записи в базе данных или номер вопроса.
    :param status_question: (str) Статус проверки ('Соответствует', 'Не соответствует').
    :return: (bool) True, если обновлено успешно, иначе False.
    """
    try:
        updated = (
            UsersQuestions.update(status_question=status_question)
            .where((UsersQuestions.id == question_id) | (UsersQuestions.question_number == question_id))
            .execute()
        )
        logger.info(f"Статус вопроса #{question_id} изменен на '{status_question}' (обновлено строк: {updated})")
        return updated > 0
    except Exception as e:
        logger.exception(f"❌ Ошибка обновления статуса вопроса #{question_id}: {e}")
        return False


def get_all_questions():
    """
    Получает все вопросы и ответы из таблицы users_questions.

    :return: (list[dict]) Список словарей с подробной информацией о вопросах.
    """
    try:
        questions = UsersQuestions.select().order_by(UsersQuestions.id.asc())
        result = [
            {
                'id': q.id,
                'question_number': q.question_number or q.id,
                'user_id': q.user_id,
                'user_username': q.user_username or "",
                'user_firstname': q.user_firstname or "",
                'user_question': q.user_question,
                'answer_ai': q.answer_ai or "",
                'status_question': q.status_question or "Не проверен",
                # Алиасы для обратной совместимости
                'answer': q.answer_ai or "",
                'status': q.status_question or "Не проверен",
                'question': q.user_question,
                'date_added': q.date_added.strftime("%Y-%m-%d %H:%M:%S") if q.date_added else ""
            }
            for q in questions
        ]
        return result
    except Exception as e:
        logger.exception(f"❌ Ошибка получения всех вопросов: {e}")
        return []
