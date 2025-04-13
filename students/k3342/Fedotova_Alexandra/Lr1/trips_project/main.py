from fastapi import FastAPI,  Depends
from models.models import *
from sqlmodel import Session, select
from connection import init_db, get_session
from routers import users, trips, trip_requests, messages, preferences, favorites

app = FastAPI()
app.include_router(users.router)
app.include_router(trips.router)
app.include_router(trip_requests.router)
app.include_router(messages.router)
app.include_router(preferences.router)
app.include_router(favorites.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/test_users")
def test_users(db: Session = Depends(get_session)):
    return db.exec(select(User)).all()

