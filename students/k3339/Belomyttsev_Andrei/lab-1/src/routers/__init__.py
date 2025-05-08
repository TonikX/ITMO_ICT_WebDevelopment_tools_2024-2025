from fastapi import APIRouter
import routers.web
import routers.auth
import routers.band
import routers.youtube
import routers.poltube

router = APIRouter()

router.include_router(routers.web.router)
router.include_router(routers.auth.router)
router.include_router(routers.band.router)
router.include_router(routers.youtube.router)