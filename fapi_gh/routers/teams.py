from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional

from db.db import get_session
from models.models import Team, TeamBase, TeamWithMembers, UserResponse, TeamMember, User, Hackathon
from utils.auth import get_current_user

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/", response_model=TeamWithMembers, status_code=status.HTTP_201_CREATED)
def create_team(
        team: TeamBase,
        session: Session = Depends(get_session),
        current_user: Optional[User] = Depends(get_current_user)
):
    """Создание новой команды."""
    try:
        # Проверка существования хакатона
        hackathon = session.get(Hackathon, team.hackathon_id)
        if not hackathon:
            raise HTTPException(status_code=404, detail="Хакатон не найден")

        # Проверка существования создателя
        creator = session.get(User, team.creator_id)
        if not creator:
            raise HTTPException(status_code=404, detail="Пользователь-создатель не найден")

        # Если пользователь аутентифицирован, проверяем что он создает команду от своего имени
        if current_user and current_user.id != team.creator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы можете создать команду только от своего имени"
            )

        # Создание команды
        db_team = Team.from_orm(team)
        session.add(db_team)
        session.commit()
        session.refresh(db_team)

        # Автоматическое добавление создателя как капитана команды
        team_member = TeamMember(
            user_id=team.creator_id,
            team_id=db_team.id,
            role="капитан",
            is_approved=True  # Создатель автоматически подтверждается
        )
        session.add(team_member)
        session.commit()

        # Формируем ответ в нужном формате
        user_response = UserResponse(
            id=creator.id,
            name=creator.name,
            email=creator.email,
            phone=creator.phone,
            bio=creator.bio,
            skills=creator.skills,
            registration_date=creator.registration_date
        )

        # Создаем TeamWithMembers объект
        team_with_members = TeamWithMembers(
            id=db_team.id,
            name=db_team.name,
            description=db_team.description,
            hackathon_id=db_team.hackathon_id,
            creator_id=db_team.creator_id,
            creation_date=db_team.creation_date,
            is_active=db_team.is_active,
            members=[user_response]
        )

        return team_with_members
    except Exception as e:
        print(f"Ошибка при создании команды: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.get("/", response_model=List[TeamWithMembers])
def get_teams(
        skip: int = 0,
        limit: int = 100,
        hackathon_id: Optional[int] = None,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
        session: Session = Depends(get_session)
):
    """Получение списка команд с возможностью фильтрации."""
    try:
        query = select(Team)

        if hackathon_id:
            query = query.where(Team.hackathon_id == hackathon_id)
        if name:
            query = query.where(Team.name.contains(name))
        if is_active is not None:
            query = query.where(Team.is_active == is_active)

        db_teams = session.exec(query.offset(skip).limit(limit)).all()

        # Создаем ответ в правильном формате
        result = []
        for team in db_teams:
            # Получаем пользователей для каждой команды
            members_query = select(TeamMember).where(TeamMember.team_id == team.id)
            team_members = session.exec(members_query).all()

            members_list = []
            for tm in team_members:
                # Получаем данные пользователя
                user = session.get(User, tm.user_id)
                if user:
                    # Создаем UserResponse объект
                    user_response = UserResponse(
                        id=user.id,
                        name=user.name,
                        email=user.email,
                        phone=user.phone,
                        bio=user.bio,
                        skills=user.skills,
                        registration_date=user.registration_date
                    )
                    members_list.append(user_response)

            # Создаем TeamWithMembers объект
            team_with_members = TeamWithMembers(
                id=team.id,
                name=team.name,
                description=team.description,
                hackathon_id=team.hackathon_id,
                creator_id=team.creator_id,
                creation_date=team.creation_date,
                is_active=team.is_active,
                members=members_list
            )
            result.append(team_with_members)

        return result
    except Exception as e:
        # Логирование ошибки для отладки
        print(f"Ошибка при получении команд: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.get("/{team_id}", response_model=TeamWithMembers)
def get_team(team_id: int, session: Session = Depends(get_session)):
    """Получение информации о команде по ID."""
    try:
        team = session.get(Team, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Команда не найдена")

        # Получаем пользователей для команды
        members_query = select(TeamMember).where(TeamMember.team_id == team.id)
        team_members = session.exec(members_query).all()

        members_list = []
        for tm in team_members:
            # Получаем данные пользователя
            user = session.get(User, tm.user_id)
            if user:
                # Создаем UserResponse объект
                user_response = UserResponse(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    phone=user.phone,
                    bio=user.bio,
                    skills=user.skills,
                    registration_date=user.registration_date
                )
                members_list.append(user_response)

        # Создаем TeamWithMembers объект
        team_with_members = TeamWithMembers(
            id=team.id,
            name=team.name,
            description=team.description,
            hackathon_id=team.hackathon_id,
            creator_id=team.creator_id,
            creation_date=team.creation_date,
            is_active=team.is_active,
            members=members_list
        )

        return team_with_members
    except Exception as e:
        print(f"Ошибка при получении команды: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.put("/{team_id}", response_model=TeamWithMembers)
def update_team(
        team_id: int,
        team_data: TeamBase,
        session: Session = Depends(get_session),
        current_user: Optional[User] = Depends(get_current_user)
):
    """Обновление данных команды."""
    try:
        db_team = session.get(Team, team_id)
        if not db_team:
            raise HTTPException(status_code=404, detail="Команда не найдена")

        # Проверка прав доступа, если пользователь аутентифицирован
        if current_user and db_team.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только создатель команды может обновлять её данные"
            )

        team_dict = team_data.dict(exclude_unset=True)
        for key, value in team_dict.items():
            setattr(db_team, key, value)

        session.add(db_team)
        session.commit()
        session.refresh(db_team)

        # Формируем ответ в нужном формате
        members_query = select(TeamMember).where(TeamMember.team_id == team_id)
        team_members = session.exec(members_query).all()

        members_list = []
        for tm in team_members:
            user = session.get(User, tm.user_id)
            if user:
                user_response = UserResponse(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    phone=user.phone,
                    bio=user.bio,
                    skills=user.skills,
                    registration_date=user.registration_date
                )
                members_list.append(user_response)

        team_with_members = TeamWithMembers(
            id=db_team.id,
            name=db_team.name,
            description=db_team.description,
            hackathon_id=db_team.hackathon_id,
            creator_id=db_team.creator_id,
            creation_date=db_team.creation_date,
            is_active=db_team.is_active,
            members=members_list
        )

        return team_with_members
    except Exception as e:
        print(f"Ошибка при обновлении команды: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
        team_id: int,
        session: Session = Depends(get_session),
        current_user: Optional[User] = Depends(get_current_user)
):
    """Удаление команды."""
    try:
        db_team = session.get(Team, team_id)
        if not db_team:
            raise HTTPException(status_code=404, detail="Команда не найдена")

        # Проверка прав доступа, если пользователь аутентифицирован
        if current_user and db_team.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только создатель команды может удалить её"
            )

        session.delete(db_team)
        session.commit()
        return None
    except Exception as e:
        print(f"Ошибка при удалении команды: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )