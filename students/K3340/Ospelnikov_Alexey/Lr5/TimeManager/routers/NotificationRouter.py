from fastapi import FastAPI, Depends, APIRouter
from models.notification import *
from connection import *
from sqlmodel import Session, select
from typing_extensions import TypedDict
from services.NotificationService import *

from schemas.notification_schema import *


notificationRouter = APIRouter(
    prefix="/notify", tags=['Notification']
)


@notificationRouter.get("/notification_list", response_model=List[NotificationRead])
def notifications_list(session=Depends(get_session)) -> List[Notification]:
    return list_all_notifications(session)


@notificationRouter.get("/{notification_id}", response_model=NotificationTask)
def notifications_get(notification_id: int, session=Depends(get_session)) -> Notification:
    return get_notification_by_id(notification_id, session)


@notificationRouter.post("/")
def notification_create(notification: Notification, session=Depends(get_session)) -> TypedDict('Response', { "status": int, "data": Notification }):
    data = new_notification_create(notification, session)
    return {"status": 200, "data": notification}



@notificationRouter.delete("/delete{notification_id}")
def notification_delete(notification_id: int, session=Depends(get_session)):
    return delete_notification(notification_id, session)
    
    
@notificationRouter.patch("/{notification_id}")
def notification_update(notification_id: int, notification: Notification, session=Depends(get_session)) -> Notification:
    db_notification = patch_notification(notification_id, notification, session)
    return db_notification

