import os
from pprint import pprint
from time import sleep
import json
import asyncio
import logging
from http import HTTPStatus

import requests
import aiohttp
from telebot import TeleBot, types
import threading

from parse_data import parser
from get_random_card import get_random_card
from settings import (ALLOWED_USERS, TELEGRAM_TOKEN,)


parse_lock = threading.Lock()


def send_message(bot, message, user_id, menu=None):

    """Отправляет сообщение в Telegram-чат."""

    try:
        bot.send_message(user_id, message, parse_mode="html", reply_markup=menu)
        logger.debug('Сообщение успешно отправлено')
    except Exception as error:
        logger.error(f'Сообщение не отправлено: {error}')


def is_user_allowed(user_id):
    return user_id in ALLOWED_USERS.split(', ')


def create_menu():
    # Создаем объект клавиатуры
    keyboard = types.InlineKeyboardMarkup()

    # Добавляем кнопки к клавиатуре
    start_button = types.InlineKeyboardButton(
        text="Старт", callback_data="start"
    )
    get_card_button = types.InlineKeyboardButton(
        text="Отправить карточку",
        callback_data="get_card"
    )
    parse_data_button = types.InlineKeyboardButton(
        text="Собрать данные",
        callback_data="parse_data"
    )

    # Добавляем кнопки в клавиатуру (в один ряд)
    keyboard.add(get_card_button)
    keyboard.row(start_button, parse_data_button)

    # Можно также добавлять кнопки в несколько рядов:
    # keyboard.row(button1, button2)
    # keyboard.add(button3)

    return keyboard


def main():
    bot = TeleBot(token=TELEGRAM_TOKEN)

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        message_for_allowed_users = (
            '<b>Добро пожаловать!</b>\n'
            '\n'
            '/start - запуск бота.\n'
            '\n'
            '/parse_data - запустить сбор данных.\n'
            '\n'
            '/get_card - получить рандомную карточку.')
        message_for_any_users = 'Извините, у вас нет доступа к этому боту.'
        user_id = str(message.chat.id)
        menu = create_menu()
        if is_user_allowed(user_id):
            send_message(bot, message_for_allowed_users, user_id, menu)
        else:
            send_message(bot, message_for_any_users, user_id)

    @bot.message_handler(commands=['parse_data'])
    def parse_new_data(message):
        message_for_allowed_users = ('Идет процесс сбора данных...'
                                     'Это может занять несколько минут.')
        message_for_any_users = ('Команда не существует')
        massege_parse_data_complete = 'Данные успешно собраны'
        massege_parse_data_error = 'Данные не собраны'
        user_id = str(message.chat.id)
        if is_user_allowed(user_id):
            send_message(bot, message_for_allowed_users, user_id)
            try:
                with parse_lock:
                    parser()
                    logger.debug('Данные успешно собраны.')
            except Exception as error:
                logger.error(f'{massege_parse_data_error}: {error}')
                send_message(bot, massege_parse_data_error, user_id)
            else:
                send_message(bot, massege_parse_data_complete, user_id)
        else:
            send_message(bot, message_for_any_users, user_id)

    @bot.message_handler(commands=['get_card'])
    def get_card(message):
        message_for_any_users = ('Команда не существует')
        massege_parse_data_error = 'Произошла ошибка...('
        user_id = str(message.chat.id)
        menu = create_menu()
        if is_user_allowed(user_id):
            try:
                send_message(bot, get_random_card(), user_id, menu)
            except Exception as error:
                logger.error(f'{massege_parse_data_error}: {error}')
                send_message(bot, massege_parse_data_error, user_id)
        else:
            send_message(bot, message_for_any_users, user_id)

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        user_id = str(message.chat.id)
        if is_user_allowed(user_id):
            bot.reply_to(message, "Бот пока не умеет общаться, используйте команды.")
        else:
            bot.reply_to(message, "Извините, у вас нет доступа к этому боту.")

    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(call):
        if call.data == "start":
            bot.answer_callback_query(call.id)
            send_welcome(call.message)
        elif call.data == "get_card":
            bot.answer_callback_query(call.id)
            get_card(call.message)
        elif call.data == "parse_data":
            bot.answer_callback_query(call.id)
            if parse_lock.locked():
                bot.send_message(
                    call.message.chat.id,
                    "Процесс парсинга уже запущен, пожалуйста, подождите."
                )
            else:
                threading.Thread(
                    target=parse_new_data,
                    args=(call.message,), daemon=True
                ).start()

    # bot.polling(interval=3, timeout=20)
    bot_thread = threading.Thread(
        target=bot.polling(interval=3, timeout=20),
        args=(bot,), daemon=True
    )
    bot_thread.start()


if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s, %(levelname)s, %(message)s, %(name)s'
    LOG_FORMATER = logging.Formatter(LOG_FORMAT)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(
        'main.log',
        mode='a',
        encoding='utf-8'
    )
    file_handler.setFormatter(LOG_FORMATER)

    logger.addHandler(file_handler)
    main()
