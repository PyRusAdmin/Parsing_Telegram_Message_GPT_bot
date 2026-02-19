# -*- coding: utf-8 -*-
import asyncio
import os

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
    Асинхронно ищет публичные группы и каналы в Telegram по заданным названиям.

    Для каждого названия выполняется поиск через Telegram API, и из результатов
    отбираются только каналы (Channel), содержащие совпадения по названию.

    :param client: (TelegramClient) Экземпляр клиентского объекта Telegram
    :param group_names: list[str] Список строк с названиями групп для поиска.

    Returns:
        list[dict]: Список словарей с информацией о найденных группах. Каждый словарь содержит:
            - 'name' (str): Название группы.
            - 'username' (str): Юзернейм группы (с @) или "нет юзернейма".
            - 'link' (str): Ссылка на группу или "недоступна".
            - 'participants' (int or str): Количество участников или "неизвестно".
            - 'telegram_id' (int): Уникальный идентификатор чата в Telegram.

    Notes:
        - Требует предварительной авторизации клиента Telegram.
        - Обрабатывает ошибки FloodWaitError, приостанавливая выполнение на указанное время.
        - Пропускает пустые строки в списке запросов.
        - Использует Telethon для низкоуровневого взаимодействия с Telegram API.
    """
    found_groups = []

    for name in group_names:
        if not name.strip():
            continue

        logger.info(f"Ищу группу: '{name}'")

        try:
            # ✅ Используем SearchRequest для поиска по названию
            search_results = await client(functions.contacts.SearchRequest(q=name, limit=10))

            # Обрабатываем результаты
            for chat in search_results.chats:
                logger.info(chat)
                telegram_id = chat.id
                group_hash = chat.access_hash
                name = chat.title or ''
                username = f"@{chat.username}"
                description = ''
                participants = chat.participants_count
                category = ''
                group_type = determine_telegram_chat_type(entity=chat)
                language = ''
                link = f"https://t.me/{chat.username}"

                found_groups.append(
                    {
                        'telegram_id': telegram_id,
                        'group_hash': group_hash,
                        'name': name,
                        'username': username,
                        'description': description,
                        'participants': participants,
                        'category': category,
                        'group_type': group_type,
                        'language': language,
                        'link': link
                    }
                )

        except FrozenMethodInvalidError:
            logger.warning('Аккаунт заморожен!')

            try:
                os.remove(f"{path}/{session_name}.session")
            except FileNotFoundError:
                pass  # файл уже удалён

        except UsernameNotOccupiedError:
            logger.warning(f"Группа '{name}' не найдена.")
        except FloodWaitError as e:
            logger.error(f"Слишком много запросов. Ждём {e.seconds} секунд.")
            await asyncio.sleep(e.seconds + 1)
        except Exception as e:
            logger.exception(f"Ошибка при поиске '{name}': {e}")

    # await client.disconnect()
    logger.info("Телеграм-клиент отключён.")
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
