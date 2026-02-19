# -*- coding: utf-8 -*-
import asyncio

import groq
from groq import AsyncGroq
from loguru import logger
from telethon.errors import FloodWaitError, UsernameNotOccupiedError, FrozenMethodInvalidError
from telethon.sync import functions

from account_manager.parser import determine_telegram_chat_type
from core.config import GROQ_API_KEY
from core.proxy_config import setup_proxy


async def category_assignment(user_input: str) -> str:
    """
    Назначает категорию с помощью Groq. Возвращает ТОЛЬКО название категории.
    """
    setup_proxy()
    client_groq = AsyncGroq(api_key=GROQ_API_KEY)

    prompt = (
        f"На основе следующих данных о Telegram-группе или канале:\n\n{user_input}\n\n"
        "Выбери ОДНУ наиболее подходящую категорию из списка ниже. "
        "Ответь ТОЛЬКО названием категории, без пояснений, кавычек и знаков препинания.\n\n"
        "Список категорий:\n"
        "Инвестиции\n"
        "Финансы и личный бюджет\n"
        "Криптовалюты и блокчейн\n"
        "Бизнес и предпринимательство\n"
        "Маркетинг и продвижение\n"
        "Технологии и IT\n"
        "Образование и саморазвитие\n"
        "Работа и карьера\n"
        "Недвижимость\n"
        "Здоровье и медицина\n"
        "Путешествия\n"
        "Авто и транспорт\n"
        "Шоппинг и скидки\n"
        "Развлечения и досуг\n"
        "Политика и общество\n"
        "Наука и исследования\n"
        "Спорт и фитнес\n"
        "Кулинария и еда\n"
        "Мода и красота\n"
        "Хобби и творчество"
    )

    try:
        chat_completion = await client_groq.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # снижаем "творчество"
            max_tokens=20  # достаточно для одного слова/фразы
        )
        result = chat_completion.choices[0].message.content.strip()
        logger.debug(f"Groq вернул категорию: '{result}'")
        return result
    except Exception as e:
        logger.exception("Ошибка при вызове Groq")
        return "Не определена"


async def get_groq_response(user_input):
    """
    Асинхронно отправляет запрос к модели Llama 4 Scout через Groq API для генерации вариантов названий групп.

    - Используется модель "meta-llama/llama-4-scout-17b-16e-instruct".
    - Ответ должен содержать только названия, без нумерации и пояснений.
    - Перед выполнением устанавливается прокси с помощью `setup_proxy()`.

    :param user_input: (str) Тема или ключевое слово, на основе которого нужно придумать названия групп.
    :return: str: Строка с 10 вариациями названий групп, разделёнными переносами строк. Возвращает пустую строку при
                  ошибке аутентификации или других исключениях.
    :raise groq.AuthenticationError: Если ключ API недействителен или не установлен.
    :raise Exception: Логируется при других ошибках (сетевые ошибки, таймауты и т.д.).
    """
    setup_proxy()  # Установка прокси
    client_groq = AsyncGroq(api_key=GROQ_API_KEY)
    try:
        chat_completion = await client_groq.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": f"Придумай 55 вариаций названий для групп {user_input}. Ответ дать строго наименования в столбик, без перечисления и без пояснения. 1. 2. 3. не применяй"
                }
            ],
        )
        logger.debug(f"Полный ответ от Groq: {chat_completion}")
        return chat_completion.choices[0].message.content
    except groq.AuthenticationError:
        if GROQ_API_KEY:
            logger.error("Ошибка аутентификации с ключом Groq API.")
        else:
            logger.error("API ключ Groq API не установлен.")

    except Exception as e:
        logger.exception(e)
        return ""


async def search_groups_in_telegram(client, group_names):
    """
    Асинхронно ищет публичные группы и каналы в Telegram по списку названий.
    При заморозке аккаунта сразу прекращает весь поиск.
    """
    found_groups = []
    account_frozen = False

    for name in group_names:
        if not name or not name.strip():
            continue

        if account_frozen:
            logger.warning(f"Аккаунт заморожен. Пропускаем '{name}'")
            continue

        logger.info(f"Ищу группу: '{name}'")

        # Проверяем, подключён ли клиент
        if not client.is_connected():
            try:
                await client.connect()
            except Exception as e:
                logger.error(f"Не удалось подключить клиента: {e}")
                break

        try:
            search_results = await client(functions.contacts.SearchRequest(q=name, limit=10))

            for chat in search_results.chats:
                if not hasattr(chat, 'title') or not chat.title:
                    continue

                telegram_id = chat.id
                group_hash = getattr(chat, 'access_hash', None)
                title = chat.title
                username = f"@{chat.username}" if getattr(chat, 'username', None) else None
                link = f"https://t.me/{chat.username}" if username else None
                participants = getattr(chat, 'participants_count', 0)
                group_type = determine_telegram_chat_type(entity=chat)

                found_groups.append({
                    'telegram_id': telegram_id,
                    'group_hash': group_hash,
                    'name': title,
                    'username': username,
                    'description': '',
                    'participants': participants,
                    'category': '',
                    'group_type': group_type,
                    'language': '',
                    'link': link
                })

        except FrozenMethodInvalidError:
            logger.warning(f'❄️ Аккаунт заморожен при поиске "{name}"!')
            await client.disconnect()
            break  # ← КРИТИЧНО: прекращаем весь поиск

        except UsernameNotOccupiedError:
            logger.warning(f"Группа '{name}' не найдена (UsernameNotOccupiedError)")

        except FloodWaitError as e:
            logger.warning(f"FloodWait {e.seconds} сек при поиске '{name}'. Ждём...")
            await asyncio.sleep(e.seconds + 2)

        except Exception as e:
            if "disconnected" in str(e).lower() or "cannot send" in str(e).lower():
                logger.error("Клиент отключён. Прекращаем поиск.")
                break
            logger.exception(f"Ошибка при поиске '{name}': {e}")

    # Финальное отключение (на всякий случай)
    try:
        if client.is_connected():
            await client.disconnect()
            logger.info("Телеграм-клиент отключён.")
    except Exception as e:
        logger.exception(e)

    if account_frozen:
        logger.error("🔴 Поиск полностью остановлен из-за заморозки аккаунта.")

    return found_groups


"""
Категории для присваивания группам и каналам из базы данных

Инвестиции
Финансы и личный бюджет
Криптовалюты и блокчейн
Бизнес и предпринимательство
Маркетинг и продвижение
Технологии и IT
Образование и саморазвитие
Работа и карьера
Недвижимость
Здоровье и медицина
Путешествия
Авто и транспорт
Шоппинг и скидки
Развлечения и досуг
Политика и общество
Наука и исследования
Спорт и фитнес
Кулинария и еда
Мода и красота
Хобби и творчество
"""
