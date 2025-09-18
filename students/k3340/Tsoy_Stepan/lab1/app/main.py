from fastapi import FastAPI
from app.db.session import engine, init_db
from app.models import *  # импортирует и регистрирует модели
from app.routers import users, accounts, categories, transactions, budgets

app = FastAPI(title="Finance Manager API")

# Можно вызвать init_db() в dev режиме, но на prod — используем alembic миграции
# init_db()

app.include_router(users.router)
app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
