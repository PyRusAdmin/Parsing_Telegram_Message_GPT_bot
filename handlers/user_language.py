from database.database import User


def determines_user_language(message_or_callback):
    """
    Определяет язык пользователя, выбранное при первом запуске бота.
    Данные загружаются из таблицы User в базе данных.

    :param message_or_callback: ID пользователя (int) из message или callback
    :return: код языка пользователя ("ru" по умолчанию)
    """
    user = User.get(User.user_id == message_or_callback)
    return user.language if user.language != "unset" else "ru"  # Возвращаем язык пользователя
