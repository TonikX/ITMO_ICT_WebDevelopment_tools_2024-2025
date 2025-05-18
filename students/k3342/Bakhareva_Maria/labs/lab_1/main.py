from fastapi import FastAPI
from fastapi.security import HTTPBearer

from db.connection import init_db

from routers.users import router as users_router
from routers.journeys import router as journeys_router
from routers.participants import router as participants_router
from routers.journey_stops import router as journey_stops_router
from routers.messages import router as messages_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(users_router)
app.include_router(journeys_router)
app.include_router(participants_router)
app.include_router(journey_stops_router)
app.include_router(messages_router)