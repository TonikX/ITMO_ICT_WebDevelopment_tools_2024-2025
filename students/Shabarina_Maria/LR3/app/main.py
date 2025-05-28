from fastapi import FastAPI
from app.user_endpoints import user_router
from app.team_platform_endpoints import team_platform_router
from app.parser_endpoint import parser_router
from app.connection import init_db

app = FastAPI()
app.include_router(user_router)
app.include_router(team_platform_router)
app.include_router(parser_router)


@app.on_event("startup")
def on_startup():
    init_db()

