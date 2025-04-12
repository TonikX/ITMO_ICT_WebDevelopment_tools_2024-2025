from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from db.connection import init_db
from endpoints import user_endpoints
from endpoints.hackathon_endpoints import hackathon_router
from endpoints.participant_endpoints import participant_router
from endpoints.task_endpoints import task_router
from endpoints.team_endpoints import team_router
from endpoints.uploaded_task_endpoints import uploaded_task_router
from endpoints.user_endpoints import user_router
from model import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(team_router, tags=["team"], prefix="/team")
app.include_router(hackathon_router, tags=["hackathon"], prefix="/hackathon")
app.include_router(participant_router, prefix="/participants", tags=["participants"])
app.include_router(uploaded_task_router, prefix="/uploads", tags=["uploads"])
app.include_router(task_router, prefix="/tasks", tags=["tasks"])

if __name__ == '__main__':
    uvicorn.run('main:app', host="localhost", port=8000, reload=True)
