## Цель
Научиться упаковывать FastAPI приложение в Docker, интегрировать парсер данных с базой данных и вызывать парсер через API и очередь.

1. Создание FastAPI приложения: Создано в рамках лабораторной работы номер 1,
2. Создание базы данных: Создано в рамках лабораторной работы номер 1,
3. Создание парсера данных: Создано в рамках лабораторной работы номер 2,
4. Реулизуйте возможность вызова парсера по http Для этого можно сделать отдельное приложение FastAPI для парсера или воспользоваться библиотекой socket или подобными,
5. Разработка Dockerfile,
6. Создание Docker Compose файла,
7. Подзадача 2: Вызов парсера из FastAPI.


docker-compose file:
```python
services:
  lr3_pg:
    image: postgres:16-alpine
    container_name: lr3_pg
    restart: unless-stopped
    environment:
      POSTGRES_USER: lr3
      POSTGRES_PASSWORD: 12345678
      POSTGRES_DB: lr3
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - "7432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    container_name: redis
    restart: unless-stopped
    ports:
      - "6379:6379"

  parser:
    image: lr2_parser:latest
    container_name: parser
    restart: unless-stopped
    ports:
      - "18000:18000"
    environment:
      DB_URL: postgresql://lr3:12345678@lr3_pg:5432/lr3
    depends_on:
      - lr3_pg
      - redis

  celery-worker:
    image: lr2_parser:latest
    container_name: parser_celery_worker
    restart: unless-stopped
    command: celery -A celery_app worker -l info
    environment:
      DB_URL: postgresql://lr3:12345678@lr3_pg:5432/lr3
    depends_on:
      - lr3_pg
      - redis

  api:
    image: lr1_api:latest
    container_name: api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      PARSER_URL: http://parser:18000
      DATABASE_URL: postgresql://lr3:12345678@lr3_pg:15432/lr3
    depends_on:
      - parser
      - celery-worker

volumes:
  pg_data:
```

Swagger:
![swagger](lab3.png)