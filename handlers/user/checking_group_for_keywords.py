# -*- coding: utf-8 -*-
import asyncio

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger  # https://github.com/Delgan/loguru
from telethon import TelegramClient
from telethon.sessions import StringSession

from account_manager.auth import CheckingAccountsValidity
from account_manager.subscription import subscription_telegram
from keyboards.user.keyboards import back_keyboard
from states.states import MyStatesParsing
from system.dispatcher import api_id, api_hash
from system.dispatcher import router


@router.message(F.text == "🔍 Проверка группы на наличие ключевых слов")
async def checking_group_for_keywords(message: Message, state: FSMContext):
    """
    Обработчик команды "🔍 Проверка группы на наличие ключевых слов".

    Принимает данные от пользователи и начинает процесс проверки группы на наличие ключевых слов.

    :param message: (Message) Объект входящего сообщения от пользователя.
    :param state: (FSMContext) Контекст машины состояний, используется для сброса текущего состояния.
    :return: None
    """
    await state.clear()  # Завершаем текущее состояние машины состояния
    await message.answer(
        text=("🔍 Введите ссылку на группу или канал для поиска ключевых слов.\n\n"
              "📌 Пример: <code>https://t.me/example_group</code> или <code>@example_channel</code>"),
        reply_markup=back_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(MyStatesParsing.get_url)


@router.message(MyStatesParsing.get_url)
async def get_url(message: Message, state: FSMContext):
    """
    Обработчик команды "Получить URL".
    :param message:
    :param state:
    :return: None
    """
    await state.update_data(url=message.text.strip())  # Сохраняем URL в контекст данных
    await message.answer(
        text=("✍️ Введите ключевое слово для поиска в сообщениях.\n\n"
              "📌 Пример: <code>Работа в Москве</code> или <code>ищу дизайнера</code>\n\n"
              "❗️Важно: Не указывайте слишком короткие или множественные слова (например: <code>работа, Москва, дизайн</code>).\n"
              "Бот ищет точные совпадения — лучше использовать фразу целиком."),
        reply_markup=back_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(MyStatesParsing.get_keyword)


@router.message(MyStatesParsing.get_keyword)
async def get_keyword(message: Message, state: FSMContext):
    """
    J
    :param message:
    :param state:
    :return:
    """
    keyword = message.text.strip()  # Получаем ключевое слово из сообщения
    await message.answer(
        text=("✅ Данные успешно получены!\n\n"
              "🔍 Начинаю поиск сообщений по указанной группе и ключевому слову…\n\n"
              "⏳ Пожалуйста, ожидайте — процесс может занять некоторое время."),
        reply_markup=back_keyboard()
    )
    await state.update_data(keyword=keyword)
    data = await state.get_data()  # Получаем данные из контекста состояния
    await state.clear()  # Завершаем текущее состояние машины состояния
    logger.info(f"Полученые данные от пользователя: ссылка {data.get("url")}, ключевое слово: {data.get('keyword')}")
    await parse_group_for_keywords(url=data.get("url"), keyword=data.get("keyword"), message=message)


async def create_client_from_session(session_path: str, api_id: int, api_hash: str):
    """
    Создаёт подключённого TelegramClient, используя session-файл,
    затем переходит на StringSession для безопасного хранения в памяти.

    :param session_path: Путь к .session файлу
    :param api_id: API ID от Telegram
    :param api_hash: API Hash от Telegram
    :return: Подключённый клиент TelegramClient
    """

    # Создаём клиент из файла сессии
    client = TelegramClient(
        session_path, api_id, api_hash,
        system_version="4.16.30-vxCUSTOM"
    )
    await client.connect()

    # Сохраняем данные сессии в строку (StringSession)
    session_string = StringSession.save(client.session)

    # Отключаемся от первого клиента (можно освободить ресурсы при необходимости)
    await client.disconnect()

    # Создаём новый клиент на основе StringSession (без сохранения на диск)
    client = TelegramClient(
        StringSession(session_string),
        api_id=api_id,
        api_hash=api_hash,
        system_version="4.16.30-vxCUSTOM"
    )

    await client.connect()
    await asyncio.sleep(1)  # Даём время на стабильное подключение

    return client


async def parse_group_for_keywords(url, keyword, message: Message):
    """
    Парсит группу на наличие ключевых слов.
    :param url:
    :param keyword:
    :param message: (telegram.Message) Объект сообщения, отправленный пользователем.
    :return:
    """
    try:
        user_id = message.from_user.id  # Получаем ID пользователя

        checking_accounts_validity = CheckingAccountsValidity(message=message, path="accounts/parsing_grup")
        await checking_accounts_validity.checking_accounts_for_validity()
        available_sessions = await checking_accounts_validity.get_available_sessions()

        # Подключаемся к текущему аккаунту
        logger.info(f"Подключаемся к сессии: {f'accounts/parsing_grup/{available_sessions[0]}'}")
        client = await create_client_from_session(
            session_path=f'accounts/parsing_grup/{available_sessions[0]}',
            api_id=api_id,
            api_hash=api_hash
        )
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
                    logger.info(f"📌 Найдено совпадение. Пересылаю сообщение ID={msg.telegram_id}")

                    # Получаем дату сообщения
                    msg_date = msg.date.strftime("%d.%m.%Y %H:%M:%S") if msg.date else "Неизвестно"

                    # Получаем информацию о чате-источнике
                    try:
                        chat_entity = await client.get_entity(url)
                        chat_title = getattr(chat_entity, "title", None) or getattr(chat_entity, "username",
                                                                                    None) or "Неизвестно"
                        chat_id = chat_entity.id
                    except Exception as e:
                        logger.warning(f"Не удалось получить название чата: {e}")
                        chat_title = "Неизвестно"
                        chat_id = None

                    # Формируем ссылку на сообщение
                    # Для чатов с username (если есть)
                    if chat_id:
                        try:
                            # Для супергрупп/каналов (chat_id начинается с -100)
                            if str(chat_id).startswith("-100"):
                                # Удаляем префикс -100 и получаем чистый ID
                                clean_chat_id = str(chat_id)[4:]
                                message_link = f"https://t.me/c/{clean_chat_id}/{msg.telegram_id}"
                            elif hasattr(chat_entity, 'username') and chat_entity.username:
                                message_link = f"https://t.me/{chat_entity.username}/{msg.telegram_id}"
                        except Exception as e:
                            logger.warning(f"Не удалось создать ссылку на сообщение: {e}")

                    # Формируем итоговое сообщение с контекстом
                    # Обрезаем текст если он слишком длинный
                    display_text = text if len(text) <= 500 else text[:500] + "..."

                    # Отправляем в целевую группу
                    await message.answer(
                        text=(f"📥 <b>Новое сообщение</b>\n\n"
                              f"<b>Источник:</b> {chat_title}\n"
                              f"<b>Дата:</b> {msg_date}\n"
                              f"<b>Ссылка:</b> <a href='{message_link}'>Перейти к сообщению</a>\n\n"
                              f"<b>Текст сообщения:</b>\n{display_text}"),
                        parse_mode="HTML"
                    )
                    logger.info(f"✅ Сообщение переслано в целевую группу (ID={user_id})")

                await asyncio.sleep(0.4)

            await message.answer(
                text=(f"🔍 Поиск завершён:\n"
                      f"Проверено сообщений: {count}\n"
                      f"Совпадений с '{keyword}': {matched_count}")
            )
        except ValueError:
            logger.warning("❌ Не удалось найти группу или канал. Возможно не подходящий гео аккаунта.")
        except Exception as e:
            logger.exception(f"❌ Ошибка при парсинге группы: {e}")
            await message.answer("❌ Произошла ошибка при парсинге группы. Проверьте ссылку и доступ к чату.")
        finally:
            await client.disconnect()
    except Exception as e:
        logger.exception(e)


def register_handlers_checking_group_for_keywords():
    """Регистрирует обработчики для проверки группы на наличие ключевых слов."""
    router.message.register(checking_group_for_keywords, F.text == "🔍 Проверка группы на наличие ключевых слов")
