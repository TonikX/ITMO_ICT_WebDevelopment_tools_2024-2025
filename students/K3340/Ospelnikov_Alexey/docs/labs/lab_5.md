# Лабораторная работа №5

## Модели


Код модели User:
```python
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str
    fullname: str
    hash_password: str
    created_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    task_list: List["Task"] = Relationship(back_populates="author")
```


Код модели Task:
```python
class PriorityType(Enum):
    extreme = "extreme"
    high = "high"
    medium = "medium"
    low = "low"


class StatusType(Enum):
    done = "done"
    in_progress = "in_progress"
    cancelled = "cancelled"
    delayed = "delayed"
    added = "added"


class TaskDefault(SQLModel):
    name: str
    description: Optional[str] = ""
    deadline: datetime
    status: StatusType
    priority: PriorityType
    tag: Optional[str] = ""
    created_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    
    
class Task(TaskDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    schedules: Optional[List["Schedule"]] = Relationship(
        back_populates="tasks", link_model=TaskSchedule
    )    
    created_by: int = Field(
        default=None, foreign_key="user.id"
    )    
    author: Optional[User] = Relationship(back_populates="task_list")
    task_link: List[TaskSchedule] = Relationship(back_populates="tasks")
    notification_list: List["Notification"] = Relationship(back_populates="parent_task")
    
    

class TaskUser(TaskDefault):
    author: Optional[User] = None
```

Код модели Schedule:
```python
class Schedule(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    date: datetime
    tasks: Optional[List["Task"]] = Relationship(
        back_populates="schedules", link_model=TaskSchedule
    )
    productivity_score: Optional[int] = 5
    notes: Optional[str] = ''
    schedule_link: List[TaskSchedule] = Relationship(back_populates="schedules")
```


Код модели Task_Schedule:
```python
class TaskScheduleDefault(SQLModel):
    urgency: Optional[int] = 5
    start_time: datetime
    end_time: Optional[datetime]

class TaskSchedule(TaskScheduleDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(
            default=None, foreign_key="task.id"
        )
    schedule_id: Optional[int] = Field(
        default=None, foreign_key="schedule.id"
    )   
    tasks: Optional["Task"] = Relationship(back_populates="task_link")
    schedules: Optional["Schedule"] = Relationship(back_populates="schedule_link")

class TaskScheduleSerializator(TaskScheduleDefault):
    tasks: Optional["Task"] = None
    schedules: Optional["Schedule"] = None
```


Код модели Notification:
```python
class NotificationDefault(SQLModel):
    created_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    message: Optional[str] = ''
    is_read: bool = False

class Notification(NotificationDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    task: int = Field(default=None, foreign_key="task.id")
    parent_task: Optional[Task] = Relationship(back_populates="notification_list")
    

class NotificationTask(NotificationDefault):
    parent_task: Optional[Task] = None
```

## Сервисы

Код ceрвиса Notification:
```python
def new_notification_create(notification: Notification, session) -> Notification:
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return {"status": 200, "data": notification}


def list_all_notifications(session) -> List[Notification]:
    return session.exec(select(Notification)).all()


def get_notification_by_id(notification_id: int, session) -> Notification:
    data = session.exec(select(Notification).where(Notification.id == notification_id)).first()
    if not data:
        raise HTTPException(status_code=404, detail="Notification not found")    
    return data

def delete_notification(notification_id: int, session):
    notification = session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    session.delete(notification)
    session.commit()
    return {"ok": True}    

def patch_notification(notification_id: int, notification: Notification, session) -> Notification:
    db_notification = session.get(Notification, notification_id)
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification_data = notification.model_dump(exclude_unset=True)
    for key, value in notification_data.items():
        setattr(db_notification, key, value)
    session.add(db_notification)
    session.commit()
    session.refresh(db_notification)
    return db_notification
```


