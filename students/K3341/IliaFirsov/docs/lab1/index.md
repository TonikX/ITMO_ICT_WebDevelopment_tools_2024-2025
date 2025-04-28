## Задание: 

**Задание на 9 Баллов:** Реализовать на основании выбранной модели с помощью инструкций из практик серверное приложение на FastAPI. Оно должно включать в себя:

- Таблицы, реализованные с помощью ORM SQLAlchemy или SQLModel с использованием БД PostgreSQL.
- API, содержащее CRUD-ы. Там где это необходимо, реализовать GET-запросы возвращающие модели с вложенными объектами (связи many-to-many и one-to-many).
- Настроенную систему миграций с помощью библиотеки Alembic.
- Аннотацию типов в передаваемых и возвращаемых значениях в API-методах.
- Оформленную файловую структуру проекта с разделением кода, отвечающего за разную бизнес-логику и предметную область, на отдельные файлы и папки.
- (опционально) Комментарии к сложным частям кода.


**Задание на 15 Баллов (можно реализовывать сразу):** Необходимо реализовать функционал пользователя в разрабатываемом приложении. Функционал включает в себя:
- Авторизацию и регистрацию
- Генерацию JWT-токенов
- Аутентификацию по JWT-токену
- Хэширование паролей
- Дополнительные АПИ-методы для получения информации о пользователе, списка пользователей и смене пароля


Я представляю свой проект как задание на 15 баллов.

Проект — админ-панель для сервиса бронирования теннисных кортов. Сервис находится на стадии go2market. 
Админ-панель выполняет функции CMS и CRM, работает с 2 БД, реализована с помощью:
- `FastAPI`
- `SQLAlchemy`
- `pydantic`
- `alembic`

---

