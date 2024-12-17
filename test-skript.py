import requests

# URL API
url = "http://127.0.0.1:8000/api/socks/income"

# Данные запроса
data = {
    "color": "red",
    "cottonPart": 50,
    "quantity": 100
}

# Отправка POST-запроса
response = requests.post(url, json=data)

# Вывод результата
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
