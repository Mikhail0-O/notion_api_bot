import threading
import asyncio

from telebot import TeleBot, types

from parse_data import parse_data
from get_random_card import get_random_card
from settings import (ALLOWED_USERS, TELEGRAM_TOKEN, logger)
from refresh_db import refresh_db
from change_group import change_group


parse_lock = threading.Lock()


def send_message(bot, message, user_id, menu=None):

    """Отправляет сообщение в Telegram-чат."""

    try:
        bot.send_message(user_id,
                         message, parse_mode="HTML", reply_markup=menu)
        logger.debug('Сообщение успешно отправлено')
    except Exception as error:
        logger.error(f'Сообщение не отправлено: {error}')


def is_user_allowed(user_id):
    return user_id in ALLOWED_USERS.split(', ')


def create_menu(card_number=None):
    # Создаем объект клавиатуры
    keyboard = types.InlineKeyboardMarkup()

    # Добавляем кнопки к клавиатуре
    start_button = types.InlineKeyboardButton(
        text="Старт", callback_data="start"
    )
    get_card_button = types.InlineKeyboardButton(
        text="Получить карточку",
        callback_data="get_card"
    )
    parse_data_button = types.InlineKeyboardButton(
        text="Собрать данные",
        callback_data="parse_data"
    )
    if card_number is not None:
        change_group_1_button = types.InlineKeyboardButton(
            text="В группу 1",
            callback_data=f"change_on_group_1:{card_number}"
        )
        change_group_2_button = types.InlineKeyboardButton(
            text="В группу 2",
            callback_data=f"change_on_group_2:{card_number}"
        )
        change_group_3_button = types.InlineKeyboardButton(
            text="В группу 3",
            callback_data=f"change_on_group_3:{card_number}"
        )
        keyboard.add(get_card_button)
        keyboard.row(
            change_group_1_button,
            change_group_2_button,
            change_group_3_button
        )
        keyboard.row(start_button, parse_data_button)
    else:
        keyboard.add(get_card_button)
        keyboard.row(start_button, parse_data_button)

    return keyboard


def main():
    bot = TeleBot(token=TELEGRAM_TOKEN)

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        message_for_allowed_users = (
            '<b>Добро пожаловать!</b>\n\n'
            '/start - запуск бота.\n\n'
            '/parse_data - запустить сбор данных.\n\n'
            '/get_card - получить рандомную карточку.\n\n'
            'Для более удобной навигации используйте кнопки.')
        message_for_any_users = 'Извините, у вас нет доступа к этому боту.'
        user_id = str(message.chat.id)
        menu = create_menu()
        if is_user_allowed(user_id):
            send_message(
                bot, message_for_allowed_users, user_id, menu)
        else:
            send_message(bot, message_for_any_users, user_id)

    @bot.message_handler(commands=['parse_data'])
    def parse_new_data(message):
        message_for_allowed_users = ('Идет процесс сбора данных...'
                                     'Это может занять несколько секунд.')
        message_for_any_users = ('Команда не существует.')
        massege_parse_data_complete = 'Данные успешно собраны.'
        massege_parse_data_error = 'Данные не собраны.'
        user_id = str(message.chat.id)
        if is_user_allowed(user_id):
            send_message(
                bot, message_for_allowed_users, user_id)
            try:
                with parse_lock:
                    asyncio.run(parse_data())
                    refresh_db()
            except Exception as error:
                logger.error(f'{massege_parse_data_error}: {error}')
                send_message(bot, massege_parse_data_error, user_id)
            else:
                send_message(
                    bot, massege_parse_data_complete, user_id)
        else:
            send_message(
                bot, message_for_any_users, user_id)

    @bot.message_handler(commands=['get_card'])
    def get_card(message):
        message_for_any_users = ('Команда не существует.')
        massege_parse_data_error = 'Произошла ошибка...('
        user_id = str(message.chat.id)
        if is_user_allowed(user_id):
            try:
                card, card_number = get_random_card()
                menu = create_menu(card_number)
                send_message(bot, card, user_id, menu)
                return card_number
            except Exception as error:
                logger.error(f'{massege_parse_data_error}: {error}')
                send_message(bot, massege_parse_data_error, user_id)
        else:
            send_message(bot, message_for_any_users, user_id)

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        user_id = str(message.chat.id)
        message_not_dialog = (
            'Бот пока не умеет общаться, '
            'используйте команды.'
        )
        message_not_enter = ('Извините, у вас нет доступа к этому боту.')
        if is_user_allowed(user_id):
            bot.reply_to(message, message_not_dialog)
        else:
            bot.reply_to(message, message_not_enter)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(call):
        if call.data == "start":
            bot.answer_callback_query(call.id)
            send_welcome(call.message)
        elif call.data == "get_card":
            bot.answer_callback_query(call.id)
            card_number = get_card(call.message)
        elif call.data.startswith("change_on_group_1"):
            bot.answer_callback_query(call.id)
            card_number = call.data.split(":")[1]
            change_group(1, int(card_number))
        elif call.data.startswith("change_on_group_2"):
            bot.answer_callback_query(call.id)
            card_number = call.data.split(":")[1]
            change_group(2, int(card_number))
        elif call.data.startswith("change_on_group_3"):
            bot.answer_callback_query(call.id)
            card_number = call.data.split(":")[1]
            change_group(3, int(card_number))
        elif call.data == "parse_data":
            bot.answer_callback_query(call.id)
            if parse_lock.locked():
                message_locked_parse = (
                    'Процесс парсинга уже запущен,'
                    'пожалуйста, подождите.'
                )
                bot.send_message(
                    call.message.chat.id, message_locked_parse)
            else:
                threading.Thread(
                    target=parse_new_data,
                    args=(call.message,), daemon=True).start()

    bot.polling(interval=3, timeout=20)
    bot_thread = threading.Thread(
        target=bot.polling(
            interval=3, timeout=20), args=(bot,), daemon=True)
    bot_thread.start()


if __name__ == '__main__':
    main()
