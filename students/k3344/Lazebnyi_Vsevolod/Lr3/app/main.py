from fastapi import FastAPI
from app.parser_endpoint import parser_router
from app.finance_endpoints import finance_router
from app.connection import init_db

app = FastAPI()
app.include_router(parser_router)
app.include_router(finance_router)

@app.on_event("startup")
def on_startup():
    init_db()