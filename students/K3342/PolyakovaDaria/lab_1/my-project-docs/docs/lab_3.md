# Отчет по лабораторной работе №3

**Задание:**  
Упаковать FastAPI-приложение, базу данных и парсер в Docker, интегрировать синхронный и асинхронный парсинг через Celery + Redis, сохранить результаты парсинга в PostgreSQL.

## Описание реализованного функционала

### 1. Упаковка приложений в Docker  
- **`lab_3/app/Dockerfile.app`** — образ для основного FastAPI-приложения.  
- **`lab_3/parser_app/Dockerfile.parser`** — образ для FastAPI-парсера.  
- **`lab_3/docker-compose.yml`** — описание сервисов:
  - **app** (FastAPI, `Dockerfile.app`)  
  - **parser** (FastAPI, `Dockerfile.parser`)  
  - **db** (Postgres:15)  
  - **redis** (Redis:7-alpine)  
  - **worker** (Celery-воркер, `Dockerfile.app`)  
  - **volume** `postgres_data` для хранения данных Postgres.

### 2. FastAPI-приложение  
- **`lab_3/app/main.py`**:
  - При старте вызывает `init_db()` из **`app/db.py`**.  
  - Подключает роутеры из **`app/routers/`**:
    - **`auth.py`** — регистрация (`POST /auth/register`), логин (`POST /auth/login`).  
    - **`user.py`** — список пользователей (`GET /users`), смена пароля (`PUT /users/change-password`).  
    - **`tasks.py`** — CRUD-операции над задачами (`POST /tasks`, `GET /tasks`, `PUT /tasks/{id}`, `DELETE /tasks/{id}`).  
  - Описывает Swagger UI и JWT-аутентификацию в функции `custom_openapi()`.

- **`lab_3/app/db.py`** — загрузка `.env`, создание движка SQLModel и генерация таблиц.  
- **`lab_3/app/models.py`** — модели SQLModel:
  - **User**, **Task**, **TimeLog**, **DailySchedule**, **UserTaskLink**  
  - **ParsedRecord** — запись результатов парсинга.

### 3. Синхронный парсинг  
- **Endpoint в `lab_3/app/main.py`**:
```
  @app.post("/parse", tags=["Parser"])
  def parse_and_save(request: URLRequest, session: Session = Depends(get_session)):
      resp = requests.post("http://parser:8001/parse", json=request.dict(), timeout=30)
      resp.raise_for_status()
      data = resp.json()
      record = ParsedRecord(
        url=request.url,
        content_size=data["content_size"],
        raw=data.get("content", "")
      )
      session.add(record); session.commit(); session.refresh(record)
      return {"saved_id": record.id, **data}
```

- **FastAPI-парсер в `lab_3/parser_app/parser.py`**:
```
@app.post("/parse")
def parse(request: URLRequest):
    response = requests.get(request.url)
    response.raise_for_status()
    return {"message": "Parsing completed successfully!", "content_size": len(response.text)}
```

### 4. Асинхронный парсинг через Celery

- **Endpoint в `lab_3/app/main.py`:**
```
@app.post("/parse_async", tags=["Parser"])
def enqueue_parse_task(request: URLRequest):
    task = parse_url_task.delay(request.url)
    return {"task_id": task.id, "status": "Task has been submitted to background processing"}
```
- **Celery-таска в `lab_3/app/celery_worker.py`:**
```
@celery_app.task
def parse_url_task(url: str):
    resp = requests.post("http://parser:8001/parse", json={"url": url}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    record = ParsedRecord(url=url, content_size=data["content_size"], raw=data.get("content",""))
    with Session(engine) as session:
        session.add(record); session.commit(); session.refresh(record)
    return {"saved_id": record.id, **data}
```
### 5. Проверка статуса фоновых задач

- **Endpoint в `lab_3/app/main.py`:**
```
@app.get("/parse_status/{task_id}", tags=["Parser"])
def parse_status(task_id: str):
    async_result = celery_app.AsyncResult(task_id)
    return {"task_id": task_id, "status": async_result.status, "result": async_result.result}
```
### 6. Swagger UI

Генерируется в `lab_3/app/main.py` через `custom_openapi()`. В интерфейсе видно: 

- Auth, Users, Tasks (защищены JWT)

- Parser: /parse, /parse_async, /parse_status/{task_id} (доступны без JWT)

### Что было сделано

**1. Настройка проекта и окружения**

Создано виртуальное окружение, установлены зависимости:
- `lab_3/app/requirements.txt`: fastapi, uvicorn, requests, pydantic, sqlmodel, alembic, celery, redis, python-dotenv, psycopg2-binary
- `lab_3/parser_app/requirements.txt`: fastapi, uvicorn, requests, pydantic, python-multipart

**2. Конфигурация Docker**

- Написаны Dockerfile.app и Dockerfile.parser.
- Описан docker-compose.yml: все сервисы, привязка портов, том для Postgres, зависимости.

**3. Реализация основного FastAPI-приложения**

- `lab_3/app/main.py`: инициализация БД, роутеры, парсинг-эндпоинты, Swagger/JWT.
- `lab_3/app/routers/`: auth.py, user.py, tasks.py.
- `lab_3/app/db.py`, `lab_3/app/models.py`.

**4. Синхронный парсинг**

`lab_3/parser_app/parser.py` и `/parse в app/main.py`.

**5. Асинхронный парсинг**

`lab_3/app/celery_worker.py` и `/parse_async в app/main.py`.

**6. Сохранение результатов парсинга**

- Модель ParsedRecord в `lab_3/app/models.py`.
- Проверка через Python REPL:
```
from sqlmodel import Session, select
from app.db import engine
from app.models import ParsedRecord

with Session(engine) as s:
    print(s.exec(select(ParsedRecord)).all())
```

**7. Статус фоновых задач**

`/parse_status/{task_id}` в `lab_3/app/main.py`.
