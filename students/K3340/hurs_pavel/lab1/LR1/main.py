from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from controllers import (
    user_controller,
    task_controller,
    time_entry_controller,
    task_assignment_controller
)

app = FastAPI(title="Time Manager API", version="1.0.0")

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

# Подключаем роутеры API
app.include_router(user_controller.router, prefix="/users", tags=["Users"])
app.include_router(task_controller.router, prefix="/tasks", tags=["Tasks"])
app.include_router(time_entry_controller.router, prefix="/time-entries", tags=["Time Entries"])
app.include_router(task_assignment_controller.router, prefix="/assignments", tags=["Task Assignments"])