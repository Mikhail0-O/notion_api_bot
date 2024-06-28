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


def get_api_response(block_id):
    """Запрашиваем потомков блока по id."""
    endpoint = f"https://api.notion.com/v1/blocks/{block_id}/children"
    try:
        response = requests.get(endpoint, headers=HEADERS)
        return response.json()
    except requests.RequestException as error:
        print(error)


def get_results(response):
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


stack_id = [NOTION_DATABASE_ID]
stack_content: list = []
while stack_id:
    pprint(stack_id)
    sleep(0.5)
    if stack_id:
        current_page_response = get_api_response(stack_id.pop(0))
    get_results(current_page_response)
print(stack_content)



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