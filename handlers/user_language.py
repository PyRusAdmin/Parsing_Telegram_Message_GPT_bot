from database.users_personal_trackings import UsersPersonalTrackings


def determines_user_language(message_or_callback) -> str:
    """
    Определяет язык пользователя, выбранный при первом запуске бота.
    Поддерживает:
      - user_id (int или str)
      - CallbackQuery (извлекает callback.from_user.id)
      - Message (извлекает message.from_user.id)

    :param message_or_callback: ID пользователя или объект сообщения/коллбэка
    :return: код языка пользователя ("ru" по умолчанию)
    """
    user_id = None
    if isinstance(message_or_callback, int):
        user_id = message_or_callback
    elif isinstance(message_or_callback, str) and message_or_callback.isdigit():
        user_id = int(message_or_callback)
    elif hasattr(message_or_callback, 'from_user') and message_or_callback.from_user:
        user_id = message_or_callback.from_user.id
    elif hasattr(message_or_callback, 'user_id'):
        user_id = message_or_callback.user_id

    if not user_id:
        return "ru"

    try:
        user = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_id)
        if user and user.language and user.language != "unset":
            return user.language
    except Exception:
        pass

    return "ru"