Код ceрвиса User:
```python
def new_user_create(user: User, session) -> User:
    hashed_password = get_password_hash(user.hash_password)
    user = User(
        email=user.email,
        fullname=user.fullname,
        hash_password=hashed_password 
    )    
    session.add(user) 
    session.commit()
    session.refresh(user)
    return user


def list_all_users(session) -> List[User]:
    return session.exec(select(User)).all()


def get_user_by_id(user_id: int, session) -> User:
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")    
    return user

def change_password(old_password: str,
                new_password: str,
                current_user: User, 
                session
                ) -> User:
    if verify_password(old_password, current_user.hash_password):
        setattr(current_user, "hash_password", get_password_hash(new_password))
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user

def delete_user(user_id: int, session):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}    

def patch_user(user_id: int, user: User, session) -> User:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
```



Код ceрвиса Task_Schedule:
```python
def new_taskSchedule_create(taskSchedule: TaskSchedule, session) -> TaskSchedule:
    session.add(taskSchedule)
    session.commit()
    session.refresh(taskSchedule)
    return {"status": 200, "data": taskSchedule}


def get_taskSchedule_by_id(taskSchedule_id: int, session) -> TaskSchedule:
    taskSchedule = session.exec(select(TaskSchedule).where(TaskSchedule.id == taskSchedule_id)).first()
    if not taskSchedule:
        raise HTTPException(status_code=404, detail="TaskSchedule not found")    
    return taskSchedule

def delete_taskSchedule(taskSchedule_id: int, session):
    taskSchedule = session.get(TaskSchedule, taskSchedule_id)
    if not taskSchedule:
        raise HTTPException(status_code=404, detail="TaskSchedule not found")
    session.delete(taskSchedule)
    session.commit()
    return {"ok": True}    

def patch_taskSchedule(taskSchedule_id: int, taskSchedule: TaskSchedule, session) -> TaskSchedule:
    db_taskSchedule = session.get(TaskSchedule, taskSchedule_id)
    if not db_taskSchedule:
        raise HTTPException(status_code=404, detail="TaskSchedule not found")
    taskSchedule_data = taskSchedule.model_dump(exclude_unset=True)
    for key, value in taskSchedule_data.items():
        setattr(db_taskSchedule, key, value)
    session.add(db_taskSchedule)
    session.commit()
    session.refresh(db_taskSchedule)
    return db_taskSchedule
```


Код ceрвиса Notification:
```python
class NotificationDefault(SQLModel):
    created_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    message: Optional[str] = ''
    is_read: bool = False

class Notification(NotificationDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    task: int = Field(default=None, foreign_key="task.id")
    parent_task: Optional[Task] = Relationship(back_populates="notification_list")
    

class NotificationTask(NotificationDefault):
    parent_task: Optional[Task] = None
```

Код ceрвиса Notification:
```python
class NotificationDefault(SQLModel):
    created_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    message: Optional[str] = ''
    is_read: bool = False

class Notification(NotificationDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    task: int = Field(default=None, foreign_key="task.id")
    parent_task: Optional[Task] = Relationship(back_populates="notification_list")
    

class NotificationTask(NotificationDefault):
    parent_task: Optional[Task] = None
```

Код ceрвиса Notification:
```python
class NotificationDefault(SQLModel):
    created_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    message: Optional[str] = ''
    is_read: bool = False

class Notification(NotificationDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    task: int = Field(default=None, foreign_key="task.id")
    parent_task: Optional[Task] = Relationship(back_populates="notification_list")
    

class NotificationTask(NotificationDefault):
    parent_task: Optional[Task] = None
```


Код ceрвиса Notification:
```python
class NotificationDefault(SQLModel):
    created_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    message: Optional[str] = ''
    is_read: bool = False

class Notification(NotificationDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    task: int = Field(default=None, foreign_key="task.id")
    parent_task: Optional[Task] = Relationship(back_populates="notification_list")
    

class NotificationTask(NotificationDefault):
    parent_task: Optional[Task] = None
```


