from fastapi import Depends, HTTPException, APIRouter

from auth import get_current_user
from models import *
from sqlmodel import select

from connection import get_session

router = APIRouter(prefix="/timelogs", tags=["Timelogs"])


@router.post("/", response_model=TimeLogRead)
def create_timelog(log: TimeLogCreate, session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Создать новую запись учёта времени для текущего пользователя.

    Args:
        log (TimeLogCreate): Данные новой записи учёта времени.
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        TimeLogRead: Данные созданной записи.
    """
    db_log = TimeLog(**log.dict(), user_id=user.id)
    session.add(db_log)
    session.commit()
    session.refresh(db_log)
    return db_log


@router.get("/", response_model=List[TimeLogRead])
def read_timelogs(session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Получить список всех записей учёта времени текущего пользователя.

    Args:
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        List[TimeLogRead]: Список записей учёта времени.
    """
    return session.exec(select(TimeLog).where(TimeLog.user_id == user.id)).all()


@router.delete("/{log_id}")
def delete_timelog(log_id: int, session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Удалить запись учёта времени по идентификатору.

    Args:
        log_id (int): Идентификатор записи.
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        dict: Статус успешного удаления.

    Raises:
        HTTPException: Если запись не найдена или пользователь не авторизован для её удаления.
    """
    log = session.get(TimeLog, log_id)
    if not log or log.user_id != user.id:
        raise HTTPException(status_code=404, detail="TimeLog not found or unauthorized")
    session.delete(log)
    session.commit()
    return {"ok": True}

