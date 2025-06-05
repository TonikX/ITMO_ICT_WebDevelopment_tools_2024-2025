import time
from contextlib import asynccontextmanager

from celery.result import AsyncResult
from fastapi import APIRouter, Depends
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.celery_worker import celery_app
from app.db.session import get_session, init_db
from app.lr2.parsers import parse_with_threading, parse_with_multiprocessing
from app.repository import ProjectRepository
from app.task_manager.tasks import fetch_story_comments


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI with async DB!"}


@app.get("/health")
async def health_check(session: Depends = Depends(get_session)):
    try:
        await session.execute(text("select 1"))
        return JSONResponse({"status": "ok"}, 200)
    except Exception as e:
        return JSONResponse({"status": "error", "details": str(e)}, 500)


router_v1 = APIRouter(prefix='/api/v1', tags=["v1"])


@router_v1.get("/items/{item_id}")
async def get_item_recursive(item_id: int, session: AsyncSession = Depends(get_session)):
    return await ProjectRepository().load_thread(session, item_id)


@router_v1.get("/topstories")
async def get_top_stories(session: AsyncSession = Depends(get_session)):
    return await ProjectRepository().get_top_stories(session)


@router_v1.get("/newstories")
async def get_new_stories(session: AsyncSession = Depends(get_session)):
    return await ProjectRepository().get_new_stories(session)


celery_router = APIRouter(prefix="/celery", tags=["celery"])


@celery_router.post("/start_task/{story_id}")
def start_task(story_id: int):
    task = fetch_story_comments.delay(story_id)
    return {"task_id": task.id}


@celery_router.get("/task_status/{task_id}")
def get_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }


@celery_router.post("/wait_for_task/{story_id}")
def wait_for_task(story_id: int):
    task = fetch_story_comments.delay(story_id)

    result = task.get()

    return {
        "task_id": task.id,
        "status": task.status,
        "result": result
    }


lab_2_router = APIRouter(prefix="/lab2", tags=["lab-2"])


@lab_2_router.post('/treading')
def run_threading_parser(index: int):
    start = time.time()
    parse_with_threading(index)
    duration = time.time() - start
    return {"method": "threading", "duration": duration}


@lab_2_router.post("/multiprocessing")
def run_multiprocessing_parser(index: int):
    start = time.time()
    parse_with_multiprocessing(index)
    duration = time.time() - start
    return {"method": "multiprocessing", "duration": duration}


app.include_router(router_v1)
app.include_router(celery_router)
app.include_router(lab_2_router)
