from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime
from ..database import get_session
from ..models import User, Role, UserRole
from ..schemas import UserCreate, UserRead, Token, RoleRead
from ..auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserRead)
def register(user_in: UserCreate, session: Session = Depends(get_session)):
    user_role = session.exec(select(Role).where(Role.name == "user")).first()
    if session.exec(select(User).where(User.username == user_in.username)).first():
        raise HTTPException(400, "Username taken")
    user = User(
        username=user_in.username,
        password_hash=hash_password(user_in.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    user_role = UserRole(user_id=user.id, role_id=user_role.id)
    session.add(user_role)
    session.commit()
    session.refresh(user)
    return UserRead(
        id=user.id,
        username=user.username,
        created_at=user.created_at,
        roles=[]
    )

@router.post("/login", response_model=Token)
def login(user_in: UserCreate, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == user_in.username)).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(401, "Bad credentials")
    access_token = create_access_token({"sub": user.id})
    return Token(access_token=access_token)


@router.get("/me", response_model=UserRead)
def me(current: User = Depends(get_current_user)):
    return UserRead(
        id=current.id,
        username=current.username,
        created_at=current.created_at,
        roles=[ur.role.name for ur in current.roles]
    )


@router.get("/", response_model=list[UserRead])
def list_users(
    session: Session = Depends(get_session),
    current: User = Depends(get_current_user)
):
    user_roles = [ur.role.name for ur in current.roles]
    if "admin" not in user_roles:
        raise HTTPException(status_code=403, detail="Admins only")

    users = session.exec(select(User)).all()
    return [
        UserRead(
            id=u.id,
            username=u.username,
            created_at=u.created_at,
            roles=[ur.role.name for ur in u.roles]
        )
        for u in users
    ]


@router.post("/{user_id}/change_password", response_model=None)
def change_password(
    user_id: int,
    new: UserCreate,
    session: Session = Depends(get_session),
    current: User = Depends(get_current_user)
):
    if current.id != user_id:
        raise HTTPException(403, "Cannot change others'™ password")
    user = session.get(User, user_id)
    user.password_hash = hash_password(new.password)
    session.add(user)
    session.commit()
    return