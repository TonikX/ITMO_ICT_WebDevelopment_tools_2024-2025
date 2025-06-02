FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей для парсера
COPY parser_requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r parser_requirements.txt

# Копирование парсеров и FastAPI приложения для парсера
COPY parsers/ ./parsers/
COPY parser_app.py .

# Установка переменных окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Открытие порта
EXPOSE 8001

# Команда запуска
CMD ["uvicorn", "parser_app:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]