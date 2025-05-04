from fastapi import APIRouter

from .trips import router as trips_router
from .user import router as users_router
from .trip_requests import router as trip_requests_router
from .messages import router as messages_router

router = APIRouter()

router.include_router(trips_router, prefix="/trips", tags=["Trips"])
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(trip_requests_router, prefix="/trip_requests", tags=["Trip Requests"])
router.include_router(messages_router, prefix="/messages", tags=["Messages"])
