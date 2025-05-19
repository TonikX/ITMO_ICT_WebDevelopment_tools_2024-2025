from fastapi import FastAPI, HTTPException
import requests
from parser import parse_and_save
from tasks import parse_and_save_task

app = FastAPI()


@app.post("/parse")
async def parse(url: str):
    try:
        await parse_and_save(url)
        return {"message": "Parsing completed!"}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/parse/queue")
async def parse_queue(url: str):
    parse_and_save_task.delay(url)
    return {"message": "Task added to queue."}
