from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import Form
from sqlalchemy.orm import selectinload
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import *
from models import User
from sqlmodel import Session, select
from schemas import *
from connection import get_session

router = APIRouter(prefix="/users", tags=["Users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/register", response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_session)):
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    # Проверка пользователя в базе данных
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=list[UserOut])
def get_all_users(db: Session = Depends(get_session)):
    return db.query(User).all()


@router.post("/change-password")
def change_password(
    old_password: str = Form(...),
    new_password: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    current_user.hashed_password = hash_password(new_password)
    db.commit()
    return {"message": "Password changed successfully"}

@router.put("/update")
def update_user(
    username: str = Form(...),
    email: str = Form(...),
    bio: str = Form(...),
    age: int = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    if current_user.id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own data")

    if username:
        current_user.username = username
    if email:
        current_user.email = email
    if bio:
        current_user.bio = bio
    if age:
        current_user.age = age

    db.commit()
    db.refresh(current_user)

    return {"message": "User data updated successfully", "user": current_user}

@router.get("", response_model=List[User])
def get_users(db: Session = Depends(get_session)):
    users = db.exec(select(User)).all()
    return users

@router.post("", response_model=User)
def create_user(user: User, db: Session = Depends(get_session)):
    db_user = User(username=user.username, email=user.email, hashed_password=user.hashed_password, age=user.age, bio=user.bio)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_session)):
    db_user = db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_session)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@router.get("/{user_id}/with_trips", response_model=UserWithTrips)
def get_user_with_trips(user_id: int, db: Session = Depends(get_session)):
    db_user = db.exec(select(User).where(User.id == user_id).options(selectinload(User.trips))).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user