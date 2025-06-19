from fastapi import FastAPI
from routers import users, transactions, categories, budgets, goals, auth
from database import engine
from sqlmodel import SQLModel
from routers.auth import router as auth_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

app.include_router(auth_router)
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(categories.router)
app.include_router(budgets.router)
app.include_router(goals.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Finance Manager API"}