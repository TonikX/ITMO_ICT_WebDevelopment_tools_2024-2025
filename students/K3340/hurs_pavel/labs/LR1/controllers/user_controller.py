
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models.user_model import User, UserCreate, UserLogin, UserRead, UserUpdatePassword
from connection import SessionLocal
from util import auth

router = APIRouter()
def get_session():
    with SessionLocal() as session:
        yield session

@router.post("/register", response_model=UserRead)
def register(user_create: UserCreate, session: Session = Depends(get_session)):
    # Проверяем, существует ли уже пользователь с таким username
    statement = select(User).where(User.username == user_create.username)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username already registered")
    
    # Хэширование пароля вручную (без сторонних библиотек)
    hashed_password = auth.get_password_hash(user_create.password)
    
    # Создаем нового пользователя
    new_user = User(
        username=user_create.username,
        hashed_password=hashed_password,
        email=user_create.email,
        bio=user_create.bio
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.post("/login")
def login(user_login: UserLogin, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == user_login.username)
    user = session.exec(statement).first()
    if not user or not auth.verify_password(user_login.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Incorrect username or password")
    
    # Генерируем JWT-токен с полезной нагрузкой
    token = auth.create_jwt_token({"user_id": user.id, "username": user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    return user

@router.put("/users/{user_id}/password", response_model=UserRead)
def update_password(user_id: int, password_update: UserUpdatePassword, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    # Проверка соответствия старого пароля
    if not auth.verify_password(password_update.old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Incorrect old password")
    
    # Хэширование нового пароля и сохранение пользователя
    user.hashed_password = auth.get_password_hash(password_update.new_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/users", response_model=list[UserRead])
def list_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users, status.HTTP_200_OK