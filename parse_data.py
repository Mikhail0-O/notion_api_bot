import json
import asyncio
from itertools import count
from http import HTTPStatus

import aiohttp


from settings import (NOTION_DATABASE_ID,
                      HEADERS, logger)
from async_timed import async_timed


autoincrement = count(start=1)


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


async def get_api_response(session, block_id, delay=1):
    """Запрашиваем потомков блока по id."""
    endpoint = f"https://api.notion.com/v1/blocks/{block_id}/children"
    attempt = 0
    while True:
        try:
            async with session.get(endpoint, headers=HEADERS,
                                   raise_for_status=True) as response:
                if response.status == HTTPStatus.OK:
                    return await response.json()
        except aiohttp.ClientError as error:
            attempt = attempt + 1
            message = (f'Ошибка: {error}'
                       f'Попытка: {attempt} '
                       f'Повторный запрос через: {delay * (2 ** attempt)} сек')
            logger.error(message)
            await asyncio.sleep(delay * (2 ** attempt))


@async_timed()
async def parse_data():
    stack_id = [NOTION_DATABASE_ID]
    all_data = []
    parent = []
    titles = []
    async with aiohttp.ClientSession() as session:
        while stack_id:
            print(stack_id)
            current_len_stack_id = len(stack_id)
            requests = [get_api_response(session, block_id)
                        for block_id in stack_id]
            response = await asyncio.gather(*requests)
            for _ in range(current_len_stack_id):
                stack_id.pop(0)
            for i in response:
                get_results(i, stack_id, all_data, parent, titles)

    with open('db.json', 'w', encoding='utf8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
