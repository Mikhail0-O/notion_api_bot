import os
from pprint import pprint
from time import sleep
import json
import asyncio

from dotenv import load_dotenv
import requests
import aiohttp


load_dotenv()


NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABSE_ID')
HEADERS = {'Authorization': f'Bearer {NOTION_TOKEN}',
           'Notion-Version': '2022-06-28'}
# ENDPOINT = f"https://api.notion.com/v1/blocks/{NOTION_DATABASE_ID}/children"
# response = requests.get(ENDPOINT, headers=HEADERS)

# with open('db.json', 'w', encoding='utf8') as f:
#     json.dump(response.json(), f, ensure_ascii=False, indent=4)


async def get_api_response(session, block_id, retries=5, delay=1):
    """Запрашиваем потомков блока по id."""
    endpoint = f"https://api.notion.com/v1/blocks/{block_id}/children"
    for attempt in range(retries):
        try:
            async with session.get(endpoint, headers=HEADERS) as response:
                if response.status == 429:
                    retry_after = int(response.headers.get(
                        'Повтор через:', delay))
                    await asyncio.sleep(retry_after)
                    return await response.json()
                else:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as error:
            print(f"Попытка: {attempt + 1} failed: {error}")
            await asyncio.sleep(delay * (2 ** attempt))


def get_results(response, stack_id, stack_content):
    """Обработка результатов запроса."""
    results = response.get('results')
    for result in results:
        if result.get('child_page'):
            stack_id.append(result.get('id'))
        if result.get('callout'):
            callout = result.get('callout')
            rich_text = callout.get('rich_text')
            content = ''.join(i['text']['content'] for i in rich_text)
            stack_content.append(content)


async def main():
    stack_id = [NOTION_DATABASE_ID]
    stack_content: list = []
    async with aiohttp.ClientSession() as session:
        while stack_id:
            pprint(stack_id)
            block_id = stack_id.pop(0)
            response = await get_api_response(session, block_id)
            get_results(response, stack_id, stack_content)

    print(stack_content)


if __name__ == '__main__':
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