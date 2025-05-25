from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.jwt import get_current_user, get_db
from models.user import User
from schemas.user import UserListRead, ChangePassword
from core import hash_password, verify_password

router = APIRouter()


@router.get("/", response_model=list[UserListRead])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.post("/change-password")
def change_password(
    data: ChangePassword,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user.id).first()
    if not user or not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный старый пароль")

    user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "Пароль успешно изменён"}
