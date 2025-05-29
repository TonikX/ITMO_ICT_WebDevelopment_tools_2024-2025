from fastapi import APIRouter, HTTPException
import requests
from models import *
from celery import Celery

celery_app = Celery("parser", broker='redis://redis:6379/0', backend='redis://redis:6379/0')

router = APIRouter()

parser_url = "http://parser:8001/parse"

@router.post("/common")
def parse(data: ParseRequest):
    response = requests.post(parser_url, json={"url": data.url})
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

@router.post("/celery-task")
def parse(data: ParseRequest):
    task = celery_app.send_task("parse_from_url", args=[data.url])
    return {"task_id": task.id, "status": "queued"}