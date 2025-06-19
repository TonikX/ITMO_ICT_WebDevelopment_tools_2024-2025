# Async Parsing with FastAPI, Celery и Docker

##  Архитектура проекта

Проект состоит из нескольких микросервисов, работающих в Docker-контейнерах:

- `api-app`: FastAPI-приложение, основной API. Вызывает задачи парсинга и сохраняет результаты в PostgreSQL.
- `parser-app`: FastAPI-приложение, отправляет задачи в Celery.
- `celery-worker`: Обрабатывает задачи асинхронного парсинга.
- `redis`: Брокер сообщений для Celery.
- `postgres`: База данных PostgreSQL для хранения пользователей.

## Docker-compose
```dockerfile


services:
  postgres:
    image: postgres:15
    container_name: postgres
    restart: always
    environment:
      POSTGRES_USER: alexander
      POSTGRES_PASSWORD: 1111
      POSTGRES_DB: finance_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  parser-app:
    build:
      context: ./lab3
    container_name: parser-app
    ports:
      - "8000:8000"

  api-app:
    build:
      context: ./lab1
    container_name: api-app
    ports:
      - "8001:8001"

    env_file:
      - ./lab1/app/.env
    depends_on:
      - parser-app

  redis:
    image: redis:7
    container_name: redis
    ports:
      - "6379:6379"

  celery-worker:
    build:
      context: ./lab3
    container_name: celery-worker
    command: celery -A celery_worker.celery_app worker --loglevel=info
    depends_on:
      - redis
    volumes:
      - ./lab3/app:/app
    working_dir: /app
volumes:
  postgres_data:
```

##  Компоненты и их взаимодействие

### 1. Пользователь → `api-app`
Отправляет запрос на парсинг:

```
POST /parser/async-parse
{
  "url": "https://habr.com/ru/users/akibkalo/"
}
```

### 2. `api-app` → `parser-app`
Асинхронно отправляет POST-запрос на `/celery-parse` в `parser-app`:

```python
response = await client.post("http://parser-app:8000/celery-parse", json={"url": url})
```

### 3. `parser-app` → Celery
Создаёт задачу:

```python
task = parse_url.delay(url)
return {"task_id": task.id}
```

### 4. Celery (в `celery-worker`)
- Получает задачу из Redis.
- Загружает страницу по URL.
- Парсит `username` с помощью `BeautifulSoup`.
- Возвращает результат.

### 5. Проверка результата:
Через:

```
GET /parser/result/{task_id}
```

FastAPI в `api-app` проверяет состояние задачи через Celery и при готовности получает результат.

### 6. Сохранение результата:
Когда имя пользователя получено — создаётся пользователь в базе:

```python
parsed_user = User(
    username=username,
    email=username + str(randint(1,1000)) + "@mail.ru",
    password="1111",
    hashed_password=hash_password("1111")
)
session.add(parsed_user)
session.commit()
```
