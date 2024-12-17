from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Socks


app = FastAPI()

# Зависимость для подключения к БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Схема для валидации входных данных
class SocksIncomeRequest(BaseModel):
    color: str
    cottonPart: int
    quantity: int

@app.post("/api/socks/income")
def register_income(socks: SocksIncomeRequest, db: Session = Depends(get_db)):
    if not (0 <= socks.cottonPart <= 100) or socks.quantity <= 0:
        raise HTTPException(status_code=400, detail="Неверные параметры")

    db_socks = Socks(color=socks.color, cottonPart=socks.cottonPart, quantity=socks.quantity)
    db.add(db_socks)  # Добавляем объект в сессию
    db.commit()  # Сохраняем изменения в базе данных
    db.refresh(db_socks)  # Обновляем объект
    return {"message": "Поступление носков успешно зарегистрировано"}

# Схема для валидации выходных данных
class SocksOutcomeRequest(BaseModel):
    color: str
    cottonPart: int
    quantity: int

# Маршрут для регистрации отпуска носков
@app.post("/api/socks/outcome")
def register_outcome(socks: SocksOutcomeRequest, db: Session = Depends(get_db)):
    # Валидация входных данных
    if not (0 <= socks.cottonPart <= 100) or socks.quantity <= 0:
        raise HTTPException(status_code=400, detail="Invalid input data")

    # Найти носки в базе данных по цвету и проценту хлопка
    db_socks = db.query(Socks).filter(
        Socks.color == socks.color,
        Socks.cottonPart == socks.cottonPart
    ).first()

    # Проверка наличия записи
    if not db_socks:
        raise HTTPException(status_code=400, detail="Socks not found in the warehouse")

    # Проверка количества носков
    if db_socks.quantity < socks.quantity:
        raise HTTPException(status_code=400, detail="Not enough socks in stock")

    # Уменьшаем количество носков
    db_socks.quantity -= socks.quantity

    # Сохраняем изменения
    db.commit()
    db.refresh(db_socks)

    return {"message": "Носки успешно выданы", "remaining": db_socks.quantity}

# Маршрут для получения количества носков по критериям
@app.get("/api/socks")
def get_socks(
    color: str = Query(..., description="Цвет носков"),
    operation: str = Query(..., description="Операция сравнения: moreThan, lessThan, equal"),
    cottonPart: int = Query(..., description="Процент хлопка для сравнения (0-100)"),
    db: Session = Depends(get_db)
):
    # Проверка корректности входных данных
    if operation not in ["moreThan", "lessThan", "equal"]:
        raise HTTPException(status_code=400, detail="Invalid operation. Allowed values: moreThan, lessThan, equal")
    if not (0 <= cottonPart <= 100):
        raise HTTPException(status_code=400, detail="cottonPart must be between 0 and 100")

    # Формирование условия для запроса
    query = db.query(Socks).filter(Socks.color == color)

    if operation == "moreThan":
        query = query.filter(Socks.cottonPart > cottonPart)
    elif operation == "lessThan":
        query = query.filter(Socks.cottonPart < cottonPart)
    elif operation == "equal":
        query = query.filter(Socks.cottonPart == cottonPart)

    # Подсчет общего количества носков
    total_quantity = sum(s.quantity for s in query.all())
    if total_quantity == 0:
        raise HTTPException(
            status_code=404,
            detail="No socks found matching the given criteria"
        )

    return {"total_quantity": total_quantity}
