from loguru import logger  # https://github.com/Delgan/loguru
from peewee import (
    IntegerField, AutoField, TextField
)

from database.database import database

"""
Запись в базу данных вопросов пользователей, что бы расширить базу знаний
"""


class Question(database.Model):
    """Модель для хранения вопросов пользователей и ответов базы знаний"""
    id = AutoField()  # автоинкремент
    user_id = IntegerField()  # ID пользователя Telegram
    question = TextField()  # Вопрос пользователя
    answer = TextField(null=True)  # Ответ на вопрос от бота


def add_question(user_id: int, question: str, answer: str):
    """
    Добавляет вопрос в базу данных.

    :param user_id: Telegram ID пользователя
    :param question: Вопрос пользователя
    :param answer: Ответ на вопрос
    :return: True, если вопрос добавлен, иначе False
    """
    Question.create(user_id=user_id, question=question, answer=answer)
    return True


def get_all_questions():
    """
    Получает все вопросы и ответы из базы данных.

    :return: Список словарей с вопросами и ответами
    """
    try:
        questions = Question.select()
        result = [
            {
                'user_id': q.user_id,
                'question': q.question,
                'answer': q.answer
            }
            for q in questions
        ]
        return result
    except Exception as e:
        logger.exception(f"❌ Ошибка получения всех вопросов: {e}")
        return []
