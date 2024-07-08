from time import time
import json
import asyncio
from http import HTTPStatus
from itertools import count

import aiohttp

from settings import (NOTION_DATABASE_ID,
                      HEADERS, logger)


autoincrement = count(start=1)


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
    flag_code = False

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
            card_number = next(autoincrement)
            data.update(card_number=card_number)
            current_title_index = next(
                i for i, parent_list in enumerate(parent)
                if parent_list[-1] == result.get('parent').get('page_id')
            )

            title = ' --> '.join(titles[current_title_index])
            data.update(title=title)

            callout = result.get('callout')
            rich_text = callout.get('rich_text', [])
            content = ''.join(i['text']['content'] for i in rich_text)

            data.update(text=content)

            URL = (f"https://www.notion.so/"
                   f"{parent[current_title_index][-1].replace('-', '')}/")

            content_code = None

            data.update(code=content_code)
            data.update(URL=URL)

            all_data.append(data)
            if content[-1] == ':':
                flag_code = True
                continue

        if flag_code:
            flag_code = False
            code = result.get('code')
            if code:
                rich_text = code.get('rich_text', [])
                content_code = ''.join(i['text']['content'] for i in rich_text)
                del all_data[-1]['code']
                all_data[-1].update(code=content_code)
                URL = (f"https://www.notion.so/"
                       f"{parent[current_title_index][-1].replace('-', '')}/")
                del all_data[-1]['URL']
                all_data[-1].update(URL=URL)


async def get_data():
    stack_id = [NOTION_DATABASE_ID]
    all_data = []
    parent = []
    titles = []
    async with aiohttp.ClientSession() as session:
        while stack_id:
            print(stack_id)
            block_id = stack_id.pop(0)
            response = await get_api_response(session, block_id)
            get_results(response, stack_id, all_data, parent, titles)

    with open('db.json', 'w', encoding='utf8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)


def parser():
    asyncio.run(get_data())
    logger.debug('Данные успешно собраны.')


if __name__ == "__main__":
    start = time()
    parser()
    logger.debug('Данные успешно собраны.')
    finish = time()
    logger.debug(finish - start)
