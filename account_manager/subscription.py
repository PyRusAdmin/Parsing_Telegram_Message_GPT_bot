import asyncio

from loguru import logger  # https://github.com/Delgan/loguru
from telethon.errors import (
    UserAlreadyParticipantError, FloodWaitError, InviteRequestSentError, AuthKeyUnregisteredError, ChannelPrivateError
)
from telethon.tl.functions.channels import JoinChannelRequest

from account_manager.utilit import normalize_telegram_link


async def subscription_telegram(client, target_username):
    """
    Подписка на группы каналы Telegram
    :param client: Telethon Client
    :param target_username: Имя канала Telegram
    """
    logger.warning(f"🔗 Подписка на {target_username}")
    # Нормализуем ссылку в единый вид (https://t.me/username) с помощью регулярных выражений
    normalized = normalize_telegram_link(input_link=target_username)
    try:
        await client.get_entity(normalized)
        logger.info(f"✅ Уже подписаны на группу {normalized}")
        return
    except FloodWaitError as e:
        logger.error(f"⚠️ FloodWait {e.seconds} сек.")
    except Exception as e:
        logger.exception(e)
        pass  # Не подписаны, продолжаем подписку

    try:
        logger.info(f"🔗 Попытка присоединиться к целевой группе {normalized}...")
        # ToDo сделать общую функцию для подписки на канал / группу
        await client(JoinChannelRequest(normalized))

        logger.success(f"✅ Успешно присоединился к целевой группе {normalized}")
    except UserAlreadyParticipantError:
        logger.info(f"ℹ️ Вы уже являетесь членом целевой группы {normalized}")
        entity = await client.get_entity(normalized)
        return entity.telegram_id
    except FloodWaitError as e:
        logger.warning(f"⚠️ Ошибка FloodWait. Ожидание {e.seconds} секунд...")
        await asyncio.sleep(e.seconds)
        try:
            # ToDo сделать общую функцию для подписки на канал / группу
            await client(JoinChannelRequest(normalized))
            entity = await client.get_entity(normalized)
            return entity.telegram_id
        except Exception as retry_error:
            logger.error(f"❌ Не удалось присоединиться к целевой группе после повторной попытки: {retry_error}")
            return None
    except AuthKeyUnregisteredError:
        logger.error(f"Не валидная сеесия Telegram. Разорвано соединение")
        return None
    except ValueError:
        logger.error(f"❌ Неверное имя пользователя целевой группы: {normalized}")
        return None
    except InviteRequestSentError:
        logger.error(f"❌ Запрос на приглашение отправлен для {normalized}, ожидание одобрения")
        return None
    except ChannelPrivateError:
        logger.error(f"⚠️ Канал {normalized} приватный")
    except Exception as e:
        logger.exception(e)
        return None