#### Файловая структура:
```
tree -I .venv -I __pycache__
.
├── __init__.py
├── abstractions
│   ├── __init__.py
│   ├── repositories
│   │   ├── __init__.py
│   │   ├── abstract.py
│   │   ├── booking_schedule.py
│   │   ├── court_organisation.py
│   │   ├── role.py
│   │   ├── schedule.py
│   │   ├── unicort
│   │   │   ├── __init__.py
│   │   │   ├── abstract.py
│   │   │   ├── booking.py
│   │   │   ├── court.py
│   │   │   ├── court_organization.py
│   │   │   ├── game_order.py
│   │   │   └── user.py
│   │   ├── user.py
│   │   └── user_comment.py
│   └── services
│       ├── __init__.py
│       ├── auth
│       │   ├── __init__.py
│       │   ├── service.py
│       │   └── tokens.py
│       ├── booking.py
│       ├── court.py
│       ├── exceptions.py
│       ├── permission.py
│       ├── role.py
│       ├── schedule.py
│       ├── unicort
│       │   ├── backend
│       │   │   └── service.py
│       │   ├── court_organisation.py
│       │   └── user.py
│       └── user.py
├── alembic.ini
├── dependencies
│   ├── __init__.py
│   ├── repositories
│   │   ├── __init__.py
│   │   ├── court.py
│   │   ├── roles.py
│   │   ├── schedule.py
│   │   ├── sessionmaker.py
│   │   ├── unicort
│   │   │   ├── __init__.py
│   │   │   ├── booking.py
│   │   │   ├── court.py
│   │   │   ├── court_organization.py
│   │   │   ├── game_order.py
│   │   │   ├── schedule.py
│   │   │   ├── sessionmaker.py
│   │   │   └── user.py
│   │   ├── user.py
│   │   └── user_comments.py
│   └── services
│       ├── __init__.py
│       ├── auth
│       │   ├── __init__.py
│       │   ├── service.py
│       │   └── token.py
│       ├── booking.py
│       ├── organisation.py
│       ├── role.py
│       ├── unicort
│       │   ├── __init__.py
│       │   ├── backend
│       │   │   └── service.py
│       │   ├── permission.py
│       │   ├── schedule.py
│       │   └── user.py
│       └── user.py
├── domain
│   ├── __init__.py
│   ├── dto
│   │   ├── __init__.py
│   │   ├── abstract.py
│   │   ├── auth.py
│   │   ├── court.py
│   │   ├── role.py
│   │   ├── unicort
│   │   │   ├── __init__.py
│   │   │   ├── achievement.py
│   │   │   ├── booking.py
│   │   │   ├── booking_promocode.py
│   │   │   ├── booking_schedule.py
│   │   │   ├── city.py
│   │   │   ├── court.py
│   │   │   ├── court_dictionary.py
│   │   │   ├── court_organization.py
│   │   │   ├── court_review.py
│   │   │   ├── district.py
│   │   │   ├── friendship.py
│   │   │   ├── game.py
│   │   │   ├── game_history.py
│   │   │   ├── game_order.py
│   │   │   ├── game_result.py
│   │   │   ├── game_score.py
│   │   │   ├── game_score_result.py
│   │   │   ├── game_user_result.py
│   │   │   ├── interest.py
│   │   │   ├── log.py
│   │   │   ├── membership.py
│   │   │   ├── notification.py
│   │   │   ├── promocode.py
│   │   │   ├── schedule.py
│   │   │   ├── schedule_occupancy.py
│   │   │   ├── user.py
│   │   │   ├── user_achievement.py
│   │   │   ├── user_booking.py
│   │   │   ├── user_interest.py
│   │   │   ├── user_promocode.py
│   │   │   └── user_review.py
│   │   ├── user.py
│   │   └── user_comment.py
│   ├── filter
│   │   ├── __init__.py
│   │   └── user.py
│   └── models
│       ├── __init__.py
│       ├── absract.py
│       ├── court_organisation.py
│       ├── role.py
│       ├── unicort
│       │   ├── __init__.py
│       │   ├── achievement.py
│       │   ├── booking.py
│       │   ├── booking_promocode.py
│       │   ├── booking_schedule.py
│       │   ├── city.py
│       │   ├── court.py
│       │   ├── court_dictionary.py
│       │   ├── court_organization.py
│       │   ├── court_review.py
│       │   ├── district.py
│       │   ├── friendship.py
│       │   ├── game.py
│       │   ├── game_history.py
│       │   ├── game_order.py
│       │   ├── game_result.py
│       │   ├── game_score.py
│       │   ├── game_score_result.py
│       │   ├── game_user_result.py
│       │   ├── interest.py
│       │   ├── log.py
│       │   ├── membership.py
│       │   ├── notification.py
│       │   ├── promocode.py
│       │   ├── schedule.py
│       │   ├── schedule_occupancy.py
│       │   ├── user.py
│       │   ├── user_achievement.py
│       │   ├── user_booking.py
│       │   ├── user_interest.py
│       │   ├── user_promocode.py
│       │   └── user_review.py
│       ├── user.py
│       └── user_comment.py
├── infrastructure
│   ├── __init__.py
│   ├── admin_db
│   │   ├── __init__.py
│   │   ├── entities.py
│   │   ├── migrations.py
│   │   ├── repositories
│   │   │   ├── __init__.py
│   │   │   ├── abstract.py
│   │   │   ├── court.py
│   │   │   ├── role.py
│   │   │   ├── user.py
│   │   │   └── user_comment.py
│   │   └── seed.py
│   ├── main_db
│   │   ├── __init__.py
│   │   ├── entities.py
│   │   ├── enums.py
│   │   └── reposiotries
│   │       ├── __init__.py
│   │       ├── abstract.py
│   │       ├── achievement.py
│   │       ├── booking.py
│   │       ├── booking_promocode.py
│   │       ├── booking_schedule.py
│   │       ├── city.py
│   │       ├── court.py
│   │       ├── court_dictionary.py
│   │       ├── court_organization.py
│   │       ├── court_review.py
│   │       ├── district.py
│   │       ├── friendship.py
│   │       ├── game.py
│   │       ├── game_history.py
│   │       ├── game_order.py
│   │       ├── game_result.py
│   │       ├── game_score.py
│   │       ├── game_score_result.py
│   │       ├── game_user_result.py
│   │       ├── interest.py
│   │       ├── log.py
│   │       ├── membership.py
│   │       ├── notification.py
│   │       ├── promocode.py
│   │       ├── schedule.py
│   │       ├── schedule_occupancy.py
│   │       ├── user.py
│   │       ├── user_achievement.py
│   │       ├── user_booking.py
│   │       ├── user_interest.py
│   │       ├── user_promocode.py
│   │       └── user_review.py
│   └── sqlalchemy
│       ├── __init__.py
│       ├── exceptions.py
│       └── repository.py
├── main.py
├── middlewares
│   ├── __init__.py
│   ├── auth_middleware.py
│   └── exception_middleware.py
├── migrations
│   ├── README
│   ├── env.py
│   ├── script.py.mako
│   └── versions
│       ├── 31e91d22258f_organisation_rename.py
│       ├── 53f27d362428_init.py
│       ├── 8ffaf9a5b8c3_roles_refactor.py
│       ├── 96f3c84e7a54_add_usercomment.py
│       ├── 97abc6892cea_court_organization.py
│       └── f5af50aded46_rename_court_to_organization.py
├── requirements.txt
├── routes
│   ├── __init__.py
│   ├── auth.py
│   ├── organisation
│   │   ├── __init__.py
│   │   └── court.py
│   ├── requests
│   │   ├── __init__.py
│   │   ├── booking.py
│   │   ├── change_role.py
│   │   ├── court.py
│   │   ├── organization.py
│   │   ├── role.py
│   │   └── user.py
│   ├── responses
│   │   ├── __init__.py
│   │   ├── booking.py
│   │   ├── court.py
│   │   ├── organisation.py
│   │   ├── role.py
│   │   ├── schedule.py
│   │   └── user.py
│   ├── roles.py
│   ├── unicort
│   │   ├── __init__.py
│   │   ├── booking.py
│   │   ├── organisation.py
│   │   ├── schedule.py
│   │   └── users.py
│   ├── user.py
│   └── utils
│       └── __init__.py
├── schema_check.py
├── services
│   ├── __init__.py
│   ├── auth.py
│   ├── exceptions.py
│   ├── organisation.py
│   ├── permission.py
│   ├── role.py
│   ├── token.py
│   ├── unicort
│   │   ├── __init__.py
│   │   ├── backend
│   │   │   ├── __init__.py
│   │   │   ├── requests
│   │   │   │   ├── __init__.py
│   │   │   │   └── booking.py
│   │   │   └── service.py
│   │   ├── booking.py
│   │   ├── schedule.py
│   │   └── user.py
│   └── user.py
├── settings
│   ├── __init__.py
│   ├── admin_db.py
│   ├── backend.py
│   ├── core_db.py
│   ├── db.py
│   ├── jwt.py
│   ├── merged_source.py
│   └── service_user.py
└── settings.json

41 directories, 257 files
```
----

