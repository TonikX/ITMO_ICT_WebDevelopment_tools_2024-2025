from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from db.connection import init_db
from endpoints.tag_endpoints import tag_router
from endpoints.task_endpoints import task_router
from endpoints.timelog_endpoints import timelog_router

from endpoints.user_endpoints import user_router
from models import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(task_router)
app.include_router(tag_router)
app.include_router(timelog_router)

if __name__ == '__main__':
    uvicorn.run('main:app', host="localhost", port=8000, reload=True)
