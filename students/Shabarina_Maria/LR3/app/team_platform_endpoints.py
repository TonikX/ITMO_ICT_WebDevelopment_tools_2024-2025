from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.orm import joinedload
from app.connection import get_session
from app.user_endpoints import auth_handler
from app.models import *
from app.read_models import *
from typing_extensions import TypedDict
from typing import List


team_platform_router = APIRouter(dependencies=[Depends(auth_handler.get_authenticated_user)])


@team_platform_router.post("/skill", tags=['Skill'], description='Создание нового навыка')
def skill_create(skill: Skill, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "data": Skill}):
    skill = Skill.model_validate(skill)
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return {"status": 200, "data": skill}


@team_platform_router.delete("/skill/delete{skill_id}", tags=['Skill'], description='Удаление навыка')
def skill_delete(skill_id: int, session=Depends(get_session)):
    skill = session.get(Skill, skill_id)
    name = skill.title
    if not skill:
        raise HTTPException(status_code=404, detail="Навык не обнаружен")
    session.delete(skill)
    session.commit()
    return {f"Навык {name} удален"}


@team_platform_router.patch("/skill/patch/{skill_id}", tags=['Skill'], description='Редактирование навыка')
def skill_update(skill_id: int, skill: Skill, session=Depends(get_session)) -> Skill:
    given_skill = session.get(Skill, skill_id)
    if not given_skill:
        raise HTTPException(status_code=404, detail="Навык не обнаружен")
    skill_data = skill.model_dump(exclude_unset=True)
    for key, value in skill_data.items():
        setattr(given_skill, key, value)
    session.add(given_skill)
    session.commit()
    session.refresh(given_skill)
    return given_skill


@team_platform_router.get("/skills_list", tags=['Skill'], description='Список всех навыков')
def skills_list(session=Depends(get_session)) -> List[Skill]:
    return session.query(Skill).all()


@team_platform_router.post("/user_skill", tags=['User Skill'], description='Создания навыка для пользоваеля')
def user_skill_create(user_skill: UserSkillDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "data": UserSkill}):
    user_skill = UserSkill.model_validate(user_skill)
    session.add(user_skill)
    session.commit()
    session.refresh(user_skill)
    return {"status": 200, "data": user_skill}


@team_platform_router.delete("/user_skill/delete{user_skill_id}", tags=['User Skill'], description='Удаление навыка пользователя')
def user_skill_delete(user_skill_id: int, session=Depends(get_session)):
    user_skill = session.get(UserSkill, user_skill_id)
    user = user_skill.user
    skill = user_skill.skill
    if not user_skill:
        raise HTTPException(status_code=404, detail="Навык пользователя не обнаружен")
    session.delete(user_skill)
    session.commit()
    return {f"Навык {skill} удален для пользователя {user}"}


@team_platform_router.patch("/user_skill/patch/{user_skill_id}", tags=['User Skill'], description='Редактирование навыка пользователя')
def user_skill_update(user_skill_id: int, user_skill: UserSkill, session=Depends(get_session)) -> UserSkill:
    given_user_skill = session.get(UserSkill, user_skill_id)
    if not given_user_skill:
        raise HTTPException(status_code=404, detail="Навык пользователя не обнаружен")
    given_user_skill_data = user_skill.model_dump(exclude_unset=True)
    for key, value in given_user_skill_data.items():
        setattr(given_user_skill, key, value)
    session.add(given_user_skill)
    session.commit()
    session.refresh(given_user_skill)
    return given_user_skill


@team_platform_router.get("/users_skills_list", tags=['User Skill'], description='Список всех навыков пользователей')
def users_skills_list(session=Depends(get_session)) -> List[UserSkillRead]:
    user_skills = (
        session.query(UserSkill)
        .options(joinedload(UserSkill.user), joinedload(UserSkill.skill))
        .all()
    )

    result = []
    for us in user_skills:
        result.append(UserSkillRead(
            id=us.id,
            level=us.level,
            user_id=us.user_id,
            skill_id=us.skill_id,
            user_name=us.user.name if us.user else None,
            skill_title=us.skill.title if us.skill else None
        ))

    return result


@team_platform_router.post("/position", tags=['Position'], description='Создание должности')
def position_create(position: Position, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "data": Position}):
    position = Position.model_validate(position)
    session.add(position)
    session.commit()
    session.refresh(position)
    return {"status": 200, "data": position}


