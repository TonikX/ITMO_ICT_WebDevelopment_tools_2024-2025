# Лабораторная работа №1: Разработка сервиса для управления личными финансами

## Текст задания

Необходиом создать простой сервис для управления личными финансами. Сервис должен позволять пользователям вводить доходы и расходы, устанавливать бюджеты на различные категории, а также просматривать отчеты о своих финансах. Дополнительные функции могут включать в себя возможность получения уведомлений о превышении бюджета, анализа трат и установки целей на будущее.

## Models

### User - пользователи
```python
class UserDefault(SQLModel):
    username: str
    email: EmailStr = Field(unique=True, index=True)
    is_active: bool = True
    hashed_password: str

class UserCreate(SQLModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(SQLModel):
    username: str
    password: str

class UserRead(SQLModel):
    id: int
    email: EmailStr
    is_active: bool

class User(UserDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    accounts: List["Account"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")

class ChangePassword(BaseModel):
    old_password: str
    new_password: str


class UserBudgetLink(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    budget_id: int = Field(foreign_key="budget.id", primary_key=True)
```
### Account - счета
```python
class AccountBase(SQLModel):
    name: str
    balance: float
    is_goal: bool = False
    target_amount: Optional[float] = None


class Account(AccountBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="accounts")


class AccountDefault(SQLModel):
    user_id: int
    name: str
    is_goal: bool = False
    balance: float = 0.0  
    target_amount: Optional[float] = None # цель (только если is_goal=True)
```
### Transaction - транзакции
```python
class TransactionBase(SQLModel):
    amount: float
    description: str
    date: datetime
    category: CategoryType


class Transaction(TransactionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="account.id")


class TransactionDefault(SQLModel):
    account_id: int
    category: CategoryType
    amount: float
    description: Optional[str]
    date: datetime
```
### Budget - бюджеты
```python
class BudgetBase(SQLModel):
    month: int
    year: int
    limit: float
    category: CategoryType
    
class Budget(BudgetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    users: List["User"] = Relationship(back_populates="shared_budgets", link_model=UserBudgetLink)

class BudgetDefault(SQLModel):
    # user_id: int
    category: CategoryType
    month: int
    year: int
    limit: float
    user_ids: List[int]

class BudgetStats(BaseModel):
    id: int
    users: List[int]
    category: CategoryType
    month: int
    year: int
    limit: float
    spent: float
    remaining: float
```
### Transfer - переводы между своими счетами
```python
class TransferBase(SQLModel):
    amount: float
    date: datetime


class Transfer(TransferBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    from_account_id: int = Field(foreign_key="account.id")
    to_account_id: int = Field(foreign_key="account.id")


class TransferDefault(SQLModel):
    from_account_id: int
    to_account_id: int
    amount: float
    date: datetime
```