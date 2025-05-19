from fastapi import FastAPI
from app.db.connection import init_db
from app.routers import (
    auth_router,
    users, 
    categories,
    transactions,
    budgets,
    accounts,
    goals,
    preferences
)

app = FastAPI(title="Personal Finance API (with manual Auth)")

app.include_router(auth_router.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(accounts.router)
app.include_router(goals.router)
app.include_router(preferences.router)


@app.get("/")
def root():
    return {"message": "Добро пожаловать в сервис управления финансами!"}

@app.on_event("startup")
def on_startup():
    init_db()