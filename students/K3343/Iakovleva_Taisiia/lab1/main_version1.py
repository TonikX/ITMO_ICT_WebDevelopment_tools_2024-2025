# from fastapi import FastAPI, HTTPException
# from typing import Optional, List
# from models import *
# from typing_extensions import TypedDict
# from lab1.connection_version1 import *
# from sqlmodel import select
# from lab1.auth_version1 import get_password_hash, verify_password, create_access_token
# from fastapi.security import OAuth2PasswordRequestForm
# from datetime import timedelta

# app = FastAPI()

# @app.on_event("startup")
# def on_startup():
#     init_db()

# @app.post("/register", response_model=UserRead)
# def register(user: UserCreate, session: Session = Depends(get_session)):
#     db_user = session.exec(select(User).where(User.email == user.email)).first()
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")

#     hashed_password = get_password_hash(user.password)
#     new_user = User(email=user.email, username=user.username, hashed_password=hashed_password)
#     session.add(new_user)
#     session.commit()
#     session.refresh(new_user)
#     return new_user

# @app.post("/login")
# def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
#     user = session.exec(select(User).where(User.email == form_data.username)).first()
#     if not user or not verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(status_code=400, detail="Incorrect email or password")

#     access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(minutes=30))
#     return {"access_token": access_token, "token_type": "bearer"}

# @app.get("/user_list")
# def users_list(session=Depends(get_session)) -> List[User]:
#     return session.exec(select(User)).all()

# @app.get("/User/{user_id}", response_model=User)
# def get_user(user_id: int, session: Session = Depends(get_session)) -> User:
#     user = session.get(User, user_id)
#     return user

# @app.post("/user")
# def create_user(user: UserDefault, session: Session = Depends(get_session)):
#     user = User.model_validate(user)
#     session.add(user)
#     session.commit()
#     session.refresh(user)
#     return {"status": 200, "data": user}


# @app.patch("/users/{user_id}", response_model=User)
# def update_user(user_id: int, user: UserDefault, session: Session = Depends(get_session)):
#     db_user = session.get(User, user_id)
#     user_data = user.model_dump(exclude_unset=True)
#     for key, value in user_data.items():
#         setattr(db_user, key, value)
#     session.add(db_user)
#     session.commit()
#     session.refresh(db_user)
#     return db_user

# @app.delete("/users/{user_id}")
# def delete_user(user_id: int, session: Session = Depends(get_session)):
#     user = session.get(User, user_id)
#     session.delete(user)
#     session.commit()
#     return {"ok": True}

# # ============ ACCOUNTS ============


# @app.get("/accounts")
# def accounts_list(session: Session = Depends(get_session)) -> List[Account]:
#     return session.exec(select(Account)).all()

# @app.post("/accounts")
# def create_account(account: AccountDefault, session: Session = Depends(get_session)):
#     if account.is_goal and account.target_amount is None:
#         raise HTTPException(status_code=400, detail="Goal accounts must have target_amount")

#     if not account.is_goal:
#         account.target_amount = None

#     account = Account.model_validate(account)
#     session.add(account)
#     session.commit()
#     session.refresh(account)
#     return {"status": 200, "data": account}


# @app.delete("/accounts/{account_id}")
# def delete_account(account_id: int, session: Session = Depends(get_session)):
#     account = session.get(Account, account_id)
#     session.delete(account)
#     session.commit()
#     return {"ok": True}

# # ============ TRANSACTIONS ============

# @app.get("/transactions", response_model=List[Transaction])
# def list_transactions(session: Session = Depends(get_session)):
#     return session.exec(select(Transaction)).all()

# @app.post("/transactions", response_model=dict)
# def create_transaction(transaction: TransactionDefault, session: Session = Depends(get_session)):
#     account = session.get(Account, transaction.account_id)

#     if not account:
#         raise HTTPException(status_code=404, detail="Account not found")

#     # --- Проверка бюджета ---
#     budget = session.exec(
#         select(Budget)
#         .where(Budget.user_id == account.user_id)
#         .where(Budget.category == transaction.category)
#         .where(Budget.month == transaction.date.month)
#         .where(Budget.year == transaction.date.year)
#     ).first()

#     warning: Optional[str] = None

#     if budget and transaction.category != CategoryType.salary:
#         start_of_month = datetime(transaction.date.year, transaction.date.month, 1)
#         end_of_month = (
#             datetime(transaction.date.year, transaction.date.month + 1, 1)
#             if transaction.date.month < 12
#             else datetime(transaction.date.year + 1, 1, 1)
#         )

