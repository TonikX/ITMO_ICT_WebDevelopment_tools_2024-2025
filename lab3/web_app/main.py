import requests
from fastapi import FastAPI, Depends, HTTPException
from fastapi.params import Body
from sqlmodel import Session

from api.dependency import get_current_user
from api.endpoints import book
from api.endpoints.book import book_router
from api.endpoints.exchangeRequest import exchange_request_router
from api.endpoints.genre import genre_router
from api.endpoints.user import user_router, user_protected_router
from api.models.connection import init_db, engine
from api.services.service import services_router


app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/trigger-parse")
def trigger_parse(url: str = Body(..., embed=True)):
    parser_url = "http://parser:8000/parse"
    try:
        response = requests.post(parser_url, json={"url": url})
        response.raise_for_status()
        task_info = response.json()
        return {
            "message": "Задача на парсинг поставлена",
            "task_id": task_info["task_id"],
            "status": task_info["status"]
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(user_protected_router, prefix="/user", tags=["User"])
app.include_router(book_router, prefix="/book", tags=["Book"], dependencies=[Depends(get_current_user)])
app.include_router(genre_router, prefix="/genre", tags=["Genre"], dependencies=[Depends(get_current_user)])
app.include_router(exchange_request_router, prefix="/exchange_request", tags=["Exchange Request"],
                   dependencies=[Depends(get_current_user)])
app.include_router(services_router, prefix="/services", tags=["Services"], dependencies=[Depends(get_current_user)])
