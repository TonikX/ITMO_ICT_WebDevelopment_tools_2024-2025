from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, events, teams, tasks, submissions

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(events.router)

api_router.include_router(teams.router)
api_router.include_router(tasks.router)
api_router.include_router(tasks.router)
api_router.include_router(submissions.router)
