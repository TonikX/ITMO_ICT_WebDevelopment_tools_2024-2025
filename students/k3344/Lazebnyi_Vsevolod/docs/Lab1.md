# <span style="color:teal">Отчет по лабораторной работе №1: Реализация сервиса для управления личными финансами</span>.
## Цель работы
Научиться реализовывать полноценное серверное приложение с использованием фреймворка FastAPI, включая работу с базой данных, аутентификацию пользователей и построение сложных связей между сущностями.
## Выбранная тема
Разработка сервиса для управления личными финансами. Сервис позволяет:
1. Регистрировать пользователей и управлять профилями  
2. Создавать категории доходов/расходов  
3. Вести учет транзакций с привязкой к категориям  
4. Устанавливать лимиты бюджетов по категориям  
5. Ставить финансовые цели и отслеживать прогресс  
6. Получать уведомления по целям

## Схема данных
![Схема базы данных](images/shema.png)  

**Основные сущности**:
- `users`: Учетные данные пользователей
- `categories`: Категории операций (доходы/расходы)
- `transactions`: Финансовые операции пользователей
- `budgets`: Лимиты расходов по категориям
- `goals`: Финансовые цели
- `notifications`: Система уведомлений



### Ход работы
1. Устанавливаем необходимые библиотеки: sqlmodel, alembic, python dotenv, fastapi[all], psycopg2-binary

2. Реализовываем файл main.py, в котором будет код для создания проекта:
```python
from fastapi import FastAPI
from endpoints.user_endpoints import user_router
from endpoints.team_platform_endpoints import team_platform_router
from db.connection import init_db


app = FastAPI()
app.include_router(user_router)
app.include_router(team_platform_router)


@app.on_event("startup")
def on_startup():
    init_db()
```


3. Реализовываем файл с подключением к БД:
```python
from sqlmodel import SQLModel, create_engine
from sqlalchemy.orm import sessionmaker
import os

DB_URL = os.getenv("DB_ADMIN")
engine = create_engine(DB_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    with SessionLocal() as session:
        yield session
```

И также передаем в alembic.ini URL базы данных с помощью .env-файла:

```

DB_URL=postgresql+psycopg2://vllazebnyi:vllazebnyi@localhost:5432/financeDB_LR1```

```
```

sqlalchemy.url = ${DB_URL}

```


4. Переходим к постепенному созданию полноценного проекта. Начнем с авторизации пользвоателя (регистрация + вход)
Создаем форму регистрации:
```python
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    status: str
    created_at: datetime.datetime
    class Config:
        orm_mode = True


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    password_hash: str
    status: str = Field(default="active")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    transactions: List["Transaction"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")
    goals: List["Goal"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")


def get_user_by_credential(session: Session, credential: str):
    return session.exec(select(User).where((User.username == credential) | (User.email == credential))).first()


@app.post("/register", response_model=UserRead)
def register(user: UserCreate, session: Session = Depends(get_session)):
    if get_user_by_credential(session, user.username):
        raise HTTPException(status_code=409, detail="Username already exists")
    if get_user_by_credential(session, user.email):
        raise HTTPException(status_code=409, detail="Email already exists")
    user_data = user.dict()
    user_data["password_hash"] = get_password_hash(user_data.pop("password"))
    return create_entity(session, User, user_data)

@app.post("/login")
def login(
        credential: str = Form(...),
        password: str = Form(...),
        session: Session = Depends(get_session)
):
    user = get_user_by_credential(session, credential)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": encode_token(user.id), "token_type": "bearer"}

@app.get("/users/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/users/change-password")
def change_password(old_password: str = Form(...), new_password: str = Form(...),
                    session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid password")
    current_user.password_hash = get_password_hash(new_password)
    session.add(current_user)
    session.commit()
    return {"message": "Password updated"}
```

5. Дописываем реализацию перевода пароля в хэш и обратно

auth.py:
```python
security = HTTPBearer()
SECRET_KEY = "NeverGonnaGiveUup"

def encode_token(user_id: int) -> str:
    payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=8),
        "iat": datetime.datetime.utcnow(),
        "sub": user_id
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

hashing.py:
```

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```


9.Сделаем все поля и запросы закрытыми для неаторизированного пользователя. Для этого пропишем следующую строчку:
```python
APIRouter(dependencies=[Depends(auth_handler.get_authenticated_user)])
```
Теперь на роутере стоит защита от незарегестрирвоанного пользователя




6. Доделываем CRUD-запросы:
```python
from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.tables import User, Category, Transaction, Budget, Goal, Notification, TransactionCategoryLink

def create_entity(session: Session, model, data: dict):
    db_entity = model(**data)
    session.add(db_entity)
    session.commit()
    session.refresh(db_entity)
    return db_entity

def get_entity(session: Session, model, entity_id: int, user_id: int = None):
    entity = session.get(model, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    if hasattr(entity, "user_id") and user_id and entity.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return entity

def get_entities(session: Session, model, user_id: int = None):
    if user_id and hasattr(model, "user_id"):
        return session.exec(select(model).where(model.user_id == user_id)).all()
    return session.exec(select(model)).all()

def delete_entity(session: Session, model, entity_id: int, user_id: int = None):
    entity = session.get(model, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    if hasattr(entity, "user_id") and user_id and entity.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    session.delete(entity)
    session.commit()

def get_user_by_credential(session: Session, credential: str):
    return session.exec(select(User).where((User.username == credential) | (User.email == credential))).first()
```

7. После создания моделей мы можем наконец применить миграции и построить базу данных в PostgreSQL:
![Alt текст](images/1.png)
![Alt текст](images/2.png)
![Alt текст](images/3.png)
![Alt текст](images/4.png)


8. После всех манипуляций и написания сrud запросов жем перейти и посмотреть документацию /docs FastAPI:
![Alt текст](images/5.png)
![Alt текст](images/7.png)

Теперь протестируем готовые запросы:

- /register: после регистрации пароль пароль "хэшируется"

![Alt текст](images/8.png)
![Alt текст](images/9.png)
![Alt текст](images/10.png)

- /login

![Alt текст](images/11.png)
![Alt текст](images/12.png)
![Alt текст](images/22.png)

- /users/me

![Alt текст](images/13.png)

- /users/change-password

- /categories

![Alt текст](images/14.png)

- /transactions

![Alt текст](images/15.png)
![Alt текст](images/16.png)
![Alt текст](images/17.png)

- /budgets
![Alt текст](images/18.png)

- /goals

![Alt текст](images/19.png)

![Alt текст](images/20.png)

- /notifications

![Alt текст](images/21.png)

## Вывод 
В рамках данной работы реализовано серверное приложение на FastAPI для управления финансами
Спроектирована и реализована реляционная БД PostgreSQL
Реализована сложная связь many-to-many между транзакциями и категориями
Внедрена аутентификация по JWT-токенам
Разработаны все основные функции финансового сервиса:
* Учет доходов/расходов
* Управление бюджетами
* Отслеживание финансовых целей
* Система уведомлений