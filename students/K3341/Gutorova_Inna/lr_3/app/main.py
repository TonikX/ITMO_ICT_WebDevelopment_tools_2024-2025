import os

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette import status

from connection import init_db
from auth.router import router as auth_router
from controllers.users import router as users_router
from controllers.tasks import router as tasks_router
from controllers.categories import router as categories_router
from controllers.tags import router as tags_router
from controllers.reminders import router as reminders_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(categories_router)
app.include_router(tags_router)
app.include_router(reminders_router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def read_root():
    return {"message": "Time Manager API"}


PARSER_SERVICE_URL = os.getenv("PARSER_SERVICE_URL", "http://parser:8001")


class ParseRequest(BaseModel):
    url: str


@app.post("/parse")
async def parse_url(request: ParseRequest):
    try:
        async with httpx.AsyncClient() as client:
            # Отправляем запрос к сервису парсера
            response = await client.post(
                f"{PARSER_SERVICE_URL}/parse",
                json={"url": request.url}
            )
            response.raise_for_status()
            return response.json()

    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Parser service is unavailable"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Parser service request timed out"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Parser error: {e.response.text}"
        )