from datetime import datetime
from loguru import logger  # https://github.com/Delgan/loguru
from peewee import (
    IntegerField, AutoField, TextField, CharField, DateTimeField, fn
)

from database.database import database

"""
Запись в базу данных вопросов пользователей, чтобы расширить базу знаний.
Таблица: users_questions
"""


class Question(database.Model):
    """
    Модель для хранения вопросов пользователей и ответов базы знаний.
    Таблица users_questions.
    """
    id = AutoField()  # ID записи в базе данных
    question_number = IntegerField(null=True)  # Номер вопроса для удобной обработки администратором
    user_id = IntegerField()  # ID пользователя Telegram
    user_username = CharField(max_length=255, null=True)  # username пользователя Telegram
    user_firstname = CharField(max_length=255, null=True)  # firstname пользователя Telegram
    user_question = TextField()  # Вопрос пользователя
    answer = TextField(null=True)  # Ответ пользователю от ИИ
    status = CharField(max_length=100, default="Новый")  # Статус обработки вопроса администратором
    date_added = DateTimeField(default=datetime.now)  # Дата добавления в базу данных

    class Meta:
        """Метаданные таблицы с вопросами от пользователей"""
        table_name = 'users_questions'

    @property
    def question(self):
        """Алиас для обратной совместимости со старым кодом"""
        return self.user_question

    @question.setter
    def question(self, value):
        self.user_question = value


def add_question(user_id: int, question: str = None, answer: str = None, user_question: str = None,
                 user_username: str = None, user_firstname: str = None, status: str = "Новый"):
    """
    Добавляет вопрос пользователя и ответ ИИ в базу данных users_questions.

    :param user_id: Telegram ID пользователя
    :param question: Вопрос пользователя (обратная совместимость)
    :param answer: Ответ на вопрос от ИИ
    :param user_question: Вопрос пользователя
    :param user_username: username пользователя в Telegram
    :param user_firstname: firstname пользователя в Telegram
    :param status: Статус обработки вопроса администратором
    :return: Созданный объект Question или None при ошибке
    """
    try:
        final_question = user_question or question or ""
        # Определяем следующий порядковый номер вопроса
        max_num = Question.select(fn.MAX(Question.question_number)).scalar()
        next_num = (max_num or 0) + 1

        rec = Question.create(
            question_number=next_num,
            user_id=user_id,
            user_username=user_username,
            user_firstname=user_firstname,
            user_question=final_question,
            answer=answer,
            status=status,
            date_added=datetime.now()
        )
        return rec
    except Exception as e:
        logger.exception(f"❌ Ошибка добавления вопроса в users_questions: {e}")
        return None


def get_all_questions():
    """
    Получает все вопросы и ответы из таблицы users_questions.

    :return: Список словарей с подробной информацией о вопросах
    """
    try:
        questions = Question.select().order_by(Question.id.asc())
        result = [
            {
                'id': q.id,
                'question_number': q.question_number or q.id,
                'user_id': q.user_id,
                'user_username': q.user_username or "",
                'user_firstname': q.user_firstname or "",
                'user_question': q.user_question,
                'question': q.user_question,  # Алиас для обратной совместимости
                'answer': q.answer or "",
                'status': q.status or "Новый",
                'date_added': q.date_added.strftime("%Y-%m-%d %H:%M:%S") if q.date_added else ""
            }
            for q in questions
        ]
        return result
    except Exception as e:
        logger.exception(f"❌ Ошибка получения всех вопросов: {e}")
        return []
