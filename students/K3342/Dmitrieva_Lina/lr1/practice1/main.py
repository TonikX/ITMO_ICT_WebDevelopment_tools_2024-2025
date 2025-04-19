from fastapi import FastAPI
from typing import List
from typing_extensions import TypedDict
from models import User, Transaction

app = FastAPI()


@app.get("/")
def hello():
    return "Hello, [username]!"

temp_db = [
    User(
        id=1,
        name="Лина",
        email="lina@example.com",
        currency="RUB",
        transactions=[
            Transaction(id=101, amount=5000, transaction_type="income", date="2025-04-01"),
            Transaction(id=102, amount=1500, transaction_type="expense", date="2025-04-02"),
        ],
    ),
    User(
        id=2,
        name="Андрей",
        email="andrey@example.com",
        currency="USD",
        transactions=[
            Transaction(id=201, amount=200, transaction_type="expense", date="2025-04-01"),
        ],
    ),
]

# Получение списка пользователей
@app.get("/users", response_model=List[User])
def get_users():
    return temp_db

# Получение конкретного пользователя по ID
@app.get("/user/{user_id}", response_model=User)
def get_user(user_id: int):
    user = next((u for u in temp_db if u.id == user_id), None)
    if user:
        return user
    return {"error": "User not found"}

# Добавление нового пользователя
@app.post("/user", response_model=User)
def create_user(user: User) -> TypedDict('Response', {"status": int, "data": User}):
    temp_db.append(user)
    return {"status": 200, "data": user}

# Удаление пользователя
@app.delete("/user/{user_id}")
def delete_user(user_id: int) -> dict:
    global temp_db
    temp_db = [u for u in temp_db if u.id != user_id]
    return {"status": 200, "message": "User deleted"}

# Обновление пользователя
@app.put("/user/{user_id}", response_model=User)
def update_user(user_id: int, user_data: User) -> dict:
    for i, user in enumerate(temp_db):
        if user.id == user_id:
            temp_db[i] = user_data
            return {"status": 200, "data": user_data}
    return {"status": 404, "error": "User not found"}
