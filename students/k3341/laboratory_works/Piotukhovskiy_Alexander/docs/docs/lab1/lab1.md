# Лабораторная работа №1. Реализация серверного приложения FastAPI.

---

Практическая работа была описана [здесь](practical_works.md).

---

## Реализация приложения
В качестве темы было выбрано веб-приложение для поиска партнеров в путешествие.

### Конфиг
Для начала было принято решение создать конфиг файл, из которого можно будет получить все необходимые настройки приложения. Начиная от порта приложения и данными для подключения к PostgreSQL, заканчивая настройкой JWT токенов.
```python
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    app_port: int = int(os.getenv("APP_PORT", 8000))

    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "postgres")
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", 5432))
    db_name: str = os.getenv("DB_NAME", "postgres")

    jwt_secret: str = os.getenv("JWT_SECRET", "Y0u_$H411_HoT_pAS$")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    class Config:
        env_file = ".env"


settings = Settings()
```
Данные загружаются из `.env` файла. В дальнейшем можно будет импортировать settings из любой части кода и получить эти переменные.


### Авторизация и аутентификация
Дальше было принято решение придумать, как защитить пользователей. Воспользуемся обычными JWT токенами.  
Нам потребуются библиотеки PyJWT (для работы с JWT токенами) и bcrypt (для хеширования паролей со случайной солью для каждого пользователя).
```shell
pip install pyjwt bcrypt
```

Был создан файл `core/auth.py`, который отвечает за безопасность, авторизацию и валидацию паролей.  
```python
def create_access_token(user_id: uuid.UUID) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "exp": expire
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token


def validate_access_token(token: str) -> tp.Optional[uuid.UUID]:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        sub = payload.get("sub")
        if not sub:
            return None
        return uuid.UUID(sub)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError):
        return None
```

Функция `create_access_token` генерирует jwt токен для определённого пользователя. В полезную нагрузку входит id пользователя и время жизни токена. JWT secret, алгоритм шифрования и время жизни токена хранится в конфиге приложения.  
Функция `validate_access_token` проверяет, чтобы полученный токен был валидным. То есть имел корректную сигнатуру и не был просроченным. В случае успеха, возвращается id пользователя. В противном случае - None.  

Далее идёт хеширование пароля и его валидация:
```python
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
```

Функция `hash_password` генерирует случайную соль для каждого пароля и хеширует ей пароль. 
Функция `verify_password` пробует зашифровать полученный пароль и сравнить его с хеш версией. Результатом будет ответ: совпадают ли пароли или нет.

---

Далее нужно сделать модели базы данных, но мы рассмотрим их дальше.  
Сейчас сделаем эндпоинты для авторизации и регистрации.

```python
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserAuthResponse)
def register(user_data: UserRegistration, session: Session = Depends(get_session)):
    error = Error()

    validate_registration(user_data, error, session)

    if error.is_error:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"errors": error.errors},
        )

    hashed_password = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        age=user_data.age,
        description=user_data.description,
        password_hash=hashed_password,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    token = auth.create_access_token(new_user.id)
    user = UserResponse.model_validate(new_user)

    return UserAuthResponse(user=user, access_token=token)


@router.post("/login", response_model=UserAuthResponse)
def login(user_data: UserLogin, session: Session = Depends(get_session)):
    login_input = user_data.login.strip()
    user = session.exec(select(User).where(or_(User.email == login_input, User.username == login_input))).first()

    if not user or not auth.verify_password(user_data.password, user.password_hash):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid credentials"}
        )

    token = auth.create_access_token(user.id)
    user = UserResponse.model_validate(user)
    return UserAuthResponse(user=user, access_token=token)
```

При регистрации проверяются все введённые данные. Если они успешно прошли проверку, пользователь считается зарегистрированным. Ему возвращается токен и краткая о нём информация.  


### База данных
Состоит из следующих таблиц:
```python
class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    username: str = Field(index=True, unique=True, nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    is_admin: bool = Field(default=False)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    age: Optional[int] = Field(default=None)
    description: Optional[str] = Field(default=None)
    password_hash: str

    created_trips: List["Trip"] = Relationship(back_populates="creator")
    trip_participations: List["TripParticipation"] = Relationship(back_populates="user")
    user_skills: List["UserSkill"] = Relationship(back_populates="user")
```
Таблица содержит необходимые данные о пользователе, а также указывает на связи с другими таблицами.

