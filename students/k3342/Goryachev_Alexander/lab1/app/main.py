from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi


from app.models import *
from typing_extensions import TypedDict
from app.connections import init_db, get_session
from http.client import HTTPException
from sqlalchemy import select
from app.routers import users, transactions, auth, categories, budgets, goals, notifications, goal_category

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

app = FastAPI(title="Personal Finance App")
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Finance API",
        version="1.0.0",
        description="API for finance management",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"OAuth2PasswordBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
session=Depends(get_session)

app.include_router(auth.router)
app.include_router(users.router, prefix="/users")
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(goals.router)
app.include_router(notifications.router)
app.include_router(goal_category.router)



