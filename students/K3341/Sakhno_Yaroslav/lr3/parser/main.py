import requests
from fastapi import FastAPI, HTTPException
from celery_config import celery_app
from parser import parse_data
from save_data import save_to_db
from celery import shared_task

app = FastAPI()

# urls = [
#     "https://www.litres.ru/author/kayl-simpson/",
#     "https://www.litres.ru/author/robert-s-martin/",
#     "https://www.litres.ru/author/darya-doncova/"
# ]
@app.get("/")
async def root():
    return {"message": "Ярослав Сахно"}


@app.post("/parse")
async def parse(url: str):
    try:
        parse_task.delay(url)
        return {"message": "Parsing task started"}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


@shared_task
def parse_task(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        author_info = parse_data(url)
        save_to_db(author_info)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
