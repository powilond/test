from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./socks.db"  # Подключение к SQLite

Base = declarative_base()

# Модель для носков
class Socks(Base):
    __tablename__ = "socks"

    id = Column(Integer, primary_key=True, index=True)
    color = Column(String, nullable=False)
    cottonPart = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)

# Создание базы данных
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
