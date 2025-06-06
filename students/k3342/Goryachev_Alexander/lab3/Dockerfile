# Базовый образ
FROM python:3.11-slim

# Установим рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы
COPY requirements.txt .

# Установим зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё приложение
COPY app/ .

# Команда запуска
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]