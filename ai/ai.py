# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime

import groq
from groq import AsyncGroq
from loguru import logger  # https://loguru.readthedocs.io/en/stable/overview.html
from telethon.errors import FloodWaitError, UsernameNotOccupiedError, FrozenMethodInvalidError
from telethon.sync import functions

from account_manager.parser import determine_telegram_chat_type
from core.config import GROQ_API_KEY
from core.proxy import setup_proxy
from database.database import TelegramGroup

"""
Категории для присваивания группам и каналам из базы данных

Инвестиции, Финансы и личный бюджет, Криптовалюты и блокчейн, Бизнес и предпринимательство
Маркетинг и продвижение, Технологии и IT, Образование и саморазвитиеРабота и карьера,
Недвижимость, Здоровье и медицина, Путешествия, Авто и транспорт, Шоппинг и скидки, Развлечения и досуг,
Политика и общество, Наука и исследования, Спорт  и фитнес, Кулинария и еда, Мода и красота, Хобби и творчество
"""


async def category_assignment(group_data: dict, client, model) -> dict:
    """
    Универсальная функция для определения категории через любой AI клиент.
    Работает с g4f (синхронный), Groq, OpenAI (асинхронные).

    :param group_data: dict с полями name, description, username, group_type, telegram_id
    :param client: g4f.client.Client | AsyncGroq | OpenAI
    :param model: название модели
    :return: dict с результатом: {"telegram_id": ..., "category": ..., "success": bool}
    """
    setup_proxy()

    try:
        # 🧩 Формируем контекст
        data_parts = []
        if group_data.get('name'):
            data_parts.append(f"Название: {group_data['name']}")
        if group_data.get('description'):
            data_parts.append(f"Описание: {group_data['description']}")
        if group_data.get('username'):
            data_parts.append(f"Username: @{group_data['username']}")
        if group_data.get('group_type'):
            data_parts.append(f"Тип: {group_data['group_type']}")

        user_input = "\n".join(data_parts) if data_parts else "Нет данных"

        prompt = (
            f"На основе следующих данных о Telegram-группе или канале:\n\n{user_input}\n\n"
            "Выбери ОДНУ наиболее подходящую категорию из списка ниже. "
            "Ответь ТОЛЬКО названием категории из списка, без пояснений, кавычек, точек и других знаков препинания. "
            "Если ни одна категория не подходит — ответь 'Не определена'.\n\n"
            "СПИСОК КАТЕГОРИЙ (выбирай ТОЛЬКО из этого списка):\n"
            "Инвестиции\nФинансы и личный бюджет\nКриптовалюты и блокчейн\n"
            "Бизнес и предпринимательство\nМаркетинг и продвижение\nТехнологии и IT\n"
            "Образование и саморазвитие\nРабота и карьера\nНедвижимость\n"
            "Здоровье и медицина\nПутешествия\nАвто и транспорт\nШоппинг и скидки\n"
            "Развлечения и досуг\nПолитика и общество\nНаука и исследования\n"
            "Спорт и фитнес\nКулинария и еда\nМода и красота\nХобби и творчество\n\n"
            "ПРАВИЛА:\n"
            "1. Ответ должен содержать ТОЛЬКО одно слово или фразу из списка категорий\n"
            "2. Никаких приветствий, объяснений, рекламы или дополнительного текста\n"
            "3. Никаких кавычек, точек или других символов\n"
            "4. Язык ответа: русский\n\n"
            "Пример правильного ответа: Технологии и IT\n"
            "Пример неправильного ответа: Hello! I think this is about technology.\n\n"
            "Твой ответ:"
        )

        # 🤖 Определяем тип клиента и делаем запрос
        client_type = type(client).__name__

        # Асинхронные клиенты (Groq, OpenAI)
        if client_type in ['AsyncGroq', 'AsyncOpenAI']:
            completion = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=20
            )
        # Синхронные клиенты (g4f, OpenAI) - вызываем через to_thread
        else:
            completion = await asyncio.to_thread(
                client.chat.completions.create,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=20
            )

        category = (
            completion.choices[0].message.content
            .strip()
            .strip('".')
        )

        # 🧹 Дополнительная очистка от мусора (реклама, приветствия и т.д.)
        # Если ответ содержит пробелы и не похож на категорию — берём первую строку
        if '\n' in category:
            category = category.split('\n')[0].strip()

        # Если ответ слишком длинный или содержит подозрительные слова — отклоняем
        suspicious_phrases = ['hello', 'hi ', 'i am', 'thank', 'proxy', 'http', 'www', 'click', 'buy']
        if any(phrase in category.lower() for phrase in suspicious_phrases):
            logger.debug(f"⚠️ Подозрительный ответ AI: {category}")
            category = "не определена"

        # ✅ Валидация результата — сверяем со списком допустимых категорий
        valid_categories = [
            "инвестиции", "финансы и личный бюджет", "криптовалюты и блокчейн",
            "бизнес и предпринимательство", "маркетинг и продвижение", "технологии и it",
            "образование и саморазвитие", "работа и карьера", "недвижимость",
            "здоровье и медицина", "путешествия", "авто и транспорт", "шоппинг и скидки",
            "развлечения и досуг", "политика и общество", "наука и исследования",
            "спорт и фитнес", "кулинария и еда", "мода и красота", "хобби и творчество",
            "не определена"
        ]

        if not category or category.lower() not in valid_categories:
            logger.debug(f"⚪ AI вернул некорректную категорию '{category}' для: {group_data.get('name')}")
            return {"telegram_id": group_data["telegram_id"], "category": None, "success": False}

        # Нормализуем категорию (нижний регистр)
        category = category.lower()

        logger.debug(f"✅ AI определил: '{group_data.get('name')}' → {category}")
        return {
            "telegram_id": group_data["telegram_id"],
            "category": category,
            "success": True
        }

    except Exception as e:
        logger.warning(f"⚠️ Ошибка AI для {group_data.get('name')}: {type(e).__name__}: {e}")
        return {
            "telegram_id": group_data.get("telegram_id"),
            "category": None,
            "success": False,
            "error": str(e)
        }


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
    Проверяет дату последнего сообщения и обновляет поле availability в БД.
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

                # ========== Проверка даты последнего сообщения ==========
                last_message_date = None
                availability = 'unknown'

                try:
                    # Получаем историю сообщений (последнее сообщение)
                    messages = await client.get_messages(chat.id, limit=1)
                    if messages and len(messages) > 0:
                        last_message = messages[0]
                        last_message_date = last_message.date
                        logger.debug(f"📅 Последнее сообщение в '{title}': {last_message_date}")

                        # Определяем активность по дате последнего сообщения
                        # Убираем часовой пояс для корректного сравнения
                        last_message_naive = last_message_date.replace(tzinfo=None)
                        days_since_last_message = (datetime.now() - last_message_naive).days

                        if days_since_last_message <= 7:
                            availability = 'active'  # Активная группа (сообщения за последнюю неделю)
                        elif days_since_last_message <= 30:
                            availability = 'active'  # Относительно активная (сообщения за последний месяц)
                        else:
                            availability = 'inactive'  # Неактивная (нет сообщений больше месяца)
                    else:
                        availability = 'inactive'  # Нет сообщений вообще
                        logger.warning(f"⚠️ В группе '{title}' нет сообщений")

                except Exception as e:
                    logger.warning(f"Не удалось получить дату последнего сообщения для '{title}': {e}")
                    availability = 'unknown'  # Не удалось определить

                # ========== Сохранение в базу данных ==========
                try:
                    # Проверяем, существует ли уже группа
                    existing_group = TelegramGroup.get_or_none(
                        (TelegramGroup.telegram_id == telegram_id) |
                        (TelegramGroup.group_hash == group_hash)
                    )

                    if existing_group:
                        # Обновляем существующую запись
                        existing_group.availability = availability
                        existing_group.save()
                        logger.debug(f"🔄 Обновлена активность группы '{title}': {availability}")
                    else:
                        # Создаём новую запись
                        TelegramGroup.create(
                            telegram_id=telegram_id,
                            group_hash=group_hash,
                            name=title,
                            username=username,
                            description='',
                            participants=participants,
                            category='',
                            group_type=group_type,
                            language='',
                            link=link,
                            availability=availability
                        )
                        logger.debug(f"✅ Добавлена новая группа '{title}': {availability}")

                except Exception as e:
                    logger.exception(f"Ошибка при сохранении группы '{title}' в БД: {e}")

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
                    'link': link,
                    'availability': availability,
                    'last_message_date': last_message_date.isoformat() if last_message_date else None
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
