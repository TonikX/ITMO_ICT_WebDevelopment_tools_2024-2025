## **Вызов парсера синхронно**

Были подготовлены файлы для запуска приложения и парсера, затем были созданы 2 папки - `client` и `parser`, в каждой есть свой `Dockerfile` и `requirements.txt`.

`Dockerfile` для `client`:
```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`Dockerfile` для `parser`:
```dockerfile
FROM python:3.11

WORKDIR /parser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

Далее был создан файл `docker-compose.yml` для оркестрации контейнеров. Всего было определено 3 контейнера - приложение, парсер и база данных.

`docker-compose.yml`:
```dockerfile
services:
  postgres:
    image: postgres:17
    restart: always
    environment:
      POSTGRES_USER: user_lr3
      POSTGRES_PASSWORD: pass_lr3
      POSTGRES_DB: lr3
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5433:5432"

  client:
    build:
      context: ./client
      dockerfile: Dockerfile
    restart: always
    depends_on:
      - postgres
      - parser
    environment:
      DB_ADMIN: postgresql://user_lr3:pass_lr3@postgres:5432/lr3
      PARSER_URL: http://parser:8001
    ports:
      - "8000:8000"

  parser:
    build:
      context: ./parser
      dockerfile: Dockerfile
    restart: always
    depends_on:
      - postgres
      - redis
    environment:
      DB_ADMIN: postgresql://user_lr3:pass_lr3@postgres:5432/lr3
    ports:
      - "8001:8001"

volumes:
  pgdata:
```

После чего контейнеры были запущены, и API было протестировано. Приложение сообщило о успешно обработанном запросе, а в базе данных появилась запись с парсингом:

 ![Swagger](../imgs/screenshot1.png)
 ![Postgres](../imgs/screenshot2.png)