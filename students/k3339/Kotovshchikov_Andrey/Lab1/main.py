from contextlib import asynccontextmanager
from fastapi import FastAPI
from users.routes import router as user_router
from profiles.routes import router as profile_router
from projects.routes import router as project_router
from teams.routes import router as team_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(user_router)
app.include_router(profile_router)
app.include_router(project_router)
app.include_router(team_router)
