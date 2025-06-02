FROM python:3.10-slim-buster

# Устанавливаем рабочую директорию
WORKDIR /app

COPY finance_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY finance_app/. .

# Копируем common из Lr3/common в /app/common
COPY common /app/common

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app:/app/common
ENV APP_ENV=production

EXPOSE 8000

# Запускаем миграции Alembic перед запуском приложения
CMD ["/bin/bash", "-c", \
    "cd /app && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"]