#### SQLAlchemy

Админ-панель использует 2 БД:

- `core`: postgres, управляется основным бекендом; миграции не используются, но очень обширно используются `relationship`
- `admin`: postgres, управляется обозреваемым сервисом, миграции через `alembic` 

Обе — DBaaS Yandex.Cloud и требуют SSL

Подключение к БД:

```python
import ssl

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from settings import settings

__all__ = [
    "session_maker",
]


ssl_context = ssl.create_default_context(cafile="/app/.postgresql/root.crt")  # todo: change "/app" -> "." for migrations
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

connect_args = {"ssl": ssl_context}

engine = create_async_engine(settings.admin_db.url, echo=False, pool_recycle=1800, pool_timeout=30)
session_maker = async_sessionmaker(engine, expire_on_commit=False)
```

Сущности `core` реализованы по принципу `DB-first`, поэтому они скучные, разберем `admin`

Базовый класс для всех сущностей:

```python
Base = declarative_base()

class AbstractBase(Base):
    __abstract__ = True

    id: Mapped[pyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )
```

Сущности:

```python
class User(AbstractBase):
    __tablename__ = "users"

    email: Mapped[Optional[str]]
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]

    organisation_id: Mapped[Optional[pyUUID]] = mapped_column(ForeignKey('courts_organisation.id'))
    role_id: Mapped[Optional[pyUUID]] = mapped_column(ForeignKey('roles.id'))

    is_active: Mapped[bool]

    role: Mapped[Optional['Role']] = relationship("Role", back_populates='users')
    court_organisation: Mapped[Optional['Organisation']] = relationship("Organisation", back_populates='users')

class Organisation(AbstractBase):
    __tablename__ = "courts_organisation"

    unicort_organization_id: Mapped[int] = mapped_column(unique=True)
    is_active: Mapped[bool]
    creator_id: Mapped[pyUUID]

    users: Mapped[List[User]] = relationship('User', back_populates='court_organisation')

class Role(AbstractBase):
    __tablename__ = "roles"

    name: Mapped[str]
    description: Mapped[str]
    court_organisation_id: Mapped[Optional[pyUUID]] = mapped_column(ForeignKey('courts_organisation.id'))
    permissions: Mapped[dict] = mapped_column(JSONB)
    is_unicort_staff: Mapped[bool] = mapped_column(default=False)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    creator_id: Mapped[Optional[pyUUID]]

    users: Mapped[List[User]] = relationship("User", back_populates='role')
```
---- 

