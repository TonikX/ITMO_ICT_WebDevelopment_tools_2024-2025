from fastapi import Depends, HTTPException, APIRouter

from auth import get_current_user
from models import *
from sqlmodel import select

from connection import get_session

router = APIRouter(prefix="/routines", tags=["Routines"])


@router.post("/", response_model=RoutineRead)
def create_routine(routine: RoutineCreate, session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Создать новую рутину (повторяющееся действие) для текущего пользователя.

    Args:
        routine (RoutineCreate): Данные новой рутины.
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        RoutineRead: Данные созданной рутины.
    """
    db_routine = Routine(**routine.dict(), user_id=user.id)
    session.add(db_routine)
    session.commit()
    session.refresh(db_routine)
    return db_routine


@router.get("/", response_model=List[RoutineRead])
def read_routines(session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Получить список всех рутин текущего пользователя.

    Args:
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        List[RoutineRead]: Список рутин.
    """
    return session.exec(select(Routine).where(Routine.user_id == user.id)).all()


@router.delete("/{routine_id}")
def delete_routine(routine_id: int, session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Удалить рутину по идентификатору.

    Args:
        routine_id (int): Идентификатор рутины.
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        dict: Статус успешного удаления.

    Raises:
        HTTPException: Если рутина не найдена или пользователь не авторизован для её удаления.
    """
    routine = session.get(Routine, routine_id)
    if not routine or routine.user_id != user.id:
        raise HTTPException(status_code=404, detail="Routine not found or unauthorized")
    session.delete(routine)
    session.commit()
    return {"ok": True}