@team_platform_router.delete("/position/delete{position_id}", tags=['Position'], description='Удаление должности')
def position_delete(position_id: int, session=Depends(get_session)):
    position = session.get(Position, position_id)
    name = position.title
    if not position:
        raise HTTPException(status_code=404, detail="Должность не обнаружена")
    session.delete(position)
    session.commit()
    return {f"Должность {name} удалена"}


@team_platform_router.patch("/position/patch/{position_id}", tags=['Position'], description='Редактирование должности')
def position_update(position_id: int, position: Position, session=Depends(get_session)) -> Position:
    given_position = session.get(Position, position_id)
    if not given_position:
        raise HTTPException(status_code=404, detail="Должность не обнаружена")
    skill_data = position.model_dump(exclude_unset=True)
    for key, value in skill_data.items():
        setattr(given_position, key, value)
    session.add(given_position)
    session.commit()
    session.refresh(given_position)
    return given_position


@team_platform_router.get("/positions_list", tags=['Position'], description='Список всех должностей')
def positions_list(session=Depends(get_session)) -> List[Position]:
    return session.query(Position).all()


@team_platform_router.post("/user_position", tags=['User Position'], description='Создание должности для пользователя')
def user_position_create(user_position: UserPositionDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "data": UserPosition}):
    user_position = UserPosition.model_validate(user_position)
    session.add(user_position)
    session.commit()
    session.refresh(user_position)
    return {"status": 200, "data": user_position}


@team_platform_router.delete("/user_position/delete{user_position_id}", tags=['User Position'], description='Удаление навыка должности пользователя')
def user_positions_delete(user_position_id: int, session=Depends(get_session)):
    user_position = session.get(UserPosition, user_position_id)
    user = user_position.user
    position = user_position.position
    if not user_position:
        raise HTTPException(status_code=404, detail="Должность пользователя не обнаружена")
    session.delete(user_position)
    session.commit()
    return {f"Должность {position} пользователя {user} удалена"}


@team_platform_router.patch("/user_position/patch/{user_position_id}", tags=['User Position'], description='Редактирование должности пользователя')
def user_positions_update(user_position_id: int, user_position: UserPosition, session=Depends(get_session)) -> UserPosition:
    given_user_position = session.get(UserPosition, user_position_id)
    if not given_user_position:
        raise HTTPException(status_code=404, detail="Должность пользователя не обнаружена")
    given_user_skill_data = user_position.model_dump(exclude_unset=True)
    for key, value in given_user_skill_data.items():
        setattr(given_user_position, key, value)
    session.add(given_user_position)
    session.commit()
    session.refresh(given_user_position)
    return given_user_position


@team_platform_router.get("/user_positions_list", tags=['User Position'], description='Список всех позиций пользователей')
def user_positions_list(session=Depends(get_session)) -> List[UserPositionRead]:
    user_positions = (
        session.query(UserPosition)
        .options(joinedload(UserPosition.user), joinedload(UserPosition.position))
        .all()
    )
    result = []
    for pos in user_positions:
        result.append(UserPositionRead(
            id=pos.id,
            experience=pos.experience,
            user_id=pos.user_id,
            position_id=pos.position_id,
            user_name=pos.user.name,
            position_title=pos.position.title
        ))
    return result


@team_platform_router.post("/project", tags=['Project'], description='Создание проекта')
def project_create(project: ProjectDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "data": Project}):
    project = Project.model_validate(project)
    session.add(project)
    session.commit()
    session.refresh(project)
    return {"status": 200, "data": project}


@team_platform_router.delete("/project/delete{project_id}", tags=['Project'], description='Удаление проекта')
def project_delete(project_id: int, session=Depends(get_session)):
    project = session.get(Project, project_id)
    name = project.title
    if not project:
        raise HTTPException(status_code=404, detail="Проект не обнаружен")
    session.delete(project)
    session.commit()
    return {f"Проект {name} удален"}


@team_platform_router.patch("/project/patch/{project_id}", tags=['Project'], description='Редактирование проекта')
def project_update(project_id: int, project: Project, session=Depends(get_session)) -> Project:
    given_project = session.get(Project, project_id)
    if not given_project:
        raise HTTPException(status_code=404, detail="Проект не обнаружен")
    project_data = project.model_dump(exclude_unset=True)
    for key, value in project_data.items():
        setattr(given_project, key, value)
    session.add(given_project)
    session.commit()
    session.refresh(given_project)
    return given_project


