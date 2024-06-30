import os
from pprint import pprint
from time import sleep
import json
import asyncio
import logging
from http import HTTPStatus

from dotenv import load_dotenv
import requests
import aiohttp
from telebot import TeleBot


load_dotenv()


ALLOWED_USERS = os.getenv('ALLOWED_USERS')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
HEADERS = {'Authorization': f'Bearer {NOTION_TOKEN}',
           'Notion-Version': '2022-06-28'}
RETRY_GET_DATA_PERIOD = 3600


async def get_api_response(session, block_id, delay=1):
    """Запрашиваем потомков блока по id."""
    endpoint = f"https://api.notion.com/v1/blocks/{block_id}/children"
    attempt = 0
    while True:
        try:
            async with session.get(endpoint, headers=HEADERS,
                                   raise_for_status=False) as response:
                if response.status == HTTPStatus.OK:
                    return await response.json()
                elif response.status in {HTTPStatus.TOO_MANY_REQUESTS,
                                         HTTPStatus.SERVICE_UNAVAILABLE}:
                    message = (f'Ошибка сервера. Статус ответа: '
                               f'{response.status}, '
                               f'Повторный запрос через: {delay} cек')
                    retry_after = int(response.headers.get(
                        'Retry-After', delay))
                    delay += 1
                    logger.error(message)
                    await asyncio.sleep(retry_after)
                response.raise_for_status()
        except aiohttp.ClientError as error:
            attempt = attempt + 1
            message = (f'Ошибка: {error}'
                       f'Попытка: {attempt} '
                       f'Повторный запрос через: {delay * (2 ** attempt)} сек')
            logger.error(message)
            await asyncio.sleep(delay * (2 ** attempt))


def get_results(response, stack_id, all_data, parent, titles):
    """Обработка результатов запроса."""
    results = response.get('results', [])

    for result in results:
        data = {}

        # Обработка дочерней страницы
        if result.get('child_page'):
            parent_id = (result.get('parent').get('database_id')
                         or result.get('parent').get('page_id'))
            child_id = result.get('id')
            child_title = result.get('child_page').get('title')

            if parent_id:
                found = False
                for i in range(len(parent)):
                    if parent[i][-1] == parent_id:
                        parent[i].append(child_id)
                        titles[i].append(child_title)
                        found = True
                        break

                if not found:
                    new_parent_entry = [parent_id, child_id]
                    new_titles_entry = [child_title]
                    for i in range(len(parent)):
                        if (parent[i][-1] == parent_id
                                or parent[i][-2] == parent_id):
                            new_parent_entry = parent[i][:-1] + [child_id]
                            new_titles_entry = titles[i][:-1] + [child_title]
                            parent.append(new_parent_entry)
                            titles.append(new_titles_entry)
                            found = True
                            break
                    if not found:
                        parent.append(new_parent_entry)
                        titles.append(new_titles_entry)

            stack_id.append(child_id)

        # Достаем content и title
        if result.get('callout'):
            current_title_index = next(
                i for i, parent_list in enumerate(parent)
                if parent_list[-1] == result.get('parent').get('page_id')
            )

            data.update(title=' --> '.join(titles[current_title_index]))

            callout = result.get('callout')
            rich_text = callout.get('rich_text', [])
            content = ''.join(i['text']['content'] for i in rich_text)
            data.update(text=content)

            URL = (f"https://www.notion.so/"
                   f"{parent[current_title_index][-1].replace('-', '')}/")
            data.update(URL=URL)

            all_data.append(data)


async def get_data():
    stack_id = [NOTION_DATABASE_ID]
    all_data = []
    parent = []
    titles = []
    async with aiohttp.ClientSession() as session:
        while stack_id:
            pprint(stack_id)
            block_id = stack_id.pop(0)
            response = await get_api_response(session, block_id)
            get_results(response, stack_id, all_data, parent, titles)

    with open('db.json', 'w', encoding='utf8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)


def parser():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # asyncio.get_event_loop().run_until_complete(get_data())
    loop.run_until_complete(get_data())
    loop.close()
    logger.debug(
        f'Данные успешно собраны. '
        f'Повтоорный сбор данных через {RETRY_GET_DATA_PERIOD} сек')


LOG_FORMAT = '%(asctime)s, %(levelname)s, %(message)s, %(name)s'
LOG_FORMATER = logging.Formatter(LOG_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stream_handler = logging.FileHandler(
    'main.log',
    mode='a',
    encoding='utf-8'
)
stream_handler.setFormatter(LOG_FORMATER)

logger.addHandler(stream_handler)
