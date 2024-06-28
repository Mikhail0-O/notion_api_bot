import json


data = [
    {
        'title': 'заголовок1->заголовок2',
        'URL': 'https://www.notion.so/REST-API-61d14bf1877a4db7b929eaa98a88db1f',
        'text': 'Консистентность — это согласованность данных друг с другом'
    },
]

with open('db1.json', 'w', encoding='utf8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
