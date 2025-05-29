Создано отдельное приложение fastAPI для парсера

```python
@app.post("/parse")
async def parse(url: str):
    try:
        return await parser.parse(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

И создан DockerFile для обоих FastApi приложений

```
FROM python:3.13

ARG APP=app

WORKDIR /${APP}

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


COPY src/ .
```

А также docker-compose.yml, где подняты оба сервиса и postgree

```
services:
  postgres:
    image: postgres:15
    container_name: postgres
    environment:
      - POSTGRES_USER
      - POSTGRES_PASSWORD
      - POSTGRES_DB
    ports:
      - "5432:5432"
    volumes:
      - ./postgres_data:/var/lib/postgresql/data

  parser:
    depends_on:
      - postgres
    build:
      context: ./parser
      dockerfile: DockerFile
    command: uvicorn main:app --host 0.0.0.0 --port 8000
    env_file: .env
    ports:
      - "8000:8000"
    container_name: parser

  app:
    depends_on:
      - postgres
    build:
      context: ./app
      dockerfile: DockerFile
    ports:
      - "7000:7000"
    env_file: .env
    container_name: app
```


Всесь код юыл протестирован и начата подзадача 2.

### Вывод
Были получены знания о составлении DockerFile и docker-compose.yml