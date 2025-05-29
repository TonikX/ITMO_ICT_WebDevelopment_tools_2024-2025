from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from connection import SessionLocal
from models.user_model import User, UserCreate, UserLogin, UserRead, UserUpdatePassword, UserUpdate
from util.auth import get_password_hash, verify_password, create_jwt_token, get_current_user

router = APIRouter()
def get_session():
    with SessionLocal() as session:
        yield session


@router.post("/register", response_model=UserRead, tags=["Users"])
def register_user(user_create: UserCreate, session: Session = Depends(get_session)):
    # Проверяем, существует ли пользователь с таким именем или email
    statement = select(User).where((User.username == user_create.username) | (User.email == user_create.email))
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with provided username or email already exists")
    
    # Хэшируем пароль
    hashed_password = get_password_hash(user_create.password)
    
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

@router.post("/login", tags=["Users"])
def login_user(user_login: UserLogin, session: Session = Depends(get_session)):
    # Поиск пользователя по username
    statement = select(User).where(User.username == user_login.username)
    user = session.exec(statement).first()
    
    # Если пользователь не найден или пароль неверен
    if not user or not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    # Генерация JWT-токена, содержащего id и username
    token = create_jwt_token({"user_id": user.id, "username": user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/{user_id}", response_model=UserRead, tags=["Users"])
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/{user_id}/password", response_model=UserRead, tags=["Users"])
def update_user_password(user_id: int, password_update: UserUpdatePassword, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Проверка старого пароля
    if not verify_password(password_update.old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password")
    

    user.hashed_password = get_password_hash(password_update.new_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.patch("/me", response_model=UserRead, tags=["Users"])
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user