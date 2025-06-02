from fastapi import FastAPI, Depends
from models.user import *
from models.schedule import *
from models.task import *
from models.task_schedule import *
from models.notification import *

from routers.UserRouter import userRouter
from routers.TaskScheduleRouter import taskScheduleRouter
from routers.TaskRouter import taskRouter
from routers.ScheduleRouter import scheduleRouter
from routers.NotificationRouter import notificationRouter
from routers.NotificationRouter import notificationRouter
from routers.AuthRouter import authRouter
from routers.ParserRouter import parserRouter


from connection import *
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing_extensions import TypedDict

from config import settings
from datetime import timedelta


app = FastAPI()

app.include_router(userRouter)
app.include_router(taskScheduleRouter)
app.include_router(taskRouter)
app.include_router(scheduleRouter)
app.include_router(notificationRouter)
app.include_router(parserRouter)

app.include_router(authRouter)


TaskScheduleSerializator.model_rebuild()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()
    
