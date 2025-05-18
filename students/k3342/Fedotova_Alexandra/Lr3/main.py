from fastapi import FastAPI,  Depends,  HTTPException
from models.models import *
from celery.result import AsyncResult
from celery_worker import celery
import time
from tasks import run_parser_task
from sqlmodel import Session, select
from connection import init_db, get_session
from app_parser.main import ParserRequest
from app_parser.parser_logic import run_parser
from routers import users, trips, trip_requests, messages, preferences, favorites
from lab2.ex1.treading_calc import calculate_sum
from lab2.ex1.multiprocessing_calc import calculate_sum as multiprocessing_sum
from lab2.ex1.asyncio_calc import calculate_sum as asyncio_sum
from lab2.ex2.asyncio_preferences import parse_and_save as parse_and_save

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

@app.get("/threading-sum")
def get_threading_sum():
    start_time = time.time()
    total = calculate_sum()
    duration = time.time() - start_time
    return {
        "method": "threading",
        "result": total,
        "duration_seconds": round(duration, 2)
    }

@app.get("/multiprocessing-sum")
def get_multiprocessing_sum():
    start_time = time.time()
    total = multiprocessing_sum()
    duration = time.time() - start_time
    return {
        "method": "multiprocessing",
        "result": total,
        "duration_seconds": round(duration, 2)
    }

@app.get("/asyncio-sum")
async def get_asyncio_sum():
    start_time = time.time()
    total = await asyncio_sum()
    duration = time.time() - start_time
    return {
        "method": "asyncio",
        "result": total,
        "duration_seconds": round(duration, 2)
    }

@app.get("/parse-preferences")
async def parse_preferences():
    start_time = time.time()
    await parse_and_save()
    duration = time.time() - start_time
    return {"message": "Parsing and saving preferences completed.", "duration_seconds": round(duration, 2)}


@app.post("/parse-sync")
def parse(request: ParserRequest):
    if not request.urls:
        raise HTTPException(status_code=400, detail="No URLs provided")

    result = run_parser(request.urls)
    return result

@app.post("/parse-async")
def parse_preferences(request: ParserRequest):
    if not request.urls:
        raise HTTPException(status_code=400, detail="No URLs provided")

    task = run_parser_task.delay(request.urls)
    return {"task_id": task.id}

@app.get("/parse-async/{task_id}")
def get_parse_status(task_id: str):
    result = AsyncResult(task_id, app=celery)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }