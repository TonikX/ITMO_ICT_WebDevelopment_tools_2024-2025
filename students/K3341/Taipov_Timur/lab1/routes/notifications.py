from fastapi import Depends, HTTPException, APIRouter

from auth import get_current_user
from models import *
from sqlmodel import select

from connection import get_session

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/", response_model=NotificationRead)
def create_notification(data: NotificationCreate, session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Создать новое уведомление для текущего пользователя.

    Args:
        data (NotificationCreate): Данные нового уведомления.
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        NotificationRead: Данные созданного уведомления.
    """
    db_notification = Notification(**data.dict(), user_id=user.id)
    session.add(db_notification)
    session.commit()
    session.refresh(db_notification)
    return db_notification


@router.get("/", response_model=List[NotificationRead])
def read_notifications(session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Получить список всех уведомлений текущего пользователя.

    Args:
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        List[NotificationRead]: Список уведомлений.
    """
    return session.exec(select(Notification).where(Notification.user_id == user.id)).all()


@router.delete("/{notification_id}")
def delete_notification(notification_id: int, session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Удалить уведомление по идентификатору.

    Args:
        notification_id (int): Идентификатор уведомления.
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        dict: Статус успешного удаления.

    Raises:
        HTTPException: Если уведомление не найдено или пользователь не авторизован для его удаления.
    """
    notification = session.get(Notification, notification_id)
    if not notification or notification.user_id != user.id:
        raise HTTPException(status_code=404, detail="Notification not found or unauthorized")
    session.delete(notification)
    session.commit()
    return {"ok": True}

