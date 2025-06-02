from typing import List
from fastapi import FastAPI
from connection import init_db, close_db
from contextlib import asynccontextmanager
from routers.category_router import router as category_router
from routers.users_router import router as user_router
from routers.task_router import router as task_router
from routers.parser_router import router as parser_router
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Или ["*"] для разрешения всех
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(category_router, prefix="/categories", tags=["Categories"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(task_router, prefix="/tasks", tags=["Tasks"])
app.include_router(parser_router, prefix="/parser", tags=["Parser"])


@app.get("/")
def test():
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)