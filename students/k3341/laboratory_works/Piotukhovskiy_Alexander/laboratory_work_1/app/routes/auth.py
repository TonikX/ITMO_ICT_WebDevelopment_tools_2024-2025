from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import or_
from sqlmodel import Session, select

from core import auth
from core.auth import hash_password, verify_password
from core.validators import validate_registration, validate_password
from db.database import get_session
from db.models import User
from dependencies.auth import get_current_user
from schemas.error import Error
from schemas.user import *

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserAuthResponse)
def register(user_data: UserRegistration, session: Session = Depends(get_session)):
    error = Error()

    validate_registration(user_data, error, session)

    if error.is_error:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"errors": error.errors},
        )

    hashed_password = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        age=user_data.age,
        description=user_data.description,
        password_hash=hashed_password,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    token = auth.create_access_token(new_user.id)
    user = UserResponse.model_validate(new_user)

    return UserAuthResponse(user=user, access_token=token)


@router.post("/login", response_model=UserAuthResponse)
def login(user_data: UserLogin, session: Session = Depends(get_session)):
    login_input = user_data.login.strip()
    user = session.exec(select(User).where(or_(User.email == login_input, User.username == login_input))).first()

    if not user or not auth.verify_password(user_data.password, user.password_hash):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid credentials"}
        )

    token = auth.create_access_token(user.id)
    user = UserResponse.model_validate(user)
    return UserAuthResponse(user=user, access_token=token)


@router.put("/password")
def change_password(
        password_data: ChangePasswordRequest,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
):
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Old password is incorrect."
        )

    error = Error()
    new_password = password_data.new_password
    if new_password == password_data.old_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New password is equal to the old password."
        )

    validate_password(new_password, error)

    if error.is_error:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"errors": error.errors},
        )

    new_hashed_pwd = hash_password(new_password)
    current_user.password_hash = new_hashed_pwd
    session.merge(current_user)
    session.commit()
    session.refresh(current_user)

    return {"message": "Password changed successfully."}