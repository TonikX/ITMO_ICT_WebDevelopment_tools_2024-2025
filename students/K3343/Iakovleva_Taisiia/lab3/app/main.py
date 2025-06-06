from fastapi import FastAPI, HTTPException, Query
from tasks import async_parse, celery_app
from db import init_db
from models import ParsedPage
from sqlmodel import Session, select
from db import engine
import celery.states as states
import time

app = FastAPI()

@app.on_event("startup")
def on_startup():
    time.sleep(5)
    init_db()

@app.post("/parse")
def parse_url(url: str = Query(..., description="URL страницы")):
    task = async_parse.delay(url)
    return {"task_id": task.id, "status": "Processing"}

@app.get("/result/{task_id}")
def get_result(task_id: str):
    result = celery_app.AsyncResult(task_id)
    if result.state == states.PENDING:
        return {"status": "Pending"}
    elif result.state == states.FAILURE:
        return {"status": "Failure", "error": str(result.result)}
    elif result.state == states.SUCCESS:
        return {"status": "Success", "result": result.result}
    else:
        return {"status": result.state}

@app.get("/pages")
def list_pages():
    with Session(engine) as session:
        pages = session.exec(select(ParsedPage)).all()
        return pages
