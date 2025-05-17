from datetime import datetime, time
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional


class UserDefault(SQLModel):
    """
    Базовая модель пользователя.

    Attributes:
        name (str): Уникальное имя пользователя.
        email (str): Электронная почта.
    """
    name: str = Field(unique=True)
    email: str


class UserCreate(UserDefault):
    """
    Модель для создания пользователя.

    Добавляет поле пароля.
    """
    password: str


class UserRead(UserDefault):
    """
    Модель для чтения данных пользователя.

    Attributes:
        id (int): Идентификатор пользователя.
    """
    id: int


class UserUpdate(SQLModel):
    """
    Модель для обновления данных пользователя (все поля необязательные).
    """
    name: str | None = None
    email: str | None = None
    password: str | None = None


class User(UserDefault, table=True):
    """
    Табличная модель пользователя для базы данных.

    Attributes:
        id (int): Первичный ключ.
        password (str): Хешированный пароль.
        projects (List[Project]): Связанные проекты.
        tasks (List[Task]): Связанные задачи.
    """
    id: int = Field(default=None, primary_key=True)
    password: str
    projects: List["Project"] = Relationship(back_populates="user")
    tasks: List["Task"] = Relationship(back_populates="user")


class UserLogin(SQLModel):
    """
    Модель для авторизации пользователя.

    Attributes:
        name (str): Имя пользователя.
        password (str): Пароль.
    """
    name: str
    password: str


class ProjectTaskLink(SQLModel, table=True):
    """
    Промежуточная таблица для связи задач и проектов.
    """
    task_id: int = Field(default=None, foreign_key="task.id", primary_key=True)
    project_id: int = Field(default=None, foreign_key="project.id", primary_key=True)


class ProjectDefault(SQLModel):
    """
    Базовая модель проекта.

    Attributes:
        name (str): Название проекта.
        description (str): Описание проекта.
        user_id (int): Владелец проекта.
    """
    name: str
    description: str
    user_id: int = Field(foreign_key="user.id")


class ProjectCreate(ProjectDefault):
    """Модель для создания проекта."""
    pass


class ProjectRead(ProjectDefault):
    """
    Модель для чтения проекта.

    Attributes:
        id (int): Идентификатор проекта.
        tasks (List[TaskRead]): Связанные задачи.
    """
    id: int
    tasks: List["TaskRead"] = []


class Project(ProjectDefault, table=True):
    """
    Табличная модель проекта.

    Attributes:
        id (int): Первичный ключ.
        user (User): Владелец проекта.
        tasks (List[Task]): Связанные задачи.
    """
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="projects")
    tasks: List["Task"] = Relationship(back_populates="projects", link_model=ProjectTaskLink)


class TagTaskLink(SQLModel, table=True):
    """
    Промежуточная таблица для связи задач и тегов.
    """
    task_id: int = Field(default=None, foreign_key="task.id", primary_key=True)
    tag_id: int = Field(default=None, foreign_key="tag.id", primary_key=True)


class TaskStatus(str, Enum):
    """
    Статус задачи.

    Значения:
        active: Активная.
        completed: Завершённая.
        archived: Архивированная.
    """
    active = "active"
    completed = "completed"
    archived = "archived"


class TaskDefault(SQLModel):
    """
    Базовая модель задачи.

    Attributes:
        name (str): Название.
        description (str): Описание.
        status (TaskStatus): Статус.
        difficulty (int): Сложность.
        priority (int): Приоритет.
        deadline (datetime): Крайний срок.
    """
    name: str
    description: str
    status: TaskStatus
    difficulty: int
    priority: int
    deadline: datetime


class TaskCreate(TaskDefault):
    """
    Модель для создания задачи.

    Attributes:
        project_ids (Optional[List[int]]): Идентификаторы связанных проектов.
    """
    project_ids: Optional[List[int]] = None


class TaskRead(TaskDefault):
    """
    Модель для чтения задачи.

    Attributes:
        id (int): Идентификатор задачи.
        time_spent (Optional[int]): Время, потраченное на задачу.
        user_id (int): Владелец задачи.
    """
    id: int
    time_spent: Optional[int] = None
    user_id: int = Field(foreign_key="user.id")


