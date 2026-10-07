import asyncio

from loguru import logger  # https://github.com/Delgan/loguru
from telethon.errors import (
    UserAlreadyParticipantError, FloodWaitError, InviteRequestSentError,
    AuthKeyUnregisteredError, ChannelPrivateError, ChannelInvalidError,
    UsernameNotOccupiedError, UsernameInvalidError
)
from telethon.tl.functions.channels import JoinChannelRequest

from account_manager.utilit import normalize_telegram_link


async def subscription_telegram(client, target_username) -> bool:
    """
    Подписка на группу или канал Telegram.

    :param client: Telethon Client
    :param target_username: Имя пользователя или ссылка на канал/группу Telegram
    :return: True если успешно подписались или уже являемся участником, False если канал не найден или произошла ошибка
    """
    if client is None:
        logger.error(f"❌ client is None при попытке подписаться на {target_username}")
        return False

    if not target_username:
        return False

    # Нормализуем ссылку в единый вид (https://t.me/username) с помощью регулярных выражений
    normalized = normalize_telegram_link(input_link=target_username)
    if not normalized:
        logger.warning(f"⚠️ Не удалось распознать ссылку или юзернейм: {target_username}")
        return False

    # 1. Получаем сущность канала/группы через get_entity
    try:
        entity = await client.get_entity(normalized)
    except (UsernameNotOccupiedError, UsernameInvalidError):
        logger.warning(f"⚠️ Канал/группа не существует: {normalized}")
        return False
    except ValueError as e:
        logger.warning(f"⚠️ Не удалось найти канал/группу {normalized}: {e}")
        return False
    except ChannelPrivateError:
        logger.warning(f"⚠️ Канал {normalized} приватный или доступ ограничен")
        return False
    except FloodWaitError as e:
        logger.warning(f"⚠️ FloodWait {e.seconds} сек. при получении информации о {normalized}")
        return False
    except AuthKeyUnregisteredError:
        logger.error("❌ Невалидная сессия Telegram. Разорвано соединение")
        return False
    except Exception as e:
        logger.warning(f"⚠️ Ошибка при получении информации о {normalized}: {e}")
        return False

    # 2. Проверяем, не являемся ли мы уже участником канала/группы
    if getattr(entity, 'left', None) is False:
        logger.info(f"ℹ️ Вы уже являетесь членом целевой группы {normalized}")
        return True

    # 3. Присоединяемся к каналу/группе
    try:
        logger.info(f"🔗 Попытка присоединиться к целевой группе {normalized}...")
        await client(JoinChannelRequest(entity))
        logger.success(f"✅ Успешно присоединился к целевой группе {normalized}")
        return True
    except UserAlreadyParticipantError:
        logger.info(f"ℹ️ Вы уже являетесь членом целевой группы {normalized}")
        return True
    except InviteRequestSentError:
        logger.info(f"📩 Запрос на приглашение отправлен для {normalized}, ожидание одобрения")
        return True
    except FloodWaitError as e:
        logger.warning(f"⚠️ Ошибка FloodWait. Ожидание {e.seconds} секунд...")
        await asyncio.sleep(e.seconds)
        try:
            await client(JoinChannelRequest(entity))
            logger.success(f"✅ Успешно присоединился к целевой группе {normalized} после ожидания")
            return True
        except UserAlreadyParticipantError:
            return True
        except Exception as retry_error:
            logger.error(f"❌ Не удалось присоединиться к {normalized} после ожидания: {retry_error}")
            return False
    except (ChannelPrivateError, ChannelInvalidError):
        logger.warning(f"⚠️ Канал {normalized} приватный или недействителен")
        return False
    except (UsernameNotOccupiedError, UsernameInvalidError, ValueError):
        logger.warning(f"❌ Неверное имя пользователя целевой группы: {normalized}")
        return False
    except AuthKeyUnregisteredError:
        logger.error("❌ Невалидная сессия Telegram. Разорвано соединение")
        return False
    except Exception as e:
        logger.error(f"❌ Не удалось присоединиться к {normalized}: {e}")
        return False
