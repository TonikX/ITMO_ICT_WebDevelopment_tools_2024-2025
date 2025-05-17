from fastapi import FastAPI
from api.auth import router as auth_router
from api import users, categories, transactions, budgets, goals, transactioncategories
from api import parser


app = FastAPI()

@app.get("/")
def root():
    return {"message": "ab.money"}

app.include_router(auth_router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(goals.router)
app.include_router(transactioncategories.router)
app.include_router(parser.router)

