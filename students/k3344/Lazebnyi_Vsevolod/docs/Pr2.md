
# Практика 1.2: Настройка БД, SQLModel и миграции через Alembic

## Для выполнения лабораторной и всех практических работ рекомендуется использовать версию Python 3.10+

### SQLModel и ORM

Для того чтобы реализовывать взаимодействие с БД не чистыми SQL-запросами при разработке приложений обычно используют ORM. При работе с Django в качестве ORM выступала библиотека, интегрированная во фреймворк, без возможности ее отдельного использования в сторонних разработках. Т.к. FastAPI предоставляет разработчику наиболее гибкую настройку всего проекта, то встроенных ORM такой фреймворк не предусматривает. При этом от разработчиков существует интегрируемая в фреймворк библиотека, а также ряд рекомендованных ORM для использования.

### SQLModel. Реализация и подключение


После установки всех зависимостей необходимо реализовать файл с подключением к БД. В файле описывается способ подключения к БД и реализоваем дополнительные методы, упрощающие инициализацию. называем файл connection.py:

### connection.py

```python
from sqlmodel import SQLModel, Session, create_engine

db_url = 'postgresql://vllazebnyi:vllazebnyi@localhost:5432/financeDB'
engine = create_engine(db_url, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

`db_url` и `engine` создают подключение к БД, эта реализация аналогична той, что использует ORM SQLAlchemy. 

Параметр `echo=True` в методе `create_engine` включает вывод всех осуществляемых SQL-запросов в командную строку.

Метод `init_db` используется для инициализации всех таблиц в созданной базе данных, его использование будет представлено ниже.

Метод-генератор `get_session` используется для получения сессий, необходимых при выполнении запросов к БД через Dependencies. 

![Получившаяся БД](images/BD.png)
![Получившаяся БД](images/4.png)

### Создание моделей

Чтобы классы моделей можно было инициализировать в БД, необходимо в параметры класса передать наследника - класс SQLModel и далее указать `table=True`.

### Обновленный файл models.py

```python
from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from datetime import datetime

class CategoryType(str, Enum):
    income = "income"
    expense = "expense"

class NotificationType(str, Enum):
    over_budget = "over_budget"
    goal_achieved = "goal_achieved"
    info = "info"

class NotificationStatus(str, Enum):
    unread = "unread"
    read = "read"

class StatusType(str, Enum):
    active = "active"
    inactive = "inactive"

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(unique=True)
    password_hash: str
    status: StatusType = Field(default=StatusType.active)
    created_at: datetime = Field(default_factory=datetime.now)

class CategoryBase(SQLModel):
    name: str = Field(unique=True)
    type: CategoryType
    status: StatusType = Field(default=StatusType.active)
    created_at: datetime = Field(default_factory=datetime.now)

class TransactionBase(SQLModel):
    amount: float
    date: datetime = Field(default_factory=datetime.now)
    description: Optional[str] = ""
    status: StatusType = Field(default=StatusType.active)

class BudgetBase(SQLModel):
    limit_amount: float
    start_date: datetime
    end_date: datetime
    status: StatusType = Field(default=StatusType.active)
    created_at: datetime = Field(default_factory=datetime.now)

class GoalBase(SQLModel):
    title: str
    target_amount: float
    current_amount: float = Field(default=0)
    deadline: datetime
    status: StatusType = Field(default=StatusType.active)
    created_at: datetime = Field(default_factory=datetime.now)

class NotificationBase(SQLModel):
    type: NotificationType
    status: NotificationStatus = Field(default=NotificationStatus.unread)
    created_at: datetime = Field(default_factory=datetime.now)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transactions: List["Transaction"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")
    goals: List["Goal"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")

class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transactions: List["Transaction"] = Relationship(back_populates="category")
    budgets: List["Budget"] = Relationship(back_populates="category")

class Transaction(TransactionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="transactions")
    category_id: int = Field(foreign_key="category.id")
    category: Category = Relationship(back_populates="transactions")

class Budget(BudgetBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="budgets")
    category_id: int = Field(foreign_key="category.id")
    category: Category = Relationship(back_populates="budgets")

class Goal(GoalBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="goals")

class Notification(NotificationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="notifications")
    budget_id: int = Field(foreign_key="budget.id")
    budget: Budget = Relationship()
```

### Запуск сервера командой:

```bash
uvicorn main:app --reload
```

### Проверяем вложенность из НЕ временной БД:

![Забираем всех юзеров](images/Pr3.png)

#### Заключение

Были реализованы все улучшения, описанные в практике, включая интеграцию SQLModel.

