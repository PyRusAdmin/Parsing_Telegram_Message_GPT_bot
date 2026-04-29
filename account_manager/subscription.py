import asyncio

from loguru import logger  # https://github.com/Delgan/loguru
from telethon.errors import (
    UserAlreadyParticipantError, FloodWaitError, InviteRequestSentError, AuthKeyUnregisteredError
)
from telethon.tl.functions.channels import JoinChannelRequest


async def subscription_telegram(client, target_username):
    """
    Подписка на группы каналы Telegram
    :param client: Telethon Client
    :param target_username: Имя канала Telegram
    :return: None
    """
    try:
        await client.get_entity(target_username)
        logger.info(f"✅ Уже подписаны на группу {target_username}")
        return
    except Exception:
        pass  # Не подписаны, продолжаем подписку

    try:
        logger.info(f"🔗 Попытка присоединиться к целевой группе {target_username}...")
        await client(JoinChannelRequest(target_username))
        logger.success(f"✅ Успешно присоединился к целевой группе {target_username}")
    except UserAlreadyParticipantError:
        logger.info(f"ℹ️ Вы уже являетесь членом целевой группы {target_username}")
        entity = await client.get_entity(target_username)
        return entity.telegram_id
    except FloodWaitError as e:
        logger.warning(f"⚠️ Ошибка FloodWait. Ожидание {e.seconds} секунд...")
        await asyncio.sleep(e.seconds)
        try:
            await client(JoinChannelRequest(target_username))
            entity = await client.get_entity(target_username)
            return entity.telegram_id
        except Exception as retry_error:
            logger.error(f"❌ Не удалось присоединиться к целевой группе после повторной попытки: {retry_error}")
            return None
    except AuthKeyUnregisteredError:
        logger.error(f"Не валидная сеесия Telegram. Разорвано соединение")
        return None
    except ValueError:
        logger.error(f"❌ Неверное имя пользователя целевой группы: {target_username}")
        return None
    except InviteRequestSentError:
        logger.error(f"❌ Запрос на приглашение отправлен для {target_username}, ожидание одобрения")
        return None
    except Exception as e:
        logger.exception(e)
        return None
