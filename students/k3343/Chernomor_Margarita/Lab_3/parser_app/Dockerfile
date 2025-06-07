FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY parser_app/ ./parser_app/

COPY app/connection.py ./app/connection.py

COPY app/models/ ./app/models/

COPY .env .

COPY . .

CMD ["uvicorn", "parser_app.main:app", "--host", "0.0.0.0", "--port", "8001"]