class Task(TaskDefault, table=True):
    """
    Табличная модель задачи.

    Attributes:
        id (int): Первичный ключ.
        time_spent (Optional[int]): Потраченное время.
        user (User): Владелец задачи.
        projects (List[Project]): Связанные проекты.
        routine (Optional[Routine]): Связанная рутина.
        tags (List[Tag]): Теги.
    """
    id: int = Field(default=None, primary_key=True)
    time_spent: Optional[int] = None
    user_id: int = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="tasks")
    projects: List["Project"] = Relationship(back_populates="tasks", link_model=ProjectTaskLink)
    routine: Optional["Routine"] = Relationship(back_populates="task", sa_relationship_kwargs={"uselist": False})
    tags: List["Tag"] = Relationship(back_populates="tasks", link_model=TagTaskLink)


class TimeLogDefault(SQLModel):
    """
    Базовая модель записи учёта времени.

    Attributes:
        task_id (int): Задача.
        user_id (int): Владелец записи.
        start_time (datetime): Начало.
        end_time (datetime): Конец.
    """
    task_id: int = Field(foreign_key="task.id")
    user_id: int = Field(foreign_key="user.id")
    start_time: datetime
    end_time: datetime


class TimeLogCreate(TimeLogDefault):
    """Модель для создания записи времени."""
    pass


class TimeLogRead(TimeLogDefault):
    """
    Модель для чтения записи времени.

    Attributes:
        id (int): Идентификатор.
    """
    id: int


class TimeLog(TimeLogDefault, table=True):
    """
    Табличная модель учёта времени.

    Attributes:
        id (int): Первичный ключ.
    """
    id: int = Field(default=None, primary_key=True)


class RoutineType(str, Enum):
    """
    Частота выполнения рутины.

    Значения:
        daily: Ежедневно.
        weekly: Еженедельно.
        monthly: Ежемесячно.
    """
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class RoutineDefault(SQLModel):
    """
    Базовая модель рутины.

    Attributes:
        name (str): Название.
        frequency (RoutineType): Частота.
        count (int): Количество повторений.
        task_id (int): Связанная задача.
    """
    name: str
    frequency: RoutineType
    count: int
    task_id: int = Field(foreign_key="task.id", unique=True)


class RoutineCreate(RoutineDefault):
    """
    Модель для создания рутины.

    Attributes:
        user_id (int): Владелец.
    """
    user_id: int = Field(foreign_key="user.id")


class RoutineRead(RoutineDefault):
    """
    Модель для чтения рутины.

    Attributes:
        id (int): Идентификатор.
    """
    id: int


class Routine(RoutineDefault, table=True):
    """
    Табличная модель рутины.

    Attributes:
        id (int): Первичный ключ.
        user_id (int): Владелец.
        task (Optional[Task]): Связанная задача.
    """
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    task: Optional["Task"] = Relationship(back_populates="routine")


class TagDefault(SQLModel):
    """
    Базовая модель тега.

    Attributes:
        user_id (int): Владелец.
        name (str): Название.
        color (str): Цвет.
    """
    user_id: int = Field(foreign_key="user.id")
    name: str
    color: str


class TagCreate(TagDefault):
    """Модель для создания тега."""
    pass


class TagRead(TagDefault):
    """
    Модель для чтения тега.

    Attributes:
        id (int): Идентификатор.
    """
    id: int


class Tag(TagDefault, table=True):
    """
    Табличная модель тега.

    Attributes:
        id (int): Первичный ключ.
        tasks (List[Task]): Связанные задачи.
    """
    id: int = Field(default=None, primary_key=True)
    tasks: List["Task"] = Relationship(back_populates="tags", link_model=TagTaskLink)


class NotificationDefault(SQLModel):
    """
    Базовая модель уведомления.

    Attributes:
        user_id (int): Владелец.
        task_id (int): Задача.
        remind_at (datetime): Время напоминания.
    """
    user_id: int = Field(foreign_key="user.id")
    task_id: int = Field(foreign_key="task.id")
    remind_at: datetime


class NotificationCreate(NotificationDefault):
    """Модель для создания уведомления."""
    pass


class NotificationRead(NotificationDefault):
    """
    Модель для чтения уведомления.

    Attributes:
        id (int): Идентификатор.
    """
    id: int


class Notification(NotificationDefault, table=True):
    """
    Табличная модель уведомления.

    Attributes:
        id (int): Первичный ключ.
    """
    id: int = Field(default=None, primary_key=True)

