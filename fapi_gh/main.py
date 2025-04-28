from fastapi import FastAPI
from routers import users, teams, team_members, hackathons, challenges, submissions, evaluations, auth
from db.db import init_db

app = FastAPI(title="Хакатон API", version="1.0.0")

@app.on_event("startup")
def on_startup():
    init_db()

# Подключение всех маршрутов
app.include_router(auth.router)  # Маршруты для аутентификации
app.include_router(users.router)
app.include_router(teams.router)
app.include_router(team_members.router)
app.include_router(hackathons.router)
app.include_router(challenges.router)
app.include_router(submissions.router)
app.include_router(evaluations.router)

@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в Хакатон API!"}
