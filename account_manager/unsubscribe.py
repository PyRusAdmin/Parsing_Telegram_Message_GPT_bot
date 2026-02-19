# -*- coding: utf-8 -*-
from loguru import logger

from telethon.errors import (
    UsernameInvalidError, UsernameNotOccupiedError, UserNotParticipantError, ChannelPrivateError
)
from telethon.tl.types import Channel, Chat

from keyboards.user.keyboards import main_menu_keyboard


async def unsubscribe(client, username_to_search, message):
    """
    Отписываемся от группы 
    
    :param message:
    :param client: клиент Telegram
    :param username_to_search:
    :return: 
    """
    # 1. Пытаемся найти чат по username
    try:
        entity = await client.get_entity(f"@{username_to_search}")
        chat_title = getattr(entity, 'title', getattr(entity, 'first_name', 'Без названия'))
        chat_id = entity.telegram_id
        chat_type = "канал" if isinstance(entity, Channel) else "группа" if isinstance(entity, Chat) else "чат"

        logger.info(f"Найден {chat_type} '{chat_title}' (ID: {chat_id}) для @{username_to_search}")
    except (UsernameInvalidError, UsernameNotOccupiedError, ValueError) as e:
        await message.answer(
            f"❌ Чат с username @{username_to_search} не найден в Telegram. "
            f"Проверьте правильность написания и убедитесь, что вы состоите в этом чате.",
            reply_markup=main_menu_keyboard()
        )
        logger.warning(f"Чат @{username_to_search} не найден для пользователя {message.from_user.user_id}: {e}")
        return

    # 2. Отписываемся от чата
    try:
        # Универсальный способ для групп и каналов
        await client.delete_dialog(entity)
        logger.info(f"Успешная отписка от {chat_type} '{chat_title}' (ID: {chat_id})")
        await message.answer(f"✅ Отписались от {chat_type} «{chat_title}» (@{username_to_search})")
    except (UserNotParticipantError, ChannelPrivateError) as e:
        # Пользователь уже не состоит в чате — продолжаем удаление из БД
        logger.warning(f"Пользователь уже не состоит в чате @{username_to_search}: {e}")
        await message.answer(f"ℹ️ Вы уже не состоите в {chat_type} «{chat_title}» (@{username_to_search})")
