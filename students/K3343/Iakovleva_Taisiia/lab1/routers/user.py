from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from typing import List
from models.models import User, UserDefault, UserCreate, UserRead, Account, Budget, Transaction, Transfer, ChangePassword
from auth.connection import get_session
from auth.jwt_utils import get_password_hash, verify_password, create_jwt_token
from datetime import timedelta
from auth.auth import bearer_scheme

from auth.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserRead)
def register(user: UserCreate, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.email == user.email)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, username=user.username, hashed_password=hashed_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.post("/login")
def login(user: UserCreate, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.email == user.email)).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token = create_jwt_token(data={"sub": str(db_user.id)}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/change-password", dependencies=[Depends(bearer_scheme)])
def change_password(
    request: ChangePassword,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # проверка старого пароля
    if not verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    # cмена на новый пароль
    current_user.hashed_password = get_password_hash(request.new_password)
    session.add(current_user)
    session.commit()

    return {"message": "Password changed successfully"}

@router.get("/")
def users_list(session=Depends(get_session)) -> List[User]:
    return session.exec(select(User)).all()

@router.patch("/{user_id}", response_model=User)
def update_user(user_id: int, user: UserDefault, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    user_data = user.model_dump(exclude_unset=True)
    user_data.pop("hashed_password", None)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    accounts = session.exec(select(Account).where(Account.user_id == user_id)).all()
    for account in accounts:
        transactions = session.exec(select(Transaction).where(Transaction.account_id == account.id)).all()
        for transaction in transactions:
            session.delete(transaction)
        transfers = session.exec(select(Transfer).where(Transfer.from_account_id == account.id)).all()
        for transfer in transfers:
            session.delete(transfer)

   
    for account in accounts:
        session.delete(account)
    budgets = session.exec(select(Budget).where(Budget.user_id == user_id)).all()
    for budget in budgets:
        session.delete(budget)
  
    session.delete(user)
    session.commit()
    return {"ok": True}

@router.get("/users-with-accounts")
def get_users_with_accounts(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    result = []

    for user in users:
        session.refresh(user, attribute_names=["accounts"])
        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "accounts": [
                {
                    "id": acc.id,
                    "name": acc.name,
                    "balance": acc.balance,
                    "is_goal": acc.is_goal,
                    "target_amount": acc.target_amount
                }
                for acc in user.accounts
            ]
        })

    return result

@router.get("/users-with-budgets")
def get_users_with_budgets(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    result = []

    for user in users:
        budgets = [{"id": b.id, "category": b.category, "month": b.month, "year": b.year, "limit": b.limit} for b in user.shared_budgets]
        result.append({
            "user_id": user.id,
            "username": user.username,
            "budgets": budgets
        })

    return result