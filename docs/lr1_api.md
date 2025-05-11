# 🔐 Авторизация

Все защищённые эндпоинты требуют передачи JWT токена в заголовке:

```
Authorization: Bearer <token>
```

## ⚙️ Настройка базы данных

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
```

## 📋 Пример модели

```python
class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, default=datetime.date.today)
    description = Column(String)
    type = Column(Enum(TransactionType), nullable=False)
```

## 📤 Пример схемы запроса

```python
class TransactionCreate(BaseModel):
    account_id: int
    amount: float
    date: Optional[date] = None
    description: Optional[str] = None
    type: Literal["income", "expense"]
    categories: List[TransactionCategoryCreate]
```

## 📡 Пример ручки

```python
@router.post("/transactions", response_model=TransactionOut)
def create_transaction_endpoint(transaction: TransactionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return create_transaction(db, transaction, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## 📍 Уведомления при превышении бюджета

```python
def check_budget_exceedance(db: Session, user_id: int, category_id: int):
    budgets = db.query(Budget).filter(Budget.user_id == user_id, Budget.category_id == category_id).all()
    for budget in budgets:
        if budget.start_date and budget.end_date:
            total_spent = ...
            if total_spent > budget.limit_amount:
                create_notification(db, user_id, "Budget Exceeded", f"Spent: {total_spent}, Limit: {budget.limit_amount}")
```

## 🧪 Пример CURL-запроса

###Testing User API Endpoints with curl
####Register a new user
```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
-H "Content-Type: application/json" \
-d '{"username": "testuser", "email": "test@example.com", "password": "secret"}'
```

####Login to get JWT token
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=testuser&password=secret"
```

####Get current user info (replace JWT_TOKEN with the actual token)
```bash
curl -X GET "http://127.0.0.1:8000/auth/users/me" \
-H "Authorization: Bearer $JWT_TOKEN"
```

####Get list of users (replace JWT_TOKEN with the actual token)
```bash
curl -X GET "http://127.0.0.1:8000/auth/users" \
-H "Authorization: Bearer $JWT_TOKEN"
```

####Change password (replace JWT_TOKEN with the actual token)
```bash
curl -X POST "http://127.0.0.1:8000/auth/change-password" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $JWT_TOKEN" \
-d '{"old_password": "secret", "new_password": "newsecret"}'
```

###Finance Endpoints
####Create Transaction
```bash
curl -X POST "http://127.0.0.1:8000/finance/transactions" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $JWT_TOKEN" \
-d '{"account_id": 1, "amount": 50.0, "description": "Dinner", "type": "expense", "categories": [{"category_id": 2, "allocated_amount": 50.0}]}'
```

####Create Account
```bash
curl -X POST "http://127.0.0.1:8000/finance/accounts" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $JWT_TOKEN" \
-d '{"name": "Checking", "balance": 1000.0}'
```

####Get Accounts
```bash
curl -X GET "http://127.0.0.1:8000/finance/accounts" \
-H "Authorization: Bearer $JWT_TOKEN"
```

####Create category
```bash
curl -X POST "http://127.0.0.1:8000/finance/categories" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $JWT_TOKEN" \
-d '{"name": "Groceries", "description": "Food and supplies"}'
```

####Create budget
```bash
curl -X POST "http://127.0.0.1:8000/finance/budgets" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $JWT_TOKEN" \
-d '{"category_id": 3, "period": "2025-05", "limit_amount": 100.0, "start_date": "2025-04-01", "end_date": "2025-12-31"}'
```

####Get categories
```bash
curl -X GET "http://127.0.0.1:8000/finance/categories" \
-H "Authorization: Bearer $JWT_TOKEN"
```

####Expense Analysis
```bash
curl -X GET "http://127.0.0.1:8000/finance/analysis/expenses" \
-H "Authorization: Bearer $JWT_TOKEN"
```

####Dashboard Summary
```bash
curl -X GET "http://127.0.0.1:8000/finance/dashboard" \
-H "Authorization: Bearer $JWT_TOKEN"
```

####Spending Trends
```bash
curl -X GET "http://127.0.0.1:8000/finance/trends/spending" \
-H "Authorization: Bearer $JWT_TOKEN"
```

####Get notifications
```bash
curl -X GET "http://127.0.0.1:8000/finance/notifications" \
-H "Authorization: Bearer $JWT_TOKEN"
```

## 🗂 Структура проекта

```
lr1/
├── app/
│   ├── models.py
│   ├── schemas/
│   ├── crud/
│   ├── api/
│   ├── database.py
│   └── main.py
├── alembic/
├── .env
├── requirements.txt
└── README.md
```

## 🚀 Как запустить

1. Установить зависимости:
```
pip install -r requirements.txt
```

2. Создать базу PostgreSQL и `.env`:
```
docker run --name my_postgres \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=dbname \
  -p 5432:5432 \
  -d postgres

DATABASE_URL=postgresql://user:pass@localhost/dbname
```

3. Прогнать миграции:
```
alembic upgrade head
```

4. Запуск:
```
uvicorn app.main:app --reload
```
