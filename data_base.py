from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

# Определение модели
Base = declarative_base()


class Data(Base):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    card_number = Column(Integer,  nullable=False)
    title = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    code = Column(String, nullable=True)
    URL = Column(String, nullable=False)
    group = Column(String, nullable=True)
