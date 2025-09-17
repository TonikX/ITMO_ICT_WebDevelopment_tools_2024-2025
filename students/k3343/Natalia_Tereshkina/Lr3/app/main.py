from fastapi import FastAPI
from app.connection import init_db
from app.finance_endpoints import router as finance_router
from app.parser_endpoint import router as parser_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(finance_router, prefix="/finance", tags=["finance"])
app.include_router(parser_router, prefix="/parser", tags=["parser"])

@app.get("/")
def hello():
    return "Never gonna give U up"