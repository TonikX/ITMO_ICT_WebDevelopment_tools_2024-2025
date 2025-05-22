from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.api.v1.routers import api_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(api_router, prefix="/api/v1")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="API Documentation",
        version="1.0.0",
        description="API documentation with proper auth",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "api/v1/auth/token",
                    "scopes": {}
                }
            }
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi