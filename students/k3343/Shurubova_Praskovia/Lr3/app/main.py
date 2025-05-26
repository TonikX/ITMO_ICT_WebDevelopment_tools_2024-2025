from fastapi import FastAPI

from fastapi.openapi.utils import get_openapi

from app.api import parser, user, exchange, book, exchange_request, library
from app.db import init_db

app = FastAPI()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="API with Manual JWT",
        version="1.0",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            if method.get("operationId") not in ["login", "register"]:
                method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(parser.router, tags=["parser"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(book.router, prefix="/books", tags=["Books"])
app.include_router(exchange.router, prefix="/exchanges", tags=["Exchanges"])
app.include_router(exchange_request.router, prefix="/exchange_requests", tags=["ExchangeRequests"])
app.include_router(library.router, prefix="/library", tags=["Library"])