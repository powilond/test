from sqlalchemy import Column, Integer, String
from database import Base

# Создание модели для таблицы "socks"
class Socks(Base):
    __tablename__ = "socks"  # Название таблицы в базе данных

    id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор
    color = Column(String, nullable=False)  # Цвет носков
    cottonPart = Column(Integer, nullable=False)  # Процент хлопка
    quantity = Column(Integer, nullable=False)  # Количество пар носков
