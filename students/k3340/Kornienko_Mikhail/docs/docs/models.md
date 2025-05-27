# Документация моделей данных системы хакатонов

В системе реализованы следующие основные модели:

---

## User (Пользователь)

**Описание:** Представляет участника или организатора хакатона.

**Поля:**
- `id: int` — идентификатор пользователя (PK)
- `username: str` — уникальное имя пользователя
- `hashed_password: str` — хэш пароля
- `email: str` — электронная почта
- `contact_number: str` — контактный телефон
- `is_confirmed: bool` — подтверждён ли пользователь
- `is_organizer: bool` — является ли пользователь организатором
- `teams_created: List[Team]` — команды, созданные пользователем
- `teams_joined: List[Team]` — команды, в которых состоит пользователь

---

## Team (Команда)

**Описание:** Представляет команду участников, работающих над задачами хакатона.

**Поля:**
- `id: int` — идентификатор команды (PK)
- `name: str` — название команды
- `description: Optional[str]` — описание
- `leader_id: int` — ID пользователя-лидера (FK)
- `leader: User` — связь с пользователем
- `members: List[User]` — список участников команды
- `submissions: List[Submission]` — список загрузок работ от команды

---

## TeamMembership (Членство в команде)

**Описание:** Ассоциативная таблица, представляющая many-to-many связь между User и Team.

**Поля:**
- `team_id: int` — ID команды (FK)
- `user_id: int` — ID пользователя (FK)
- `role: str` — роль участника в команде
- `joined_at: datetime` — дата вступления

---

## Task (Задача)

**Описание:** Задача, публикуемая организаторами хакатона.

**Поля:**
- `id: int` — идентификатор задачи (PK)
- `title: str` — название
- `description: str` — описание
- `requirements: str` — требования к задаче
- `evaluation_criteria: str` — критерии оценки
- `created_at: datetime` — дата публикации
- `organizer_id: int` — ID организатора (FK)
- `organizer: User` — связь с организатором
- `submissions: List[Submission]` — список решений по задаче

---

## Submission (Загрузка работы)

**Описание:** Представляет решение команды на определённую задачу.

**Поля:**
- `id: int` — идентификатор загрузки (PK)
- `description: str` — описание работы
- `submission_url: Optional[str]` — ссылка на прототип или репозиторий
- `submitted_at: datetime` — дата загрузки
- `score: Optional[float]` — оценка работы
- `team_id: int` — ID команды (FK)
- `task_id: int` — ID задачи (FK)
- `team: Team` — связь с командой
- `task: Task` — связь с задачей

---

# Связи между моделями

- **User ↔ Team**: many-to-many через TeamMembership
- **Team ↔ Submission**: one-to-many
- **Task ↔ Submission**: one-to-many
- **User ↔ Task**: one-to-many (организаторы)
- **User ↔ Team (leader)**: one-to-many

_Конец документации_