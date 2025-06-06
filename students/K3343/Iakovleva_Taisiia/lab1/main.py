from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from auth.auth import get_current_user
from auth.jwt_utils import custom_openapi
from auth.connection import init_db
from routers import user, accounts, budgets, transactions, transfers

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.openapi = lambda: custom_openapi(app)

# публичные
app.include_router(user.router)

# защищённые
protected_routers = [accounts.router, budgets.router, transactions.router, transfers.router]

for router in protected_routers:
    app.include_router(router, dependencies=[Depends(get_current_user)])

app.include_router(user.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(transfers.router)
