from fastapi import FastAPI
from endpoints.user_endpoints import user_router
from endpoints.team_platform_endpoints import team_platform_router
from db.connection import init_db


app = FastAPI()
app.include_router(user_router)
app.include_router(team_platform_router)


@app.on_event("startup")
def on_startup():
    init_db()
