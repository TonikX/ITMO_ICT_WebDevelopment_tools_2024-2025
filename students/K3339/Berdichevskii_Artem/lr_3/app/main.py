from fastapi import FastAPI, HTTPException
import requests
from app.tasks import parse_url_task

app = FastAPI()

@app.post("/parse-direct")
def parse_direct(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return {"message": "Parsed directly", "length": len(response.text)}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/parse-async")
def parse_async(url: str):
    task = parse_url_task.delay(url)
    return {"message": "Parsing started", "task_id": task.id}