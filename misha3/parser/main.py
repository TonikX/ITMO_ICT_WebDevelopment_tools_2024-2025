from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from task2.parser import parse_html, fetch_sync, fetch_async
import asyncio

app = FastAPI()


class HTMLRequest(BaseModel):
    html: str


@app.post("/parse")
def parse_and_save(request: HTMLRequest):
    try:
        data = parse_html(request.html)
        return {"message": "Parsed successfully", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users_sync")
def get_users_sync():
    try:
        users = fetch_sync()
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users_async")
async def get_users_async():
    try:
        users = await fetch_async()
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))