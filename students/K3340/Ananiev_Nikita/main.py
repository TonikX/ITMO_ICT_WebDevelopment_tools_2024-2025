import uvicorn
from fastapi import FastAPI, Security
from contextlib import asynccontextmanager
from endpoints.profile_endpoints import profile_router
from endpoints.book_endpoints import book_router
from endpoints.auth_endpoints import auth_router
from endpoints.sharing_endpoints import share_router
from jwt_logic import HTTPAuthorizationCredentials, bearer_scheme

from connection import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router, tags=['auth'])
app.include_router(profile_router, tags=['profile'])
app.include_router(book_router, tags=['book'])
app.include_router(share_router, tags=['share'])

if __name__ == '__main__':
    uvicorn.run("main:app", host='localhost', port=8080, reload=True)
