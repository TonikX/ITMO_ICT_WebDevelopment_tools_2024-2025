from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi

from connection import init_db
from api import transactions, categories, goals, budgets, budget_categories, auth

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
app.include_router(transactions.router, prefix="/api/v1", tags=["Transactions"])
app.include_router(categories.router, prefix="/api/v1", tags=["Categories"])
app.include_router(budgets.router, prefix="/api/v1", tags=["Budgets"])
app.include_router(goals.router, prefix="/api/v1", tags=["Goals"])
app.include_router(budget_categories.router, prefix="/api/v1", tags=["BudgetCategories"])

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Finance API",
        version="3.0.0",
        description="API for personal finance management",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi