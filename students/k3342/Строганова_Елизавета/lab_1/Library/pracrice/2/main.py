from logging import shutdown

from fastapi import FastAPI
from contextlib import asynccontextmanager
from db import init_db  # Импортируем функцию инициализации БД

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("📌 Запуск приложения, создаём таблицы в БД...")
    init_db()  # Создаём таблицы при старте
    shutdown()
    print("📌 Завершение работы приложения...")

app = FastAPI(lifespan)

@app.get("/")
def read_root():
    return {"message": "Приложение работает!"}
