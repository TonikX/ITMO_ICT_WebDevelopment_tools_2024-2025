from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from db.connection import init_db
from endpoints.schedule_endpoints import schedule_router
from endpoints.schedule_task_endpoints import schedule_task_router
from endpoints.task_endpoints import task_router
from endpoints.timelog_endpoints import timelog_router
from endpoints.user_endpoints import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(task_router, prefix="/tasks", tags=["Tasks"])
app.include_router(timelog_router, prefix="/timelogs", tags=["TimeLogs"])
app.include_router(schedule_router, prefix="/schedules", tags=["DailySchedules"])
app.include_router(schedule_task_router, prefix="/schedules/tasks", tags=["DailySchedulesTasks"])

if __name__ == '__main__':
    uvicorn.run('main:app', host="localhost", port=8000, reload=True)
