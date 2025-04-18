from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.connections import get_session
from app.models import User, UserRead, UserUpdatePassword
from app.core.security import verify_password, hash_password
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=User)
def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/", response_model=list[User])
def get_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()

# GET /users/me
@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

# GET /users/
@router.get("/", response_model=list[UserRead])
def list_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()

# PUT /users/password
@router.put("/password")
def change_password(
    data: UserUpdatePassword,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password")

    current_user.hashed_password = hash_password(data.new_password)
    session.add(current_user)
    session.commit()
    return {"message": "Password changed successfully"}