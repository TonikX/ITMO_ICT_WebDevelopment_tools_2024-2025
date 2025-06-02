from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from common.models.user import User
from app.schemas.user import UserCreate, UserOut, UserLogin, ChangePassword, UserUpdateUsername
from app.crud.user import (
    get_user_by_username,
    get_user_by_email,
    create_user,
    get_user,
    get_users,
    update_user_password,
    update_user_username,
    delete_user,
)
from app.auth.security import verify_password
from app.auth.jwt import create_access_token
from app.database import SessionLocal
from app.auth.deps import get_db, get_current_user, oauth2_scheme

router = APIRouter(tags=["Users"])


@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username) or get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Username or email already registered")
    return create_user(db, user)

# @router.post("/login")
@router.post("/login", summary="Get JWT token", description="Use this endpoint to authenticate.")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, form_data.username)
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": db_user.username})
    print("Login as:", db_user.username, type(db_user.username))
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=list[UserOut])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    return get_users(db, skip=skip, limit=limit)

@router.get("/users/{user_id}", response_model=UserOut)
def read_user_by_id(user_id: int, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.post("/users/change-password")
def change_password(
    change: ChangePassword,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    current_user = get_current_user(token=token, db=db)
    try:
        if not verify_password(change.old_password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Old password is incorrect")
        update_user_password(db, current_user, change.new_password)
        return {"msg": "Password updated successfully"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/users/update-username", response_model=UserOut)
def update_username(
        update_data: UserUpdateUsername,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if get_user_by_username(db, update_data.new_username):
        raise HTTPException(status_code=400, detail="Username already taken")

    updated_user = update_user_username(db, current_user, update_data.new_username)
    return updated_user


@router.delete("/users/me")
def delete_user_me(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    delete_user(db, current_user)
    return {"msg": "User deleted successfully"}
