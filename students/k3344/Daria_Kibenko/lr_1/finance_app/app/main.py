from fastapi import FastAPI
from app.api import user

app = FastAPI(title="Finance App")

app.include_router(user.router, prefix="/users", tags=["Users"])
