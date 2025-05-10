from fastapi import FastAPI
from app.api import auth, finance

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(finance.router, prefix="/finance", tags=["finance"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
