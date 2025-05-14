# main.py

from fastapi import FastAPI
from controllers import (
    user_controller,
    team_controller,
    team_membership_controller,
    hackathon_controller,
    task_controller,
    submission_controller
)
from fastapi.openapi.utils import get_openapi

app = FastAPI(title="Hackathon System API", version="1.0.0")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description="API для приложения тайм-менеджера.",
        routes=app.routes,
    )
    # Добавляем схему безопасности в компоненты
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    # Если необходимо добавить безопасную схему для всех эндпоинтов, можно сделать так:
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method].setdefault("security", [{"BearerAuth": []}])
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Переопределяем генерацию OpenAPI-схемы
app.openapi = custom_openapi
app.include_router(user_controller.router, prefix="/users", tags=["Users"])
app.include_router(team_controller.router, prefix="/teams", tags=["Teams"])
app.include_router(team_membership_controller.router, prefix="/memberships", tags=["TeamMembership"])
app.include_router(hackathon_controller.router, prefix="/hackathons", tags=["Hackathons"])
app.include_router(task_controller.router, prefix="/tasks", tags=["Tasks"])
app.include_router(submission_controller.router, prefix="/submissions", tags=["Submissions"])