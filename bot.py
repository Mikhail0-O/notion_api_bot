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


load_dotenv()


NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
HEADERS = {'Authorization': f'Bearer {NOTION_TOKEN}',
           'Notion-Version': '2022-06-28'}
# ENDPOINT = f"https://api.notion.com/v1/blocks/{NOTION_DATABASE_ID}/children"
# response = requests.get(ENDPOINT, headers=HEADERS)

# with open('db.json', 'w', encoding='utf8') as f:
#     json.dump(response.json(), f, ensure_ascii=False, indent=4)


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


# def get_results(response, stack_id, all_data, parent):
#     """Обработка результатов запроса."""
#     results = response.get('results')
#     for result in results:
#         data = {}
#         if result.get('child_page'):
#             if result.get('parent').get('database_id'):
#                 parent.append([result.get('parent').get('database_id'), result.get('id')])
#                 # for i in parent:
#                 #     if result.get('parent').get('database_id') == i[-1]:
#                 #         i.append(result.get('id'))
#             else:
#                 # parent.append([result.get('parent').get('database_id'), result.get('id')])
#                 for i in parent:
#                     # parent.append([result.get('parent').get('database_id'), result.get('id')])
#                     if result.get('parent').get('page_id') == i[-1]:
#                         i.append(result.get('id'))
#                     else:
#                         parent_i = []
#                         for j in i:
#                             parent_i.append(j)
#                             if result.get('parent').get('page_id') == j:
#                                 parent_i.append(result.get('parent').get('page_id'))
#                                 parent.append(parent_i)
#             # print(result.get('child_page').get('title'))
#             # parent.append(result.get('child_page').get('title'))
#             stack_id.append(result.get('id'))
#         if result.get('callout'):
#             # title = '->'.join(parent)
#             # print(parent)
#             # parent = []
#             callout = result.get('callout')
#             rich_text = callout.get('rich_text')
#             content = ''.join(i['text']['content'] for i in rich_text)
#             data.update(text=content)
#             all_data.append(data)
#             # stack_content.append(content)

def get_results(response, stack_id, all_data, parent, titles):
    """Обработка результатов запроса."""
    results = response.get('results', [])

    for result in results:
        data = {}

        # Обработка дочерней страницы
        if result.get('child_page'):
            parent_id = result.get('parent', {}).get('database_id') or result.get('parent', {}).get('page_id')
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
                    new_titles_entry = ['Конспект', child_title]
                    for i in range(len(parent)):
                        if parent[i][-1] == parent_id or parent[i][-2] == parent_id:
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

        # Обработка callout
        if result.get('callout'):
            callout = result.get('callout')
            rich_text = callout.get('rich_text', [])
            content = ''.join(i['text']['content'] for i in rich_text)
            data.update(text=content)
            all_data.append(data)


async def main():
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

    print(all_data)
    pprint(parent)
    pprint(titles)
    logger.debug('Данные успешно собраны')


if __name__ == '__main__':
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
    asyncio.get_event_loop().run_until_complete(main())


# Пример ответа
# {
#       "object": "block",
#       "id": "92caa944-00a7-4e91-860a-5de4b59f20ec",
#       "parent": {
#         "type": "database_id",
#         "database_id": "67e8d4a3-c141-440a-98ea-d7b0a474905d"
#       },
#       "created_time": "2024-02-04T19:18:00.000Z",
#       "last_edited_time": "2024-06-26T16:05:00.000Z",
#       "created_by": {
#         "object": "user",
#         "id": "0d6c3117-661e-4680-9397-1a01a6d1557c"
#       },
#       "last_edited_by": {
#         "object": "user",
#         "id": "0d6c3117-661e-4680-9397-1a01a6d1557c"
#       },
#       "has_children": true,
#       "archived": false,
#       "in_trash": false,
#       "type": "child_page",
#       "child_page": {
#         "title": "Python"
#       }
# },