#         # Получаем все предыдущие транзакции за этот месяц
#         total_spent = session.exec(
#             select(Transaction)
#             .where(Transaction.account_id == account.id)
#             .where(Transaction.category == transaction.category)
#             .where(Transaction.date >= start_of_month)
#             .where(Transaction.date < end_of_month)
#         ).all()

#         spent_sum = sum(t.amount for t in total_spent)

#         if spent_sum + transaction.amount > budget.limit:
#             warning = (
#                 f"💸 Budget exceeded: {(spent_sum + transaction.amount):.2f} > limit {budget.limit:.2f}"
#             )

#     # --- Обновляем баланс ---
#     if transaction.category == CategoryType.salary:
#         account.balance += transaction.amount
#     else:
#         if account.balance < transaction.amount:
#             raise HTTPException(status_code=400, detail="Insufficient funds")
#         account.balance -= transaction.amount

#     session.add(account)  # Обновляем счёт

#     # --- Сохраняем транзакцию ---
#     transaction = Transaction.model_validate(transaction)
#     session.add(transaction)
#     session.commit()
#     session.refresh(transaction)

#     return {
#         "transaction": transaction,
#         "warning": warning
#     }


# # ============ BUDGETS ============

# @app.get("/budgets", response_model=List[BudgetStats])
# def list_budgets(session: Session = Depends(get_session)):
#     budgets = session.exec(select(Budget)).all()
#     result = []

#     for budget in budgets:
#         start_of_month = datetime(budget.year, budget.month, 1)
#         end_of_month = (
#             datetime(budget.year, budget.month + 1, 1)
#             if budget.month < 12
#             else datetime(budget.year + 1, 1, 1)
#         )

#         transactions = session.exec(
#             select(Transaction)
#             .where(Transaction.account.has(user_id=budget.user_id))
#             .where(Transaction.category == budget.category)
#             .where(Transaction.date >= start_of_month)
#             .where(Transaction.date < end_of_month)
#         ).all()

#         spent = sum(t.amount for t in transactions if t.category != CategoryType.salary)

#         result.append(BudgetStats(
#             id=budget.id,
#             user_id=budget.user_id,
#             category=budget.category,
#             month=budget.month,
#             year=budget.year,
#             limit=budget.limit,
#             spent=spent,
#             remaining=max(0, budget.limit - spent)
#         ))

#     return result


# @app.post("/budgets", response_model=Budget)
# def create_budget(budget: BudgetDefault, session: Session = Depends(get_session)):
#     budget = Budget.model_validate(budget)
#     session.add(budget)
#     session.commit()
#     session.refresh(budget)
#     return budget

# # ============ TRANSFERS ============

# @app.get("/transfers", response_model=List[Transfer])
# def list_transfers(session: Session = Depends(get_session)):
#     return session.exec(select(Transfer)).all()

# @app.post("/transfers", response_model=Transfer)
# def create_transfer(transfer: TransferDefault, session: Session = Depends(get_session)):
#     if transfer.from_account_id == transfer.to_account_id:
#         raise HTTPException(status_code=400, detail="Cannot transfer to the same account")

#     from_account = session.get(Account, transfer.from_account_id)
#     to_account = session.get(Account, transfer.to_account_id)

#     if not from_account or not to_account:
#         raise HTTPException(status_code=404, detail="Account not found")

#     if from_account.balance < transfer.amount:
#         raise HTTPException(status_code=400, detail="Insufficient funds in source account")

#     # Перевод средств
#     from_account.balance -= transfer.amount
#     to_account.balance += transfer.amount

#     transfer = Transfer.model_validate(transfer)
#     session.add(transfer)
#     session.add(from_account)
#     session.add(to_account)
#     session.commit()
#     session.refresh(transfer)
#     return transfer


# @app.get("/users-with-accounts")
# def get_users_with_accounts(session: Session = Depends(get_session)):
#     users = session.exec(select(User)).all()
#     result = []

#     for user in users:
#         session.refresh(user, attribute_names=["accounts"])
#         result.append({
#             "id": user.id,
#             "username": user.username,
#             "email": user.email,
#             "accounts": [
#                 {
#                     "id": acc.id,
#                     "name": acc.name,
#                     "balance": acc.balance,
#                     "is_goal": acc.is_goal,
#                     "target_amount": acc.target_amount
#                 }
#                 for acc in user.accounts
#             ]
#         })

#     return result
