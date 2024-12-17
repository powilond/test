from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import Socks, SessionLocal

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
        raise HTTPException(status_code=400, detail="Invalid input data")

    db_socks = Socks(color=socks.color, cottonPart=socks.cottonPart, quantity=socks.quantity)
    db.add(db_socks)
    db.commit()
    db.refresh(db_socks)
    return {"message": "Socks income registered successfully"}