#### alembic

По умолчанию `alembic` синхронный, но мы хотим использовать для миграций те же данные для подключения, что и в основном проекте. Конечно, можно было бы просто использовать значения хоста/порта/etc, но это скучно, поэтому у нас есть кастомный `env.py` с асинхронными функциями, которые позволяют использовать `alembic` с `asyncpg` вместо `psychopg2`

```python
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from infrastructure.admin_db.entities import Base
from settings import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
config.set_main_option("sqlalchemy.url", settings.admin_db.url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

Также миграции запускаются при старте проекта вместе с сидами

```python
import logging
import subprocess

logger = logging.getLogger(__name__)

async def apply_migrations():
    migrations_is_ok = subprocess.call(["alembic", "upgrade", "head"]) == 0
    if not migrations_is_ok:
        logger.error("There is an error while upgrading database")
        exit(1)

```

----

#### API

Все эндпоинты в обязательном порядке аннотируются Pydantic-моделями, корректный swagger нам крайне необходим, потому что я не хочу рассказывать всей команде фронтенда устно форматы ответов.
Также мы поддерживаем camelCase для любого общения бекенда и фронтенда, поэтому модели содержат определения полей с Field(alias='...')
Например:

```python
class UserResponse(BaseModel):
    id: UUID
    email: Optional[str] = None
    username: str
    organisation_id: Optional[UUID] = Field(None, serialization_alias='organisationId')
    organisation_name: Optional[str] = Field(None, serialization_alias='organisationName')
    is_active: bool = Field(..., serialization_alias='isActive')
    role: Optional[RoleResponse] = None
    created_at: datetime = Field(..., serialization_alias='createdAt')
    updated_at: datetime = Field(..., serialization_alias='updatedAt')

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
```

Ручек у нас много, так что покажу несколько для примера:

```python
router = APIRouter(
    prefix="/user",
    tags=["Users"],
)

logger = logging.getLogger(__name__)


@router.get('/me')
async def get_me(request: Request) -> UserResponse:
    user_id = get_user_id_from_request(request)
    user_service = get_user_service()

    return UserResponse.model_validate(await user_service.get_me(user_id=user_id))


@router.post('/create')
async def create_user(
        request: Request,
        new_user: CreateUserRequest,
) -> Annotated[str, 'new user password']:
    user_id = get_user_id_from_request(request)
    permission_service = get_permission_service()
    court = await permission_service.check_create_users_permission(user_id, new_user)
    user_service = get_user_service()
    return await user_service.create_user(
        court_id=court.id if court else None,
        user=new_user,
    )


@router.get('/{user_id}')
async def get_user(
        request: Request,
        user_id: UUID,
) -> UserResponse:
    request_user_id = get_user_id_from_request(request)
    permission_service = get_permission_service()

    organisation = await permission_service.check_get_users_permission(request_user_id)

    user_service = get_user_service()
    user = await user_service.get_user(
        organisation_id=organisation.id if organisation else None,
        user_id=user_id,
    )
    return UserResponse.model_validate(user)


@router.get('')
async def get_users(
        request: Request,
        page: int = 1,
        size: int = 10,
        user_filter: UserFilter = FilterDepends(UserFilter)
) -> List[UserResponse]:
    request_user_id = get_user_id_from_request(request)
    permission_service = get_permission_service()
    organisation = await permission_service.check_get_users_permission(request_user_id)
    user_service = get_user_service()

    users = await user_service.get_users(
        organisation_id=organisation.id if organisation else None,
        page=page,
        size=size,
        user_filter=user_filter
    )
    return [UserResponse.model_validate(user) for user in users]
