# app/main.py

from fastapi import FastAPI
from app.api import profiles, projects, users, team_members

app = FastAPI(title="Team Finder API")

app.include_router(users.router)
app.include_router(profiles.router)
app.include_router(projects.router)
app.include_router(team_members.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Team Finder API"}