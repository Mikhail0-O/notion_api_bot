import json
import asyncio
import logging
from http import HTTPStatus
from time import time

import aiohttp

from settings import NOTION_DATABASE_ID, HEADERS

# Настройка логгера
LOG_FORMAT = '%(asctime)s, %(levelname)s, %(message)s, %(name)s'
logging.basicConfig(filename='main.log', level=logging.DEBUG, format=LOG_FORMAT, encoding='utf-8')
logger = logging.getLogger(__name__)


async def get_api_response(session, block_id, delay=1):
    """Запрашиваем потомков блока по id."""
    endpoint = f"https://api.notion.com/v1/blocks/{block_id}/children"
    attempt = 0
    while True:
        try:
            async with session.get(endpoint, headers=HEADERS) as response:
                if response.status == HTTPStatus.OK:
                    return await response.json()
                elif response.status in {HTTPStatus.TOO_MANY_REQUESTS, HTTPStatus.SERVICE_UNAVAILABLE}:
                    retry_after = int(response.headers.get('Retry-After', delay))
                    logger.error(f'Ошибка сервера. Статус ответа: {response.status}, Повторный запрос через: {retry_after} сек')
                    await asyncio.sleep(retry_after)
                else:
                    response.raise_for_status()
        except aiohttp.ClientError as error:
            attempt += 1
            logger.error(f'Ошибка: {error}. Попытка: {attempt}. Повторный запрос через: {delay * (2 ** attempt)} сек')
            await asyncio.sleep(delay * (2 ** attempt))


def get_results(response, stack_id, all_data, parent, titles):
    """Обработка результатов запроса."""
    results = response.get('results', [])

    for result in results:
        data = {}
        if child_page := result.get('child_page'):
            parent_id = result.get('parent', {}).get('database_id') or result.get('parent', {}).get('page_id')
            child_id = result.get('id')
            child_title = child_page.get('title')

            if parent_id:
                found = False
                for i, parent_list in enumerate(parent):
                    if parent_list[-1] == parent_id:
                        parent[i].append(child_id)
                        titles[i].append(child_title)
                        found = True
                        break
                if not found:
                    new_parent_entry = [parent_id, child_id]
                    new_titles_entry = [child_title]
                    for i, parent_list in enumerate(parent):
                        if parent_list[-1] == parent_id or parent_list[-2] == parent_id:
                            parent.append(parent_list[:-1] + [child_id])
                            titles.append(titles[i][:-1] + [child_title])
                            found = True
                            break
                    if not found:
                        parent.append(new_parent_entry)
                        titles.append(new_titles_entry)

            stack_id.append(child_id)

        if callout := result.get('callout'):
            current_title_index = next(i for i, parent_list in enumerate(parent) if parent_list[-1] == result.get('parent').get('page_id'))
            data['title'] = ' --> '.join(titles[current_title_index])
            data['text'] = ''.join(rt['text']['content'] for rt in callout.get('rich_text', []))
            data['URL'] = f"https://www.notion.so/{parent[current_title_index][-1].replace('-', '')}/"
            all_data.append(data)


async def get_data():
    stack_id = [NOTION_DATABASE_ID]
    all_data = []
    parent = []
    titles = []
    async with aiohttp.ClientSession() as session:
        while stack_id:
            block_id = stack_id.pop(0)
            response = await get_api_response(session, block_id)
            get_results(response, stack_id, all_data, parent, titles)
    with open('db.json', 'w', encoding='utf8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)


def parser():
    asyncio.run(get_data())


if __name__ == '__main__':
    start = time()
    parser()
    logger.debug('Данные успешно собраны.')
    logger.debug(f'Время выполнения: {time() - start} секунд.')
