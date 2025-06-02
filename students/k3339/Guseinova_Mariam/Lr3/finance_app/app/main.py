from fastapi import FastAPI
from app.api import user, category, transaction, budget, goal, tag, parser
from fastapi.openapi.utils import get_openapi

app = FastAPI()

app.include_router(user.router)
app.include_router(category.router)
app.include_router(transaction.router)
app.include_router(budget.router)
app.include_router(goal.router)
app.include_router(tag.router)

app.include_router(parser.router, prefix="/api/v1/parsers", tags=["parsers"])

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Finance API",
        version="1.0.0",
        routes=app.routes,
        description="API для управления финансами"
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
