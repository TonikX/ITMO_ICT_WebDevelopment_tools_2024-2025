from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware

from main_app.auth.auth import authenticate_request
from main_app.db import init_db
from fastapi import FastAPI
from main_app.routers import participants, reviews, user, trip, discussion, parser
from main_app.auth.openapi import custom_openapi

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.openapi = lambda: custom_openapi(app)

app.include_router(user.router)
app.include_router(parser.router, tags=["parser"])
protected_routers = [
    trip.router,
    discussion.router,
    participants.router,
    reviews.router,
]

for router in protected_routers:
    app.include_router(router, dependencies=[Depends(authenticate_request)])


