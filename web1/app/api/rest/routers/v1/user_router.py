from fastapi import APIRouter, Depends
from app.controolers import user_controller
from app.models import UserAuth, UserUpdate

router = APIRouter(prefix="/user", tags=["Users"])

router.post("/login")(user_controller.login)
router.post("/registration")(user_controller.register)
router.post("/set-admin/{user_id}")(user_controller.set_admin)
router.post("/get-profile")(user_controller.get_profile)
router.get("/get-all")(user_controller.get_all_users)
router.get("/get-one/{user_id}")(user_controller.get_user)
router.delete("/delete-profile")(user_controller.delete_user)
router.patch("/update-profile")(user_controller.update_user)