```

В проекте используется паттерн "репозиторий", который инкапсулирует работу с БД. 
Так, все `reationship`-поля маппятся в соответствующие `pydantic`-модели внутри слоя репозиториев.
При этом есть ситуации, когда в ответе API нужна информация из обеих БД/дополнительная обработка. В таком случае подготовка экземпляров моделей для ответа ложится на сервисный слой.
Пример:

```python

class UnicortBookingResponse(BaseModel):
    id: int
    booking_time: datetime = Field(..., serialization_alias='bookingTime')
    date: Optional[pydate] = None
    price: float
    payment_link: Optional[str] = Field(None, serialization_alias='paymentLink')
    payment_id: Optional[str] = Field(None, serialization_alias='paymentId')
    order_id: Optional[int] = Field(None, serialization_alias='orderId')
    booked_by: Annotated[
        BookedBy,
        Field(..., serialization_alias='bookedBy'),
        EnumNameSerializer
    ]
    status: Annotated[Optional[BookingStatus], EnumNameSerializer] = None
    promocode_id: Optional[int] = Field(None, serialization_alias='promocodeId')
    organisation_name: str = Field(..., serialization_alias='organisationName')

    start_time: time = Field(..., serialization_alias='startTime')
    end_time: time = Field(..., serialization_alias='endTime')

    users: List[BookingUserResponse]
    booked_by_user: Optional[BookingUserResponse] = Field(None, serialization_alias='bookedByUser')
    court_info: Optional[CourtResponse] = Field(None, serialization_alias='courtInfo')

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

@router.get('/actual')
async def get_actual_bookings(
        request: Request,
) -> list[UnicortBookingResponse]:
    user_id = get_user_id_from_request(request)
    permission_service = get_permission_service()
    court = await permission_service.check_get_bookings_permission(user_id)
    booking_service = get_booking_service()

    return await booking_service.get_actual_booking(court, user_id)


class UnicortBookingService(UnicortBookingServiceInterface):
    
    async def get_actual_booking(
            self,
            court: Organisation,
            user_id: UUID,
    ) -> list[UnicortBookingResponse]:
        responses = []
        if not court:
            booking_info = await self.bookings_repository.get_actual_booking()
            for booking in booking_info:
                booking_response = self._map_admin_booking(booking)
                responses.append(booking_response)
            return responses

        courts_ids = await self.court_organization_repository.get_courts(court.unicort_organization_id)
        booking_info = await self.bookings_repository.get_actual_booking_by_court_ids(courts_ids)
        for booking in booking_info:
            booking_response = self._map_unicort_booking(booking)
            responses.append(booking_response)

        return responses

    @staticmethod
    def _map_unicort_booking(booking: Booking) -> UnicortBookingResponse:
        logger.info(booking.schedules)
        start_time = min(map(lambda x: x.start_time, booking.schedules))
        end_time = max(map(lambda x: x.end_time, booking.schedules))

        return UnicortBookingResponse(
            id=booking.id,
            booking_time=booking.booking_time,
            date=booking.date.date(),
            price=booking.price,
            payment_link=booking.payment_link,
            payment_id=booking.payment_id,
            order_id=booking.order_id,
            booked_by=booking.booked_by,
            status=booking.status,
            promocode_id=booking.promocode_id,
            users=[
                BookingUserResponse.model_validate(user) for user in booking.invited_users or []
            ],
            booked_by_user=BookingUserResponse.model_validate(booking.creator) if booking.creator else None,
            court_info=CourtResponse.model_validate(booking.schedules[0].court),

            start_time=start_time,
            end_time=end_time,
            organisation_name=booking.court.organisation.name,
        )
```

----

#### AUTH

Хешируем пароли с argon2, креды - логин + пароль.
Так как ресурс непубличный, создание аккаунтов происходит только уже зарегистрированным пользователем. 
Пароль для нового пользователя возвращается строкой в ответе, смена пароля еще не реализована

```python
import logging

from fastapi import APIRouter, Header, HTTPException

from abstractions.services.exceptions import (
    NoSuchUserException,
    WrongCredentialsException,
    InvalidTokenException,
    ExpiredTokenException
)
from dependencies.services.auth import get_auth_service
from domain.dto.auth import AuthTokens, Credentials

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

logger = logging.getLogger(__name__)


