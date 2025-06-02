from fastapi import FastAPI, Depends
from main import parse_link, parse_link_list
from worker import parse_url_task, celery_app
from fastapi.middleware.cors import CORSMiddleware
from celery.result import AsyncResult

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/parse")
def trigger_parse_task(url: str):
    task = parse_url_task.delay(url)
    return {"message": "Task submitted", "task_id": task.id}

@app.get("/task-status/{task_id}")
def get_task_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task.id,
        "status": task.status,
        "result": task.result if task.successful() else None
    }

@app.post("/parse-direct")
async def parse_direct(url: str):
    try:
        count = await parse_link(url)
        return {"message": "Парсинг завершён", "added": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка парсинга: {e}")
