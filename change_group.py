from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data_base import Data


def change_group(new_group, card_number):

    engine = create_engine('sqlite:///data.db')

    # Создание сессии
    Session = sessionmaker(bind=engine)
    session = Session()
    card = session.query(Data).filter_by(card_number=card_number).first()
    card.group = new_group
    session.commit()
    session.close()


if __name__ == "__main__":
    card_number = 1
    new_group = 2
    change_group(card_number, new_group)
