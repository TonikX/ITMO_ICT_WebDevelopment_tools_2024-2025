## Лабораторная работа №3.

# Цель

Научиться упаковывать FastAPI приложение в Docker, интегрировать парсер данных с базой
данных и вызывать парсер через API и очередь.

# Ход работы

1. Установим зависимости

```bash
pip install celery redis requests beautifulsoup4 aiohttp
```

2. Парсер как отдельный сервис

```python
from fastapi import FastAPI, HTTPException
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List

app = FastAPI(title="Parser Service")

async def parse_url(url: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                title = soup.title.string.strip() if soup.title else "No title"
                return title
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Error parsing {url}: {e}")

@app.post("/parse", response_model=List[dict])
async def parse_urls(urls: List[str]):
    tasks = [parse_url(url) for url in urls]
    titles = await asyncio.gather(*tasks, return_exceptions=True)
    results = [{"url": urls[i], "title": titles[i] if not isinstance(titles[i], Exception) else str(titles[i])} for i in range(len(urls))]
    return results
```

3. Создайем `requirements.txt`

4. Разрабатываем докерфайлы для приложения и парсера

5. Создаем Docker Compose файла

```yaml
services:
  db:
    image: postgres:13  
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_password  
      POSTGRES_DB: time_manager_db
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data  

  fastapi:
    build: . 
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:your_password@db/time_manager_db  
      SECRET_KEY: your_random_secret_key  
    depends_on:
      - db  
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

  parser:
    build: ./task2  
    ports:
      - "8001:8001"
    command: ["uvicorn", "parser_app:app", "--host", "0.0.0.0", "--port", "8001"]

  redis:
    image: redis:6  
    ports:
      - "6379:6379"

  celery_worker:
    build: . 
    command: celery -A celery_app worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://postgres:your_password@db/time_manager_db
      CELERY_BROKER_URL: redis://redis:6379/0  
      CELERY_RESULT_BACKEND: redis://redis:6379/0
    depends_on:
      - db
      - redis
      - parser  

volumes:
  db_data:
```

6. Интегрируем Celery и создаем задачи

```python
from celery_app import app
import requests
from app.crud.tasks import create_task
from app.schemas import TaskCreate
from app.connection import get_session

@app.task
def parse_and_save_task(url: str, user_id: int):
    try:
        parser_url = "http://parser:8001/parse"  
        response = requests.post(parser_url, json=[url])
        response.raise_for_status()
        results = response.json()
        title = results[0]['title'] if results else "No title"

        with get_session() as session:
            task = TaskCreate(title=title, description=url)
            create_task(session, task, user_id)
        return {"status": "success", "url": url, "title": title}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

7. Добавляем эндпоинт для вызова парсера

```python
@router.post("/parse")
def parse_url(url: str, current_user: User = Depends(get_current_user)):
    task = parse_and_save_task.delay(url, current_user.id)
    return {"task_id": task.id, "message": "Parsing started asynchronously"}
```

8. Запускаем и тестируем

# Выводы

В ходе этой лабораторной работы я научился работать с докером и обрабатывать многопоточные запросы с приложения.