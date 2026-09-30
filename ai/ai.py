import asyncio
import re
from datetime import datetime
import random

import groq
import openai
from groq import AsyncGroq
from lingua import LanguageDetectorBuilder  # Библиотека для автоматического определения языка
from loguru import logger  # https://loguru.readthedocs.io/en/stable/overview.html
from telethon.errors import FloodWaitError, UsernameNotOccupiedError, FrozenMethodInvalidError
from telethon.sync import functions
from openai import AsyncOpenAI
from account_manager.parser import determine_telegram_chat_type
from account_manager.utilit import choosing_random_ai_model
from core.config import GROQ_API_KEY, ADMIN_USER_ID, OPENROUTER_API_KEY
from core.constants import ISO_639_1_CODES
from core.proxy import setup_proxy
from database.database import TelegramGroup
from system.dispatcher import bot

"""
Категории для присваивания группам и каналам из базы данных

Инвестиции, Финансы и личный бюджет, Криптовалюты и блокчейн, Бизнес и предпринимательство
Маркетинг и продвижение, Технологии и IT, Образование и саморазвитиеРабота и карьера,
Недвижимость, Здоровье и медицина, Путешествия, Авто и транспорт, Шоппинг и скидки, Развлечения и досуг,
Политика и общество, Наука и исследования, Спорт  и фитнес, Кулинария и еда, Мода и красота, Хобби и творчество
"""


class CategoryAssignment:
    """Определение категории через AI g4f.client.Client AsyncGroq  OpenAI"""

    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )  # g4f.client.Client | AsyncGroq | OpenAI
        self.model = ["deepseek/deepseek-v4-flash"]  # название модели. Например: ""deepseek/deepseek-v4-flash""

    async def get_random_ai_model(self) -> str:
        return random.choice(self.model)

    async def build_group_context(self, group_data):

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

        return "\n".join(data_parts) if data_parts else "Нет данных"

    async def category_assignment(self, group_data: dict) -> dict:
        """
        Универсальная функция для определения категории через любой AI клиент.
        Работает с g4f (синхронный), Groq, OpenAI (асинхронные).

        :param group_data: dict с полями name, description, username, group_type, telegram_id
        :return: dict с результатом: {"telegram_id": ..., "category": ..., "success": bool}
        """
        setup_proxy()
        user_input = self.build_group_context(group_data)
        try:
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
            client_type = type(self.client).__name__

            # Асинхронные клиенты (Groq, OpenAI)
            if client_type in ['AsyncGroq', 'AsyncOpenAI']:
                completion = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=200
                )
            # Синхронные клиенты (g4f, OpenAI) - вызываем через to_thread
            else:
                completion = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=200
                )

            raw_content = completion.choices[0].message.content if (
                    completion and completion.choices and completion.choices[0].message) else None
            if not raw_content:
                logger.debug(f"⚪ AI ({self.model}) вернул пустой ответ для: {group_data.get('name')}")
                return {"telegram_id": group_data.get("telegram_id"), "category": None, "success": False}

            # 🧹 Очищаем от блоков рассуждений <think>...</think> (для reasoning-моделей)
            raw_content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()
            raw_content = re.sub(r'</?think>', '', raw_content).strip()

            logger.debug(f"🤖 Ответ AI ({self.model}) для '{group_data.get('name')}': '{raw_content}'")

            category = raw_content.strip().strip('".\'').lower()

            # Если ответ содержит переносы строк — берём последнюю непустую строку (где обычно и находится итоговый ответ)
            if '\n' in category:
                lines = [l.strip() for l in category.split('\n') if l.strip()]
                if lines:
                    category = lines[-1]

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

            matched_category = None
            for cat in valid_categories:
                if cat in category:
                    matched_category = cat
                    break

            if not matched_category:
                logger.debug(f"⚪ AI вернул некорректную категорию '{raw_content}' для: {group_data.get('name')}")
                return {"telegram_id": group_data["telegram_id"], "category": None, "success": False}

            category = matched_category
            logger.debug(f"✅ AI определил: '{group_data.get('name')}' → {category}")
            return {
                "telegram_id": group_data["telegram_id"],
                "category": category,
                "success": True
            }
        except groq.RateLimitError as e:
            logger.error(f"⚠️ Groq Rate Limit для {group_data.get('name')}: {e}")
            return {"telegram_id": group_data.get("telegram_id"), "category": None, "success": False, "error": str(e)}
        except openai.NotFoundError as e:
            logger.error(f"⚠️ Модель AI недоступна {self.model} для {group_data.get('name')}: {e}")
            return {"telegram_id": group_data.get("telegram_id"), "category": None, "success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"⚠️ Ошибка AI для {group_data.get('name')}: {type(e).__name__}: {e}")
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
        model = choosing_random_ai_model()
        logger.debug(
            f"Выбранная модель: {model} для дальнейшего формирования ответа названий групп и каналов для последующего поиска в Telegram.")

        chat_completion = await client_groq.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": f"Придумай 30 коротких вариаций названий и ключевых слов для поиска Telegram-групп по теме: {user_input}. Ответ дай СТРОГО по одному названию на каждой новой строке (в столбик). Не используй нумерацию, заголовки, категории и запятые."
                }
            ],
        )
        logger.debug(f"Полный ответ от Groq: {chat_completion}")
        raw_ans = chat_completion.choices[0].message.content or ""
        # Очищаем ответ от блока рассуждений <think>...</think>, если модель вернула мыслительный процесс
        cleaned_ans = re.sub(r'<think>.*?</think>', '', raw_ans, flags=re.DOTALL).strip()
        cleaned_ans = re.sub(r'</?think>', '', cleaned_ans).strip()
        return cleaned_ans

    except groq.RateLimitError:
        logger.error(f"Привышены лимиты запросов к Groq API на модель {model}")
        # TODO добавить отправку сообщения администратору бота

    except groq.AuthenticationError:
        if GROQ_API_KEY:
            logger.error("Ошибка аутентификации с ключом Groq API.")
        else:
            logger.error("API ключ Groq API не установлен.")
        return ""
    except groq.NotFoundError as e:
        logger.error(e)  # Ошибка аутентификации с ключом Groq API, Возможно нужно сменить модель ИИ
        await bot.send_message(
            chat_id=int(ADMIN_USER_ID),  # ID Администратора бота
            text=f"Ошибка аутентификации с ключом Groq API: {e}"
        )
        return ""
    except Exception as e:
        logger.exception(e)
        return ""


