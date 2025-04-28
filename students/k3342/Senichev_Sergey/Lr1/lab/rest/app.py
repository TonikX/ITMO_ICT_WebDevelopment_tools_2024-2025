from fastapi import FastAPI

from rest.sprint.router import router as sprint_router
from rest.task.router import router as task_router
from rest.task_link.router import router as task_links_router
from rest.user.router import router as user_router
from rest.project.router import router as project_router
from rest.comment.router import router as comment_router

app = FastAPI()

app.include_router(task_router)
app.include_router(sprint_router)
app.include_router(task_links_router)
app.include_router(user_router)
app.include_router(project_router)
app.include_router(comment_router)
