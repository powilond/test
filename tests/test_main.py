from fastapi.testclient import TestClient
from main import app
from main import app  # Импортируем FastAPI приложение
import sys
import os

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

client = TestClient(app)

# Тест на успешный запрос с корректными параметрами
def test_get_socks_success():
    response = client.get("/api/socks", params={
        "color": "red",
        "operation": "moreThan",
        "cottonPart": 30
    })
    assert response.status_code == 200
    assert "total_quantity" in response.json()

# Тест на некорректное значение operation
def test_get_socks_invalid_operation():
    response = client.get("/api/socks", params={
        "color": "red",
        "operation": "invalid",
        "cottonPart": 30
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid operation. Allowed values: moreThan, lessThan, equal"

# Тест на недопустимое значение cottonPart
def test_get_socks_invalid_cotton_part():
    response = client.get("/api/socks", params={
        "color": "red",
        "operation": "moreThan",
        "cottonPart": 150
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "cottonPart must be between 0 and 100"

# Тест на случай, если носки не найдены
def test_get_socks_not_found():
    response = client.get("/api/socks", params={
        "color": "purple",
        "operation": "equal",
        "cottonPart": 50
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "No socks found matching the given criteria"