async def search_groups_in_telegram(client, group_names):
    """
    Асинхронно ищет публичные группы и каналы в Telegram по списку названий.
    При заморозке аккаунта сразу прекращает весь поиск.
    Проверяет дату последнего сообщения и обновляет поле availability в БД.

    :param client: Объект клиента Telethon.
    :param group_names: Список названий групп.
    :return: Список найденных групп.
    """

    Category_Assignment = CategoryAssignment()

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
                logger.exception(f"Не удалось подключить клиента: {e}")
                break

        try:
            search_results = await client(functions.contacts.SearchRequest(q=name, limit=20))

            for chat in search_results.chats:
                if not hasattr(chat, 'title') or not chat.title:
                    continue

                # Получем данные группы / канала найденного в поиске Telegram
                telegram_id = chat.id  # ID группы / канала
                group_hash = getattr(chat, 'access_hash', None)  # Хеш группы / канала
                title = chat.title  # Название группы / канала
                username = f"@{chat.username}" if getattr(chat, 'username', None) else None  # Имя группы / канала
                link = f"https://t.me/{chat.username}" if username else None  # Ссылка на группу / канал
                participants = getattr(chat, 'participants_count', 0)  # Количество участников группы / канала
                description = getattr(chat, 'description', '')  # Описание группы / канала
                group_type = determine_telegram_chat_type(entity=chat)  # Тип группы / канала

                # Создаем словарь с данными группы / канала
                group_data = {
                    "name": title,
                    "description": description,
                    "username": username,
                    "group_type": group_type,
                    "telegram_id": telegram_id,
                }

                # Проверяем, существует ли уже группа
                existing_group = TelegramGroup.get_or_none(
                    (TelegramGroup.telegram_id == telegram_id) |
                    (TelegramGroup.group_hash == group_hash)
                )
                if existing_group:
                    logger.warning(f"Группа {title} {username} уже существует в базе данных")

                    # 1. Если язык в БД у существующей группы не определён — определяем и обновляем запись
                    if not existing_group.language or existing_group.language.strip() in ('', 'unknown', 'none'):
                        logger.info(f"Язык группы {title} {username} не определён в БД, определяем...")
                        try:
                            detector = LanguageDetectorBuilder.from_all_spoken_languages().build()
                            res = detector.detect_language_of(title)
                            if res is not None:
                                code = res.iso_code_639_1.name.lower()
                                if code in ISO_639_1_CODES:
                                    existing_group.language = code
                                    existing_group.save()
                                    logger.info(f"✅ Обновлён язык для существующей группы {title} {username}: {code}")
                        except Exception as e:
                            logger.warning(f"Ошибка определения языка для существующей группы '{title}': {e}")
                    else:
                        logger.info(f"Язык группы {title} {username} уже определён в БД: {existing_group.language}")

                    # 2. Если категория в БД у существующей группы не определена — определяем через AI и обновляем запись
                    if not existing_group.category or existing_group.category.strip() in ('', 'none', 'не определена'):
                        logger.info(f"Категория группы {title} {username} не определена в БД, определяем через AI...")
                        # try:

                        res_cat = await Category_Assignment.category_assignment(
                            group_data=group_data,
                        )
                        if res_cat.get("success") and res_cat.get("category"):
                            cat_lower = res_cat["category"].lower()
                            existing_group.category = cat_lower
                            existing_group.save()
                            logger.info(f"✅ Доопределена и обновлена категория в БД для {title}: {cat_lower}")
                        # except Exception as e:
                        #     logger.warning(f"Ошибка определения категории для существующей группы '{title}': {e}")
                    else:
                        logger.info(
                            f"Категория группы {title} {username} уже определена в БД: {existing_group.category}")

                    continue

                # Инициализация локальных переменных для новой группы
                lang_code = ''
                last_message_date = None
                # availability = 'unknown'

                """
                Определение языка группы / канала (для новой группы — 100%)
                """
                logger.info(f"Найдена новая группа {title} {username}, определяем язык")
                try:
                    detector = LanguageDetectorBuilder.from_all_spoken_languages().build()
                    text = title
                    result = detector.detect_language_of(text)

                    if result is not None:
                        detected_lang = result.iso_code_639_1.name.lower()
                        if detected_lang in ISO_639_1_CODES:
                            lang_code = detected_lang
                            logger.info(f"✅ {title} → язык: {lang_code}")
                        else:
                            logger.warning(f"Язык {detected_lang} не найден в списке ISO_639_1")
                    else:
                        logger.warning(f"Язык для группы {title} {username} не определён")
                except Exception as e:
                    logger.warning(f"Ошибка определения языка для '{title}': {e}")

                """
                Определение категории группы / канала
                """
                logger.info(f"Найдена группа {title} {username}, определяем категорию")

                # try:
                # group_data = {
                #     "name": title,
                #     "description": getattr(chat, 'description', ''),
                #     "username": username,
                #     "group_type": group_type,
                #     "telegram_id": telegram_id,
                # }
                result = await Category_Assignment.category_assignment(
                    group_data=group_data,
                )
                # except openai.BadRequestError as e:
                #     logger.error(f"Не подходящая модель AI: {e}")

                category_lower = ''
                if result.get("success") and result.get("category"):
                    category_lower = result["category"].lower()
                    logger.info(f"✅ {title} {username} → {category_lower}")
                else:
                    logger.warning(f"❌ {title} {username} — AI не определил")

                # ========== Проверка даты последнего сообщения ==========
                try:
                    messages = await client.get_messages(chat.id, limit=1)
                    if messages and len(messages) > 0:
                        last_message = messages[0]
                        last_message_date = last_message.date
                        logger.debug(f"📅 Последнее сообщение в '{title}': {last_message_date}")

                        last_message_naive = last_message_date.replace(tzinfo=None)
                        days_since_last_message = (datetime.now() - last_message_naive).days

                        if days_since_last_message <= 30:
                            availability = 'active'
                        else:
                            availability = 'inactive'
                    else:
                        availability = 'inactive'
                        logger.warning(f"⚠️ В группе '{title}' нет сообщений")

                except Exception as e:
                    logger.exception(f"Не удалось получить дату последнего сообщения для '{title}': {e}")
                    availability = 'unknown'

                # Сохранение в базу данных data/bot.db, таблица telegram_groups
                try:
                    TelegramGroup.create(
                        telegram_id=telegram_id,
                        group_hash=group_hash,
                        name=title,
                        username=username,
                        description=description,
                        participants=participants,
                        category=category_lower,
                        group_type=group_type,
                        language=lang_code,
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
                    'category': category_lower,
                    'group_type': group_type,
                    'language': lang_code,
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
                logger.exception("Клиент отключён. Прекращаем поиск.")
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
