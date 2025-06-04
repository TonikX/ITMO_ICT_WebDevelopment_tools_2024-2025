from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tasks import parse_and_save_task, parse

app = FastAPI()


@app.post("/parse")
async def parse_endpoint(url: str):
    await parse(url)
    return {"message": "Parsing completed"}


@app.post("/parse_celery")
async def parse_endpoint(url: str):
    parse_and_save_task.apply_async(args=[url], queue='parser')
    return {"message": "Task started"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
