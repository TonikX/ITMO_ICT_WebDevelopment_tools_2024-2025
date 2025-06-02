from fastapi import FastAPI

from db.connection import init_db
from routes.api import router


app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"message": "Приложение работает!"}


app.include_router(router)
