from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import Notification, User
from app.connections import get_session
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/", response_model=Notification)
def create_notification(notification: Notification, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    notification.user_id = user.id
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification

@router.get("/", response_model=list[Notification])
def get_notifications(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    statement = select(Notification).where(Notification.user_id == user.id)
    return session.exec(statement).all()

@router.get("/{notification_id}", response_model=Notification)
def get_notification(notification_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    notification = session.get(Notification, notification_id)
    if not notification or notification.user_id != user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.put("/{notification_id}/read", response_model=Notification)
def mark_as_read(notification_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    notification = session.get(Notification, notification_id)
    if not notification or notification.user_id != user.id:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification

@router.delete("/{notification_id}")
def delete_notification(notification_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    notification = session.get(Notification, notification_id)
    if not notification or notification.user_id != user.id:
        raise HTTPException(status_code=404, detail="Notification not found")

    session.delete(notification)
    session.commit()
    return {"ok": True}