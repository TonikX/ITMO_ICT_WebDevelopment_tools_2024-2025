import typing as tp

from fastapi import APIRouter, Depends, HTTPException, status
import uuid
from sqlmodel import Session, select

from core.validators import validate_username, validate_email, validate_age
from db.database import get_session
from db.models import User, Skill, UserSkill
from dependencies.admin import admin_required
from dependencies.auth import get_current_user
from schemas.error import Error
from schemas.user import UserResponse, UserUpdate, UserSkillsUpdate, ExtendedUserResponse

router = APIRouter()


@router.get("/me", response_model=ExtendedUserResponse)
def get_current_user_data(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_user_info(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    error = Error()

    if user_update.username is not None:
        validate_username(user_update.username.strip(), error, session)

    if user_update.email is not None:
        validate_email(user_update.email.strip(), error, session)

    if user_update.age is not None:
        validate_age(user_update.age, error)

    if error.is_error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": error.errors}
        )

    current_user.username = user_update.username.strip() if user_update.username is not None else current_user.username
    current_user.email = user_update.email.strip() if user_update.email is not None else current_user.email
    current_user.first_name = user_update.first_name.strip() if user_update.first_name is not None else current_user.first_name
    current_user.last_name = user_update.last_name.strip() if user_update.last_name is not None else current_user.last_name
    current_user.last_name = user_update.last_name.strip() if user_update.last_name is not None else current_user.last_name
    current_user.age = user_update.age if user_update.age is not None else current_user.age
    current_user.description = user_update.description.strip() if user_update.description is not None else current_user.description

    session.merge(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.patch("/skills")
def update_user_skills(
        skills_update: UserSkillsUpdate,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
):
    if skills_update.add:
        for item in skills_update.add:
            skill_obj = session.exec(select(Skill).where(Skill.id == item.skill_id)).first()
            if not skill_obj:
                continue
            existing_link = session.exec(select(UserSkill).where(UserSkill.user_id == current_user.id, UserSkill.skill_id == item.skill_id)).first()
            if existing_link:
                existing_link.proficiency = item.proficiency
            else:
                new_link = UserSkill(user_id=current_user.id, skill_id=item.skill_id, proficiency=item.proficiency)
                session.add(new_link)
    session.commit()

    if skills_update.remove:
        for skill_id in skills_update.remove:
            link = session.exec(select(UserSkill).where(UserSkill.user_id == current_user.id, UserSkill.skill_id == skill_id)).first()
            if link:
                session.delete(link)

    session.commit()
    return {"result": "success"}

# Admin
@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(admin_required)])
def get_user_info(user_id: str, session: Session = Depends(get_session)):
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid user id format."
        )
    user = session.exec(select(User).where(User.id == user_uuid)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse, dependencies=[Depends(admin_required)])
def update_user_info(user_id: str, user_update: UserUpdate, session: Session = Depends(get_session)):
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid user id format."
        )
    user = session.exec(select(User).where(User.id == user_uuid)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    error = Error()

    if user_update.username is not None:
        validate_username(user_update.username.strip(), error, session)

    if user_update.email is not None:
        validate_email(user_update.email.strip(), error, session)

    if user_update.age is not None:
        validate_age(user_update.age, error)

    if error.is_error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": error.errors}
        )

    user.username = user_update.username.strip() if user_update.username is not None else user.username
    user.email = user_update.email.strip() if user_update.email is not None else user.email
    user.first_name = user_update.first_name.strip() if user_update.first_name is not None else user.first_name
    user.last_name = user_update.last_name.strip() if user_update.last_name is not None else user.last_name
    user.last_name = user_update.last_name.strip() if user_update.last_name is not None else user.last_name
    user.age = user_update.age if user_update.age is not None else user.age
    user.description = user_update.description.strip() if user_update.description is not None else user.description

    session.merge(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/all", response_model=tp.List[UserResponse], dependencies=[Depends(admin_required)])
def get_all_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users
