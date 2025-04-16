from fastapi import FastAPI
from app.api.endpoints import users, transactions, categories, budgets, tags

app = FastAPI(title="Personal Finance Management API")

# Include routers for modular endpoints
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(budgets.router, prefix="/budgets", tags=["budgets"])
app.include_router(tags.router, prefix="/tags", tags=["tags"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
