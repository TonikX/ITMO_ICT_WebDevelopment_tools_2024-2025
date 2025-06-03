В начале я создал dockerfile для проекта app (fast api приложение) и для парсера.
Выглядят они одинаково. Потом настроил requirements.txt

```python
FROM python:3.9
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /code
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
```
Парсер был переделан так, чтобы принимать http запросы и возвращать json:
```python
import requests
from fastapi import FastAPI, HTTPException


def fetch_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) "
                      "Gecko/20100101 Firefox/138.0"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.text


def parse_data(url: str):
    html = fetch_html(url)
    title = html.split('<title itemprop="headline">')[1].split('</title>')[0]
    wealth = html.split('profile-info__item-value">$')[1].split('B</div>')[0]
    return {
        "title": title,
        "wealth": wealth
    }


app = FastAPI()


@app.get("/parse")
def parse(url: str):
    try:
        return parse_data(url)
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

```

Всё это было объединено docker-compose.yml:
```yaml
services:
  app:
    build:
      context: ./app
    container_name: app_container
    ports:
      - "8000:80"
    depends_on:
      - db
      - parser
    networks:
      - network
    environment:
      DB_ADMIN: "postgresql+pg8000://postgres:12345678@postgres_container:5432/appdb"
      PARSER_URL: "http://parser_container:80/parse"

  db:
    image: postgres:17.2
    container_name: postgres_container
    ports:
      - "5432:5432"
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: 12345678
      POSTGRES_DB: appdb
    volumes:
      - ~/postgres-data:/var/lib/postgresql/data
    networks:
      - network

  parser:
    build:
      context: ./parser
    container_name: parser_container
    networks:
      - network

networks:
  network:
```

Внутрь app добавил вызов парсера и протестировал работу, всё ок.
После этого я начал добавлять celery. Переделал парсер:
```python
import os
from celery import Celery
import requests

REDIS_BROKER = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
REDIS_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

celery_app = Celery("parser", broker=REDIS_BROKER, backend=REDIS_BACKEND)

@celery_app.task
def parse_url(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    html = resp.text

    title = html.split('<title itemprop="headline">')[1].split('</title>')[0]
    wealth = html.split('profile-info__item-value">$')[1].split('B</div>')[0]
    wealth = wealth.replace('.', '') if wealth else "0"
    return {"title": title, "wealth": wealth}
```

Потом переделал app, добавил вместо одного старого два новых эндпоинта для взаимодействия с celery
```python
@app.post("/schedule-parse")
async def schedule_parse(url: str):
    task = celery.send_task("main.parse_url", args=[url])
    return {"task_id": task.id}


@app.get("/parse-result/{task_id}")
async def parse_result(task_id: str):
    res = AsyncResult(task_id, app=celery)
    if res.ready():
        return {"status": res.status, "result": res.result}
    else:
        return {"status": res.status}
```

Обновил docker-compose.yml, убрал оттуда парсер и добавил его как celery worker'а и редис:
```yaml
services:
  app:
    build:
      context: ./app
    container_name: app_container
    ports:
      - "8000:80"
    depends_on:
      - db
      - redis
      - celery_worker
    networks:
      - network
    environment:
      DB_ADMIN: "postgresql+pg8000://postgres:12345678@postgres_container:5432/appdb"
      CELERY_BROKER_URL: "redis://redis:6379/0"
      CELERY_RESULT_BACKEND: "redis://redis:6379/1"

  db:
    image: postgres:17.2
    container_name: postgres_container
    ports:
      - "5432:5432"
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: 12345678
      POSTGRES_DB: appdb
    volumes:
      - ~/postgres-data:/var/lib/postgresql/data
    networks:
      - network

  redis:
    image: redis:8-alpine
    container_name: redis_container
    ports:
      - "6379:6379"
    networks:
      - network

  celery_worker:
    build:
      context: ./parser
    container_name: celery_worker_container
    depends_on:
      - redis
      - db
    networks:
      - network
    environment:
      CELERY_BROKER_URL: "redis://redis:6379/0"
      CELERY_RESULT_BACKEND: "redis://redis:6379/1"
      DB_ADMIN: "postgresql+pg8000://postgres:12345678@postgres_container:5432/appdb"
    command: celery -A main worker --concurrency=4

networks:
  network:
```

Так выглядит работа эндпоинтов:
![img_3.png](img_3.png)
![img_4.png](img_4.png)