from fastapi import FastAPI, Depends
from app.db import init_db
from app.routers.auth import router as auth_router
from app.routers.user import router as user_router
from app.routers.tasks import router as task_router
from app.utils.security import get_current_user
from fastapi.openapi.utils import get_openapi


app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(auth_router, prefix="/auth", tags=["Auth"])

app.include_router(user_router, prefix="/users", tags=["Users"])

app.include_router(task_router, prefix="/tasks", tags=["Tasks"])


@app.get("/")
def read_root():
    return {"message": "Time Manager API is running!"}


@app.get("/users/me")
def read_users_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Time Manager API",
        version="0.1.0",
        description="API для управления задачами и временем",
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
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
