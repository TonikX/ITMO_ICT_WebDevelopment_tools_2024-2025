from fastapi import FastAPI
from db.connection import init_db
from routers import (
    auth_router,
    users, 
    categories,
    transactions,
    budgets,
    accounts,
    goals,
    preferences,
    parser
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
app.include_router(parser.router)


@app.get("/")
def root():
    return {"message": "Добро пожаловать в сервис управления финансами!"}

@app.on_event("startup")
def on_startup():
    init_db()