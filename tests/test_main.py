import pytest
from fastapi.testclient import TestClient
from main import app
from models import Base
from database import engine

# Фикстура для очистки и подготовки базы данных перед каждым тестом
@pytest.fixture(scope="function")
def client():
    # Создаем все таблицы перед запуском теста
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # Удаляем все таблицы после завершения теста
    Base.metadata.drop_all(bind=engine)

# Тесты для POST /api/socks/income
def test_post_socks_income_success(client):
    response = client.post("/api/socks/income", json={
        "color": "red",
        "cottonPart": 50,
        "quantity": 100
    })
    assert response.status_code == 200
    assert response.json() == {"message": "Поступление носков успешно зарегистрировано"}

def test_post_socks_income_invalid_data(client):
    # Некорректное количество
    response = client.post("/api/socks/income", json={
        "color": "red",
        "cottonPart": 50,
        "quantity": -10
    })
    assert response.status_code == 400
    assert "Неверные параметры" in response.json()["detail"]

    # Некорректный процент хлопка
    response = client.post("/api/socks/income", json={
        "color": "red",
        "cottonPart": 120,
        "quantity": 10
    })
    assert response.status_code == 400
    assert "Неверные параметры" in response.json()["detail"]

# Тесты для POST /api/socks/outcome
def test_post_socks_outcome_success(client):
    # Добавляем носки на склад
    client.post("/api/socks/income", json={
        "color": "blue",
        "cottonPart": 70,
        "quantity": 50
    })

    # Отпускаем часть носков
    response = client.post("/api/socks/outcome", json={
        "color": "blue",
        "cottonPart": 70,
        "quantity": 30
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Носки успешно выданы"
    assert response.json()["remaining"] == 20

def test_post_socks_outcome_not_enough_quantity(client):
    # Добавляем носки на склад
    client.post("/api/socks/income", json={
        "color": "blue",
        "cottonPart": 70,
        "quantity": 10
    })

    # Пытаемся отпустить больше, чем есть
    response = client.post("/api/socks/outcome", json={
        "color": "blue",
        "cottonPart": 70,
        "quantity": 20
    })
    assert response.status_code == 400
    assert "Not enough socks in stock" in response.json()["detail"]

def test_post_socks_outcome_not_found(client):
    # Пытаемся отпустить несуществующие носки
    response = client.post("/api/socks/outcome", json={
        "color": "green",
        "cottonPart": 30,
        "quantity": 10
    })
    assert response.status_code == 400
    assert "Socks not found in the warehouse" in response.json()["detail"]

# Тесты для GET /api/socks
def test_get_socks_success(client):
    # Добавляем носки на склад
    client.post("/api/socks/income", json={
        "color": "red",
        "cottonPart": 50,
        "quantity": 100
    })
    client.post("/api/socks/income", json={
        "color": "red",
        "cottonPart": 80,
        "quantity": 50
    })

    # Запрос на носки с cottonPart > 40
    response = client.get("/api/socks", params={
        "color": "red",
        "operation": "moreThan",
        "cottonPart": 40
    })
    assert response.status_code == 200
    assert response.json()["total_quantity"] == 150

def test_get_socks_not_found(client):
    # Запрос на несуществующие носки
    response = client.get("/api/socks", params={
        "color": "purple",
        "operation": "equal",
        "cottonPart": 50
    })
    assert response.status_code == 404
    assert "No socks found matching the given criteria" in response.json()["detail"]

def test_get_socks_invalid_operation(client):
    # Некорректная операция
    response = client.get("/api/socks", params={
        "color": "red",
        "operation": "invalid",
        "cottonPart": 50
    })
    assert response.status_code == 400
    assert "Invalid operation" in response.json()["detail"]
