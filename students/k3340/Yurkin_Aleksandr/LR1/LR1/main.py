from fastapi import FastAPI

from connection import init_db
from controllers.user_controller import router as user_router
from controllers.trip_controller import router as trip_router
from controllers.message_controller import router as message_router
from controllers.review_controller import router as review_router

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def hello():
    return "Hello, [username]!"


app.include_router(user_router)
app.include_router(trip_router)
app.include_router(message_router)
app.include_router(review_router)