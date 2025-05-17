from fastapi import Depends, HTTPException, APIRouter

from auth import get_current_user
from models import *
from sqlmodel import select
from sqlalchemy.orm import selectinload

from connection import get_session

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectRead)
def create_project(project: ProjectCreate, session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Создать новый проект для текущего пользователя.

    Args:
        project (ProjectCreate): Данные нового проекта.
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        ProjectRead: Данные созданного проекта.
    """
    db_project = Project(**project.dict(), user_id=user.id)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project


@router.get("/", response_model=List[ProjectRead])
def read_projects(session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Получить список всех проектов текущего пользователя.

    Args:
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        List[ProjectRead]: Список проектов.
    """
    statement = (
        select(Project)
        .where(Project.user_id == user.id)
        .options(selectinload(Project.tasks))
    )
    return session.exec(statement).all()


@router.delete("/{project_id}")
def delete_project(project_id: int, session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Удалить проект по идентификатору.

    Args:
        project_id (int): Идентификатор проекта.
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        dict: Статус успешного удаления.

    Raises:
        HTTPException: Если проект не найден или пользователь не авторизован.
    """
    project = session.get(Project, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")
    session.delete(project)
    session.commit()
    return {"ok": True}


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, project_data: ProjectCreate, session=Depends(get_session),
                   user: User = Depends(get_current_user)):
    """
    Обновить данные проекта по идентификатору.

    Args:
        project_id (int): Идентификатор проекта.
        project_data (ProjectCreate): Новые данные проекта.
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        ProjectRead: Обновлённые данные проекта.

    Raises:
        HTTPException: Если проект не найден или пользователь не авторизован.
    """
    project = session.get(Project, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")
    for key, value in project_data.dict(exclude_unset=True).items():
        setattr(project, key, value)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