@team_platform_router.get("/project_list", tags=['Project'], description='Список всех проектов')
def project_list(session=Depends(get_session)) -> List[Project]:
    return session.query(Project).all()


@team_platform_router.post("/participation", tags=['Participation'], description='Создание участия в проекте')
def participation_create(participation: ParticipationDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "data": Participation}):
    participation = Participation.model_validate(participation)
    session.add(participation)
    session.commit()
    session.refresh(participation)
    return {"status": 200, "data": participation}


@team_platform_router.delete("/participation/delete{participation_id}", tags=['Participation'], description='Удаление участия в проекте')
def participation_delete(participation_id: int, session=Depends(get_session)):
    participation = session.get(Participation, participation_id)
    project = participation.project.title
    user = participation.user.name
    if not participation:
        raise HTTPException(status_code=404, detail="Участие в проекте не обнаружено")
    session.delete(participation)
    session.commit()
    return {f"Участие в проекте {project} пользователя {user} удалено"}


@team_platform_router.patch("/participation/patch/{participation_id}", tags=['Participation'], description='Редактирование участия в проекте')
def participation_update(participation_id: int, participation: Participation, session=Depends(get_session)) -> Participation:
    given_participation = session.get(Participation, participation_id)
    if not given_participation:
        raise HTTPException(status_code=404, detail="Участие в проекте не обнаружено")
    project_data = participation.model_dump(exclude_unset=True)
    for key, value in project_data.items():
        setattr(given_participation, key, value)
    session.add(given_participation)
    session.commit()
    session.refresh(given_participation)
    return given_participation


@team_platform_router.get("/participation_list", tags=['Participation'], description='Список всех участников проектов')
def participation_list(session=Depends(get_session)) -> List[ParticipationRead]:
    participation = (
        session.query(Participation)
        .options(joinedload(Participation.user), joinedload(Participation.project))
        .all()
    )
    result = []
    for part in participation:
        result.append(ParticipationRead(
            id=part.id,
            user_id=part.user_id,
            project_id=part.project_id,
            user_name=part.user.name,
            project_title=part.project.title
        ))
    return result


@team_platform_router.get("/all_project_participants", tags=['Participation'], description='Состав участников проекта')
def all_project_participants(project_id: int, session=Depends(get_session)) -> List[ProjectParticipantsRead]:
    participants = (session.query(Participation).filter(Participation.project_id == project_id).all())
    return [
        ProjectParticipantsRead(
            id=part.id,
            user_id=part.user_id,
            user_name=part.user.name,
        ) for part in participants
    ]


@team_platform_router.post("/task", tags=['Task'], description='Создание задач для проектов')
def task_create(task: TaskDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "data": Task}):
    task = Task.model_validate(task)
    session.add(task)
    session.commit()
    session.refresh(task)
    return {"status": 200, "data": task}


@team_platform_router.delete("/task/delete{task_id}", tags=['Task'], description='Удаление задачи')
def task_delete(task_id: int, session=Depends(get_session)):
    task = session.get(Task, task_id)
    description = task.description
    project = task.project
    if not task:
        raise HTTPException(status_code=404, detail="Задача не обнаружена")
    session.delete(task)
    session.commit()
    return {f"Задача '{description}' для проекта {project} удалена"}


@team_platform_router.patch("/task/patch/{task_id}", tags=['Task'], description='Редактирование задачи')
def task_update(task_id: int, task: Task, session=Depends(get_session)) -> Task:
    given_task = session.get(Task, task_id)
    if not given_task:
        raise HTTPException(status_code=404, detail="Задача не обнаружена")
    project_data = task.model_dump(exclude_unset=True)
    for key, value in project_data.items():
        setattr(given_task, key, value)
    session.add(given_task)
    session.commit()
    session.refresh(given_task)
    return given_task


@team_platform_router.get("/tasks_list", tags=['Task'], description='Список всех задач')
def tasks_list(session=Depends(get_session)) -> List[Task]:
    return session.query(Task).all()


@team_platform_router.get("/tasks_for_user", tags=['Task'], description='Список всех задач пользователя')
def tasks_for_user(user_id: int, session=Depends(get_session)) -> List[UserTasksRead]:
    tasks = (session.query(Task).filter(Task.user_id == user_id).all())
    return [
        UserTasksRead(
            id=task.id,
            description=task.description,
            deadline=task.deadline,
            status=task.status,
            project_title=task.project.title
        ) for task in tasks
    ]
