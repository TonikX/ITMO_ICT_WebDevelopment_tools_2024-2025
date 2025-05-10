from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import select, Session
from typing import List

from app.connection import get_session
from app.models import NotificationDefault, Notification

router = APIRouter()

@router.post("/notification")
def create_notification(notification_data: NotificationDefault, session: Session = Depends(get_session)):
    notification = Notification.model_validate(notification_data)
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return {"status": 200, "data": notification}


@router.get("/notification_list", response_model=List[Notification])
def get_notifications(session: Session = Depends(get_session)):
    return session.exec(select(Notification)).all()


@router.get("/notification/{notification_id}", response_model=Notification)
def get_notification_by_id(notification_id: int, session: Session = Depends(get_session)):
    notification = session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.delete("/notification/delete/{notification_id}")
def delete_notification(notification_id: int, session: Session = Depends(get_session)):
    notification = session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    session.delete(notification)
    session.commit()
    return {"status": "OK"}


@router.put("/notification/{notification_id}")
def update_notification(notification_id: int, notification_data: NotificationDefault, session: Session = Depends(get_session)):
    notification = session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    for key, value in notification_data.model_dump(exclude_unset=True).items():
        setattr(notification, key, value)

    session.add(notification)
    session.commit()
    session.refresh(notification)
    return {"status": "OK", "data": notification}
