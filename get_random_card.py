from random import choice

from telebot import formatting
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data_base import Data
from settings import PRIORITY_OF_GROUPS


def get_random_card():

    engine = create_engine('sqlite:///data.db')

    # Создание сессии
    Session = sessionmaker(bind=engine)
    session = Session()
    while True:
        current_group = choice(PRIORITY_OF_GROUPS)
        cards_from_current_group = session.query(
            Data).filter_by(group=current_group)
        if cards_from_current_group.first():
            break

    all_cards_in_current_group = session.query(Data.card_number).filter_by(group=current_group)
    all_cards_in_current_group_list = [card.card_number for card in all_cards_in_current_group]
    current_card_number = choice(all_cards_in_current_group_list)

    cards_from_current_group = session.query(Data).filter_by(group=current_group, card_number=current_card_number)
    current_card = cards_from_current_group.first()
    group_title = (f'Карточка № {str(current_card.card_number)} из группы '
                   f'№ {str(current_card.group)}')
    if current_card.code:
        message = (
            f'{formatting.hitalic(group_title)}\n\n'
            f'{formatting.hbold(current_card.title)}\n\n'
            f'{current_card.text}\n\n'
            f'{formatting.hpre(str(current_card.code))}\n\n'
            f'{current_card.URL}'
        )
    else:
        message = (
            f'{formatting.hitalic(group_title)}\n\n'
            f'{formatting.hbold(current_card.title)}\n\n'
            f'{current_card.text}\n\n'
            f'{current_card.URL}'
        )
    session.close()
    return message, current_card.card_number


if __name__ == '__main__':
    print(get_random_card())
