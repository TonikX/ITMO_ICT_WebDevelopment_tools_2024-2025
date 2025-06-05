FROM python:3.12-slim

WORKDIR /parser

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY parser_service_app ./parser_service_app

CMD ["uvicorn", "parser_service_app.main:app", "--host", "0.0.0.0", "--port", "8001"]
