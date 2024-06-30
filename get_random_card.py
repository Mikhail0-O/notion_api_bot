import json
from random import choice


def get_random_card():
    with open('db.json', 'r', encoding='utf8') as json_file:
        data = json.load(json_file)
        choice_data = choice(data)
        items = list(choice_data.values())
        message = (f'<b>{items[0]}.</b>\n'
                   f'\n'
                   f'{items[1]}\n'
                   f'\n'
                   f'{items[2]}')
        return message


get_random_card()