```python
class Trip(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    title: str
    description: str
    departure: datetime
    arrival: Optional[datetime] = None
    departure_location: str
    arrival_location: str
    creator_id: uuid.UUID = Field(foreign_key="user.id")

    creator: Optional[User] = Relationship(back_populates="created_trips")
    participations: List["TripParticipation"] = Relationship(back_populates="trip")

class TripParticipation(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    trip_id: uuid.UUID = Field(foreign_key="trip.id")
    role: TripRole = Field(
        default=TripRole.passenger,
        sa_column=Column(SAEnum(TripRole, name="trip_role", create_type=True), default=TripRole.passenger)
    )
    status: TripStatus = Field(
        default=TripStatus.pending,
        sa_column=Column(SAEnum(TripStatus, name="trip_status", create_type=True), default=TripStatus.pending)
    )
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="trip_participations")
    trip: Optional[Trip] = Relationship(back_populates="participations")
```

Таблица Trip содержит информацию о поездке, а таблица TripParticipation - об участниках этой поездки (связь многие-ко-многим).

```python
class Skill(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str
    description: Optional[str] = None
    user_skills: List["UserSkill"] = Relationship(back_populates="skill")

class UserSkill(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    skill_id: uuid.UUID = Field(foreign_key="skill.id")
    proficiency: int = Field(default=1, ge=1, le=10)

    user: Optional[User] = Relationship(back_populates="user_skills")
    skill: Optional[Skill] = Relationship(back_populates="user_skills")
```

Таблица Skill содержит информацию о навыках, которые могут быть у пользователей, а таблица UserSkill связывает навыки с пользователями (связь многие-ко-многим).


### Валидации
В коде есть несколько кастомных валидаций. Могут выполняться как все сразу вместе, так и по отдельности. Если не будет пройдена одна из вызванных проверок, операция будет отменена.

__Проверка username__:
- длина не менее 5 символов;
- содержит только латинские буквы, цифры, точку и нижнее подчёркивание;
- не содержит спецсимволы в начале/конце и не содержит подряд несколько спецсимволов;
- username уникален.

__Проверка email__:
- маску адреса электронной почты;
- email уникален.

__Проверка пароля__:
- длина не менее 8 символов;
- содержит хотя бы одну заглавную букву;
- содержит хотя бы одну строчную букву;
- содержит хотя бы одну цифру.

__Проверка возраста__:
- от 18 лет и старше


### Зависимости
Некоторые эндпоинты зависимы от определённых условий. Например, пользователь должен быть авторизован или быть администратором. Чтобы в каждом необходимом эндпоинте не дублировать множество строк кода, валидация была вынесена в "зависимости":
```python
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
):
    token = credentials.credentials
    user_id: uuid.UUID | None = validate_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    return user


def admin_required(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required."
        )
    return current_user
```

В дальнейшем можно ссылаться на необходимую зависимость напрямую в эндпоинте:
```python
@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(admin_required)])
def get_user_info(user_id: str, session: Session = Depends(get_session)):
    ...
```

### Эндпоинты
Были сделаны CRUD'ы для пользователей (их данных), отдельный эндпоинт для обновления пароля, получение определённого пользователя по id или всех пользователей сразу (admin only), авторизация и регистрация, CRUD'ы для поездки, возможность добавиться или покинуть поездку, а также поиск поездок по определённым параметрам.


### Миграции
По аналогии с практикой были настроены миграции. Некоторые из них были написаны во время выполнения лабораторной работы. Вместо хеша используется счётчик, чтобы версии миграций были более читабельные. 

## Итог
Итоговая схема проекта:
```
Lab1/
├── alembic
│   ├── README
│   ├── env.py
│   ├── script.py.mako
│   └── versions
│       ├── 1_added_field_is_admin_to_user.py
│       ├── 2_added_fields_first_name_and_last_name.py
│       ├── 3_added_skills_to_skill_table.py
│       └── 4_added_age_and_description_to_user.py
├── alembic.ini
├── app
│   ├── config.py
│   ├── core
│   │   ├── auth.py
│   │   └── validators.py
│   ├── db
│   │   ├── database.py
│   │   └── models.py
│   ├── dependencies
│   │   ├── admin.py
│   │   └── auth.py
│   ├── main.py
│   ├── routes
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── trip.py
│   │   └── user.py
│   └── schemas
│       ├── error.py
│       ├── trip.py
│       └── user.py
├── docker-compose.yml
└── requirements.txt
```