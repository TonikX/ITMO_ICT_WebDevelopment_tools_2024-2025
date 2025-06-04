import os
import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

PARSER_URL = os.getenv("PARSER_URL")


@app.post("/parse")
async def parse_endpoint(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{PARSER_URL}/parse?url={url}") as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise HTTPException(status_code=resp.status, detail=f"Parser error: {text}")
                return {"message": "Parser completed"}
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=500, detail=f"Parser request failed: {str(e)}")


@app.post("/parse_celery")
async def parse_endpoint(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{PARSER_URL}/parse_celery?url={url}") as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise HTTPException(status_code=resp.status, detail=f"Task error: {text}")
                return {"message": "Task started"}
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=500, detail=f"Task request failed: {str(e)}")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
