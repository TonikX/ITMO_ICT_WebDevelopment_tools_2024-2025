from fastapi import FastAPI

from routers import user, trips, trip_requests, messages

app = FastAPI()

app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(trips.router, prefix="/trips", tags=["trips"])
app.include_router(trip_requests.router, prefix="/trip-requests", tags=["trip-requests"])
app.include_router(messages.router, prefix="/messages", tags=["messages"])
