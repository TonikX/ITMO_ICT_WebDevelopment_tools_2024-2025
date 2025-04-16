from fastapi import FastAPI
from connection import init_db
from routers import transactions, categories, budgets

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(transactions.router)
app.include_router(categories.router)
app.include_router(budgets.router)
