from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import router
from database import engine
from admin import setup_admin
import models

models.Base.metadata.create_all(bind=engine)

# app = FastAPI(docs_url=None, redoc_url=None)
app = FastAPI(redoc_url=None)

app.include_router(router)

app.mount('/static', StaticFiles(directory='static'), name='static')

setup_admin(app, engine)