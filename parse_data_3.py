import asyncio
import json

import requests

from settings import NOTION_DATABASE_ID, HEADERS


async def get_api_response(block_id):
    """Запрашиваем потомков блока по id."""
    endpoint = f"https://api.notion.com/v1/blocks/{block_id}/children"
    response = requests.get(endpoint, headers=HEADERS)
    return response.json()


async def get_results(response, stack_id, all_data, parent, titles):
    """Обработка результатов запроса."""
    results = response.get('results', [])

    for result in results:
        data = {}

        # Обработка дочерней страницы
        if result.get('child_page'):
            parent_id = result.get('parent', {}).get('database_id') or result.get('parent', {}).get('page_id')
            child_id = result.get('id')
            child_title = result.get('child_page', {}).get('title')

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

        # Достаем content и title
        if result.get('callout'):
            current_title_index = next(
                i for i, parent_list in enumerate(parent)
                if parent_list[-1] == result.get('parent', {}).get('page_id')
            )

            data.update(title=' --> '.join(titles[current_title_index]))

            callout = result.get('callout', {})
            rich_text = callout.get('rich_text', [])
            content = ''.join(i['text']['content'] for i in rich_text)
            data.update(text=content)

            URL = f"https://www.notion.so/{parent[current_title_index][-1].replace('-', '')}/"
            data.update(URL=URL)

            all_data.append(data)


async def get_data():
    stack_id = [NOTION_DATABASE_ID]
    all_data = []
    parent = []
    titles = []
    tasks_1 = []
    tasks_2 = []
    while stack_id:
        current_stack_id_len = len(stack_id)
        for id in stack_id:
            print(stack_id)
            tasks_1.append(asyncio.create_task(get_api_response(id)))
        responses = await asyncio.gather(*tasks_1)
        for response in responses:
            tasks_2.append(asyncio.create_task(get_results(response, stack_id, all_data, parent, titles)))
        await asyncio.gather(*tasks_2)
        # for _ in range(current_stack_id_len):
        #     stack_id.pop(0)
        stack_id = stack_id[current_stack_id_len:]

    with open('db1.json', 'w', encoding='utf8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)


asyncio.run(get_data())
