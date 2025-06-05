# lab_3/fastapi.Dockerfile
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Создание директорий для uploads и static files
RUN mkdir -p /app/uploads/player_photos \
    && mkdir -p /app/uploads/player_certificates \
    && mkdir -p /app/uploads/team_logos

# Установка переменных окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Открытие порта
EXPOSE 8000

# Команда запуска
CMD ["uvicorn", "app.urls:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]