@router.post('/signin')
async def sign_in(
        credentials: Credentials,
) -> AuthTokens:
    auth_service = get_auth_service()

    try:
        tokens = await auth_service.create_token(credentials)
        return tokens
    except (NoSuchUserException, WrongCredentialsException):
        raise HTTPException(status_code=401, detail="Ошибка: неправильное имя пользователя или пароль")


@router.post('/refresh')
async def refresh_tokens(
        refresh_token: str = Header(alias='X-Refresh-Token'),
) -> AuthTokens:
    if not refresh_token:
        raise HTTPException(status_code=401, detail='No refresh token provided')

    auth_service = get_auth_service()

    try:
        new_tokens = await auth_service.refresh_token(refresh_token)
        return new_tokens
    except (InvalidTokenException, NoSuchUserException, ExpiredTokenException) as e:
        code, detail = 401, 'Unknown authorization exception'
        match e:
            case InvalidTokenException():
                detail = 'Refresh token is invalid'
            case ExpiredTokenException():
                detail = 'Refresh token is expired'
            case NoSuchUserException():
                detail = 'User ID found by refresh token does not exist'

        logger.info(detail)
        raise HTTPException(status_code=code, detail=detail)
```

```python
import random
import string
from dataclasses import dataclass
from uuid import UUID

from passlib.hash import argon2

from abstractions.repositories.user import UserRepositoryInterface
from abstractions.services.auth.service import AuthServiceInterface
from abstractions.services.auth.tokens import TokenServiceInterface
from abstractions.services.exceptions import (
    NoSuchUserException,
    WrongCredentialsException,
    ExpiredTokenException,
    InvalidTokenException,
)
from domain.dto.auth import AuthTokens, Credentials
from infrastructure.sqlalchemy.exceptions import NotFoundException


@dataclass
class AuthService(AuthServiceInterface):
    token_service: TokenServiceInterface
    user_repository: UserRepositoryInterface

    async def get_user_id_from_jwt(self, token: str) -> UUID:
        claims = self.token_service.get_token_payload(token)
        user_id = claims.get('sub')
        if not user_id:
            raise InvalidTokenException

        try:
            user = await self.user_repository.get(user_id)
        except NotFoundException:
            raise NoSuchUserException

        if not user.is_active:
            raise PermissionError("Your account has been disabled.")

        return user.id

    async def create_token(self, credentials: Credentials) -> AuthTokens:
        user = await self.user_repository.get_by_username(username=credentials.username)
        if not user:
            raise NoSuchUserException

        if not self.verify_password(credentials.password, user.hashed_password):
            raise WrongCredentialsException

        return self.token_service.create_auth_token(user)

    async def refresh_token(self, refresh_token: str) -> AuthTokens:
        try:
            claims = self.token_service.get_token_payload(refresh_token)
            user_id = claims.get('sub')
            if not user_id:
                raise InvalidTokenException

            user = await self.user_repository.get(user_id)
            return self.token_service.create_auth_token(user)

        except (ExpiredTokenException, InvalidTokenException, NotFoundException):
            raise InvalidTokenException

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Хеширует пароль с использованием Argon2.

        :param password: Пароль для хеширования.
        :return: Захешированный пароль.
        """
        return argon2.using(rounds=4).hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Проверяет пароль против захешированного значения.

        :param password: Пароль для проверки.
        :param hashed_password: Захешированный пароль.
        :return: True, если пароль корректный, иначе False.
        """
        return argon2.verify(password, hashed_password)

    @staticmethod
    def generate_password(length: int = 12) -> str:
        if length < 4:
            raise ValueError("Длина пароля должна быть не менее 4 символов для обеспечения сложности.")

        # Обязательные категории символов
        categories = [
            random.choice(string.ascii_lowercase),  # Одна строчная буква
            random.choice(string.ascii_uppercase),  # Одна заглавная буква
            random.choice(string.digits),  # Одна цифра
            random.choice(string.punctuation)  # Один специальный символ
        ]

        # Остальные символы из всех категорий
        all_characters = string.ascii_letters + string.digits + string.punctuation
        categories.extend(random.choice(all_characters) for _ in range(length - 4))

        # Перемешиваем символы для равномерного распределения
        random.shuffle(categories)

        return ''.join(categories)
```
