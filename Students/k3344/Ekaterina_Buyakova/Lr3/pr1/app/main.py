from fastapi import FastAPI

from core import settings
from routers import analytics
from routers import auth, transactions, categories
from routers import budget_alerts
from routers import budgets
from routers import users

app = FastAPI(
    title="Сервис управления финансами",
    description="API для управления личными финансами",
    version="1.0.0",
    swagger_ui_parameters={"oauth2RedirectUrl": "/auth"}
)

app.include_router(auth.router, prefix="/auth", tags=["Авторизация"])
app.include_router(users.router, prefix="/users", tags=["Пользователи"])
app.include_router(transactions.router, prefix="/transactions", tags=["Транзакции"])
app.include_router(categories.router, prefix="/categories", tags=["Категории"])
app.include_router(budgets.router, prefix="/budgets", tags=["Бюджеты"])
app.include_router(budget_alerts.router, prefix="/budgets", tags=["Бюджетные уведомления"])
app.include_router(analytics.router, prefix="/analytics", tags=["Аналитика"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=settings.APP_PORT)
