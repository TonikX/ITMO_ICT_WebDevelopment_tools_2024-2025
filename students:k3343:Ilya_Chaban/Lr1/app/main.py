from fastapi import FastAPI
from app.connection import init_db
from app.routers import budget, category, goal, notification, transaction, auth

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(budget.router, prefix="/api", tags=["Budgets"])
app.include_router(category.router, prefix="/api", tags=["Categories"])
app.include_router(transaction.router, prefix="/api", tags=["Transactions"])
app.include_router(goal.router, prefix="/api", tags=["Goals"])
app.include_router(notification.router, prefix="/api", tags=["Notifications"])