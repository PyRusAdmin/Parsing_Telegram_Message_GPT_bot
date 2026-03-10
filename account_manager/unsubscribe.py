# -*- coding: utf-8 -*-
from loguru import logger
from telethon.errors import (
    UsernameInvalidError, UsernameNotOccupiedError, UserNotParticipantError, ChannelPrivateError, FloodWaitError
)


async def unsubscribe(client, username_to_search):
    """
    Отписываемся от группы. Username должен быть в формате @username

    :param client: клиент Telegram
    :param username_to_search: username чата в Telegram
    """
    try:
        entity = await client.get_entity(username_to_search)  # Пытаемся найти чат по username
        title = entity.title or ""
        logger.info(f"Найден {title} {username_to_search}")
        await client.delete_dialog(username_to_search)  # Отписываемся от чата
        logger.info(f"Успешная отписка от '{title}' {username_to_search}")
    except (UsernameInvalidError, UsernameNotOccupiedError, ValueError) as e:
        logger.warning(f"Чат {username_to_search} не найден для пользователя: {e}")
        return
    except FloodWaitError as e:
        logger.error(f"⚠️ FloodWait {e.seconds} сек.")
    except (UserNotParticipantError, ChannelPrivateError) as e:
        logger.warning(f"Пользователь уже не состоит в чате {username_to_search}: {e}")
    except Exception as e:
        logger.exception(e)
