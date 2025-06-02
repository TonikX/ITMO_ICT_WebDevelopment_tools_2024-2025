FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Обязательно слушаем на 0.0.0.0, иначе из web_app не достучаться
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
