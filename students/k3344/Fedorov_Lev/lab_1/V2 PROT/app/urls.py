import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .models import init_db

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from .routes.users.auth import router as auth_router
from .routes.users.crud import router as user_router
from .routes.protocol.excel_routes_protocol import router as protocol_router
from .routes.users.login import router as login_router
from .config import DATABASE_URL
from .routes.users.roles import router as user_roles_router
from .routes.tournaments.crud import router as tournament_cruds_router
from .routes.tournaments.seasons import router as tournament_seasons_router
from .routes.tournaments.applications import router as tournament_applications_router
from .routes.teams.crud import router as teams_crud_router
from .routes.teams.players import router as teams_players_router
from .routes.players.crud import router as players_cruds_router
from .routes.schools.crud import router as schools_crud_router
from .routes.players.documents import router as player_documents_router

# Новые роутеры для парсера
from .routes.parser.parse_routes import router as parse_router
from .routes.parser.celery_routes import router as celery_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine, SessionMaker = await init_db(DATABASE_URL)

    app.state.db_session = SessionMaker
    app.state.engine = engine

    yield

    await engine.dispose()

app = FastAPI(
    title="Hockey API",
    description="API for hockey team management with parsing capabilities",
    docs_url="/docs",
    lifespan=lifespan
)

# Существующие роутеры
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(protocol_router)
app.include_router(login_router)
app.include_router(user_roles_router)
app.include_router(tournament_cruds_router)
app.include_router(tournament_seasons_router)
app.include_router(tournament_applications_router)
app.include_router(teams_crud_router)
app.include_router(teams_players_router)
app.include_router(players_cruds_router)
app.include_router(schools_crud_router)
app.include_router(player_documents_router)

# Новые роутеры для парсинга
app.include_router(parse_router)    # Прямые вызовы парсера
app.include_router(celery_router)   # Очереди Celery

@app.get("/")
async def root():
    return {
        "message": "Hockey API with Parsing",
        "version": "3.0.0",
        "features": [
            "Team Management",
            "Tournament Management", 
            "Player Management",
            "Sports Data Parsing",
            "Queue-based Processing"
        ],
        "endpoints": {
            "docs": "/docs",
            "parser": "/parser",
            "queue": "/queue"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "hockey-api",
        "version": "3.0.0"
    }