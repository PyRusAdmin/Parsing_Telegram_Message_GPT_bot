import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger

from account_manager.auth import CheckingAccountsValidity
from account_manager.subscription import subscription_telegram
from database.database import User
from keyboards.user.keyboards import back_keyboard
from locales.locales import t
from states.states import MyStatesParsing

router = Router(name=__name__)


@router.message(
    (F.text == t('check_group_for_keywords_button', 'ru')) | (F.text == t('check_group_for_keywords_button', 'en')))
async def checking_group_for_keywords(message: Message, state: FSMContext):
    """
    Обработчик команды "Проверка группы на наличие ключевых слов".

    Принимает данные от пользователи и начинает процесс проверки группы на наличие ключевых слов.

    :param message: (Message) Объект входящего сообщения от пользователя.
    :param state: (FSMContext) Контекст машины состояний, используется для сброса текущего состояния.
    """
    await state.clear()  # Завершаем текущее состояние машины состояния
    user = User.get(User.user_id == message.from_user.id)
    await message.answer(
        text=t("check_group_ask_url", lang=user.language),
        reply_markup=back_keyboard(lang=user.language),
        parse_mode="HTML"
    )
    await state.set_state(MyStatesParsing.get_url)


@router.message(MyStatesParsing.get_url)
async def get_url(message: Message, state: FSMContext):
    """
    Обработчик команды "Получить URL".
    :param message: (Message) Объект входящего сообщения от пользователя.
    :param state: (FSMContext) Контекст машины состояний, используется для получения данных и сброса текущего состояния.
    """
    await state.update_data(url=message.text.strip())  # Сохраняем URL в контекст данных
    user = User.get(User.user_id == message.from_user.id)
    await message.answer(
        text=t("check_group_ask_keyword", lang=user.language),
        reply_markup=back_keyboard(lang=user.language),
        parse_mode="HTML"
    )
    await state.set_state(MyStatesParsing.get_keyword)


@router.message(MyStatesParsing.get_keyword)
async def get_keyword(message: Message, state: FSMContext):
    """
    Обработчик команды "Получить ключевое слово".
    :param message: (Message) Объект входящего сообщения от пользователя.
    :param state: (FSMContext) Контекст машины состояний, используется для получения данных и сброса текущего состояния.
    """
    keyword = message.text.strip()  # Получаем ключевое слово из сообщения
    user = User.get(User.user_id == message.from_user.id)
    await message.answer(
        text=t("check_group_started", lang=user.language),
        reply_markup=back_keyboard(lang=user.language)
    )
    await state.update_data(keyword=keyword)
    data = await state.get_data()  # Получаем данные из контекста состояния
    await state.clear()  # Завершаем текущее состояние машины состояния
    logger.info(f"Полученые данные от пользователя: ссылка {data.get('url')}, ключевое слово: {data.get('keyword')}")
    await parse_group_for_keywords(url=data.get("url"), keyword=data.get("keyword"), message=message)


async def parse_group_for_keywords(url, keyword, message: Message):
    """
    Парсит группу на наличие ключевых слов.
    :param url: (str) Ссылка на группу в Telegram.
    :param keyword: (str) Ключевое слово для поиска.
    :param message: (telegram.Message) Объект сообщения, отправленный пользователем.
    """
    try:
        user_id = message.from_user.id  # Получаем ID пользователя
        user = User.get(User.user_id == message.from_user.id)

        # ✅ Создаем checker БЕЗ path (он не нужен для работы с БД)
        checker = CheckingAccountsValidity(message=message)  # path=None по умолчанию
        client = await checker.start_random_client()

        await subscription_telegram(client, url)

        try:
            # Определяем параметры для парсинга
            parse_kwargs = {
                'limit': 500,  # Количество последних сообщений для проверки
            }
            count = 0
            matched_count = 0

            # Итерируем сообщения
            async for msg in client.iter_messages(entity=url, **parse_kwargs):
                count += 1
                text = msg.message if msg.message else ""
                if text and keyword.lower() in text.lower():
                    matched_count += 1
                    logger.info(f"✅ Найдено сообщение с ключевым словом: '{keyword}' — {text.strip()}")

                    # ИСПРАВЛЕНО: используем msg.id вместо message.id
                    logger.info(f"📌 Найдено совпадение. Пересылаю сообщение ID={msg.id}")

                    # Получаем дату сообщения
                    msg_date = msg.date.strftime("%d.%m.%Y %H:%M:%S") if msg.date else "Неизвестно"

                    # Получаем информацию о чате-источнике
                    try:
                        chat_entity = await client.get_entity(url)
                        title = chat_entity.title or ""

                        chat_id = chat_entity.id
                    except Exception as e:
                        logger.warning(f"Не удалось получить название чата: {e}")
                        title = ""
                        chat_id = None

                    # Формируем ссылку на сообщение
                    message_link = None  # Инициализируем переменную
                    if chat_id:
                        try:
                            # Для супергрупп/каналов (chat_id начинается с -100)
                            if str(chat_id).startswith("-100"):
                                # Удаляем префикс -100 и получаем чистый ID
                                clean_chat_id = str(chat_id)[4:]
                                message_link = f"https://t.me/c/{clean_chat_id}/{msg.id}"
                            elif hasattr(chat_entity, 'username') and chat_entity.username:
                                message_link = f"https://t.me/{chat_entity.username}/{msg.id}"
                        except Exception as e:
                            logger.warning(f"Не удалось создать ссылку на сообщение: {e}")

                    # Формируем итоговое сообщение с контекстом
                    # Обрезаем текст если он слишком длинный
                    display_text = text if len(text) <= 500 else text[:500] + "..."

                    # Отправляем в целевую группу
                    if message_link:
                        await message.answer(
                            text=t(
                                "check_group_new_message_with_link",
                                lang=user.language,
                                title=title,
                                msg_date=msg_date,
                                message_link=message_link,
                                display_text=display_text
                            ),
                            parse_mode="HTML"
                        )
                    else:
                        await message.answer(
                            text=t(
                                "check_group_new_message_no_link",
                                lang=user.language,
                                title=title,
                                msg_date=msg_date,
                                display_text=display_text
                            ),
                            parse_mode="HTML"
                        )
                    logger.info(f"✅ Сообщение переслано в целевую группу (ID={user_id})")

                await asyncio.sleep(0.4)

            await message.answer(
                text=t(
                    "check_group_summary",
                    lang=user.language,
                    count=count,
                    keyword=keyword,
                    matched_count=matched_count
                )
            )
        except ValueError:
            logger.warning("❌ Не удалось найти группу или канал. Возможно не подходящий гео аккаунта.")
        except Exception as e:
            logger.exception(f"❌ Ошибка при парсинге группы: {e}")
            await message.answer(t("check_group_parse_error", lang=user.language))
        finally:
            if client is not None:
                await client.disconnect()
            else:
                logger.warning("Клиент не был создан или заблокирован")
    except Exception as e:
        logger.exception(e)
