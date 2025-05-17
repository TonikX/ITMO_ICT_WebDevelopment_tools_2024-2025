from fastapi import Depends, HTTPException, APIRouter

from auth import get_current_user
from models import *
from sqlmodel import select

from connection import get_session

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.post("/", response_model=TagRead)
def create_tag(tag: TagCreate, session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Создать новый тег для текущего пользователя.

    Args:
        tag (TagCreate): Данные нового тега.
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        TagRead: Данные созданного тега.
    """
    db_tag = Tag(**tag.dict(), user_id=user.id)
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag


@router.get("/", response_model=List[TagRead])
def read_tags(session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Получить список всех тегов текущего пользователя.

    Args:
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        List[TagRead]: Список тегов.
    """
    return session.exec(select(Tag).where(Tag.user_id == user.id)).all()


@router.delete("/{tag_id}")
def delete_tag(tag_id: int, session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Удалить тег по идентификатору.

    Args:
        tag_id (int): Идентификатор тега.
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        dict: Статус успешного удаления.

    Raises:
        HTTPException: Если тег не найден или пользователь не авторизован для его удаления.
    """
    tag = session.get(Tag, tag_id)
    if not tag or tag.user_id != user.id:
        raise HTTPException(status_code=404, detail="Tag not found or unauthorized")
    session.delete(tag)
    session.commit()
    return {"ok": True}

