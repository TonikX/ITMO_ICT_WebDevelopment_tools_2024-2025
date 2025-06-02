FROM python:3.10-slim-buster

WORKDIR /app

# Устанавливаем curl и другие необходимые зависимости
RUN apt-get update && apt-get install -y \
    curl \
    netcat-traditional \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY parser/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY parser/. .

COPY common /app/common

ENV PYTHONPATH=/app:/app/common
ENV APP_ENV=parsers

EXPOSE 8001

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]