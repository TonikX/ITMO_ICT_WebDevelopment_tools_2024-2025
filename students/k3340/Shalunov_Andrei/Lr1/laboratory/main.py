import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from connection import init_db
from auth_endpoints import auth_router
from profile_endpoints import profile_router
from book_endpoints import book_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(book_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
