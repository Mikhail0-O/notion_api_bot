import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data_base import Data


def refresh_db():

    # engine = create_engine('sqlite:////data/data.db')
    engine = create_engine('sqlite:///data/data.db')
    Data.metadata.create_all(engine)

    # Создание сессии
    Session = sessionmaker(bind=engine)
    session = Session()

    # Загрузка данных из JSON-файла
    # with open('/data/db.json', 'r', encoding='utf-8') as file:
    #     json_data = json.load(file)

    with open('data/db.json', 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    # Собираем block_id из JSON-файла
    json_block_ids = {entry.get('block_id')for entry in json_data
                      if 'block_id' in entry}
    db_entries = session.query(Data).all()
    for db_entry in db_entries:
        if db_entry.block_id and db_entry.block_id not in json_block_ids:
            session.delete(db_entry)

    # Добавление данных в базу
    for entry in json_data:
        existing_entry = session.query(
            Data
        ).filter_by(block_id=entry['block_id']).first()
        if existing_entry:
            # Если запись существует, проверяем на изменения
            if (existing_entry.title != entry['title'] or
                    existing_entry.text != entry['text'] or
                    existing_entry.card_number != entry['card_number'] or
                    existing_entry.code != entry['code']):
                existing_entry.title = entry['title']
                existing_entry.text = entry['text']
                existing_entry.code = entry['code']
                existing_entry.card_number = entry['card_number']
        else:
            # Если запись не существует, добавляем новую
            new_entry = Data(
                block_id=entry['block_id'],
                card_number=entry['card_number'],
                title=entry['title'],
                text=entry['text'],
                code=entry['code'],
                URL=entry['URL'],
                group=1
            )
            session.add(new_entry)

    # Сохранение изменений в базе данных
    session.commit()

    # Закрытие сессии
    session.close()


if __name__ == "__main__":
    refresh_db()
