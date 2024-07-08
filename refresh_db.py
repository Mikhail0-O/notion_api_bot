import json

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from data_base import Data


def refresh_db():

    engine = create_engine('sqlite:///data.db')

    # Создание сессии
    Session = sessionmaker(bind=engine)
    session = Session()

    # Загрузка данных из JSON-файла
    with open('db.json', 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    # Добавление данных в базу
    for entry in json_data:
        existing_entry = session.query(
            Data
        ).filter_by(card_number=entry['card_number']).first()
        if existing_entry:
            # Если запись существует, проверяем на изменения
            if (existing_entry.title != entry['title'] or
                existing_entry.text != entry['text'] or
                    existing_entry.code != entry['code']):
                existing_entry.title = entry['title']
                existing_entry.text = entry['text']
                existing_entry.code = entry['code']
                existing_entry.URL = entry['URL']
        else:
            # Если запись не существует, добавляем новую
            new_entry = Data(
                card_number=entry['card_number'],
                title=entry['title'],
                text=entry['text'],
                code=entry['code'],
                URL=entry['URL'],
                group=1
            )
            session.add(new_entry)

    len_json_data = len(json_data)
    len_data_base = session.query(Data).count()
    # print(len_json_data)
    # print(len_data_base)
    while len_data_base > len_json_data:
        last_entry = session.query(Data).order_by(desc(Data.card_number)).first()
        session.delete(last_entry)
        len_data_base = session.query(Data).count()

    # print(len(json_data))
    # print(session.query(Data).count())
    # Сохранение изменений в базе данных
    session.commit()

    # Закрытие сессии
    session.close()


if __name__ == "__main__":
    refresh_db()
