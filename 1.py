import json

from random import choice
# from time import sleep

# from exceptions import RequestError


# data = [
#     {
#         'title': 'заголовок1->заголовок2',
#         'URL': 'https://www.notion.so/REST-API-61d14bf1877a4db7b929eaa98a88db1f',
#         'text': 'Консистентность — это согласованность данных друг с другом'
#     },
# ]

# with open('db1.json', 'w', encoding='utf8') as f:
#     json.dump(data, f, ensure_ascii=False, indent=4)

# while True:
#     try:
#         1 / 0
#     except Exception as error:
#         raise RequestError(f'Неизвестная ошибка HTTP-запроса: {error}')
#     sleep(5)

# a = 'sdfsdf-sdfds-sdf'
# b = a.replace('-', '')
# print(b)
with open('db.json', 'r', encoding='utf8') as json_file:
    data = json.load(json_file)
    print(choice(data))
