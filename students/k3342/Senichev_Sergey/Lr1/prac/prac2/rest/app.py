from fastapi import FastAPI

from students.k3342.practical_works.Senichev_Sergey.fastapi.prac2.rest.sprint.router import router as sprint_router
from students.k3342.practical_works.Senichev_Sergey.fastapi.prac2.rest.task.router import router as task_router
from students.k3342.practical_works.Senichev_Sergey.fastapi.prac2.rest.task_link.router import router as task_links_router

app = FastAPI()

app.include_router(task_router)
app.include_router(sprint_router)
app.include_router(task_links_router)
