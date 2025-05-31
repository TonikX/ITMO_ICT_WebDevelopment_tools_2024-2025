from fastapi import FastAPI
from db.connection import init_db

from api.users import router as users_router
from api.trips import router as trips_router
from api.companions import router as companions_router
from api.itineraries import router as itineraries_router
from api.messages import router as messages_router
from api.parser_proxy import router as parser_proxy_router

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(users_router)
app.include_router(trips_router)
app.include_router(companions_router)
app.include_router(itineraries_router)
app.include_router(messages_router)
app.include_router(parser_proxy_router)
