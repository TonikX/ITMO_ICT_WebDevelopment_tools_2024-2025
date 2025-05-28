from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
from typing import List
from celery_worker import parse_urls

app = FastAPI()

class URLRequest(BaseModel):
    urls: List[str]

class ParseResponse(BaseModel):
    task_id: str

@app.post("/parse/sync")
def parse_urls_sync(request: URLRequest):
    """Synchronously parse URLs using the parser service"""
    parser_url = os.getenv('PARSER_URL', 'http://parser:8001')
    results = []
    
    for url in request.urls:
        try:
            response = requests.post(
                f"{parser_url}/parse",
                json={"url": url}
            )
            response.raise_for_status()
            results.append(response.json())
        except requests.RequestException as e:
            results.append({"error": str(e), "url": url})
    
    return results

@app.post("/parse/async", response_model=ParseResponse)
async def parse_urls_async(request: URLRequest):
    """Asynchronously parse URLs using Celery"""
    # Send task to Celery
    task = parse_urls.delay(request.urls)
    return ParseResponse(task_id=task.id)

@app.get("/parse/status/{task_id}")
async def get_parse_status(task_id: str):
    """Get the status of an async parsing task"""
    task = parse_urls.AsyncResult(task_id)
    if task.ready():
        return {"status": "completed", "result": task.get()}
    return {"status": "processing"}