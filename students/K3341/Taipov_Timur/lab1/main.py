from fastapi import FastAPI
from routes import tasks, users, projects, tags, timelogs, routines, notifications

app = FastAPI()

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tags.router)
app.include_router(timelogs.router)
app.include_router(routines.router)
app.include_router(notifications.router)
