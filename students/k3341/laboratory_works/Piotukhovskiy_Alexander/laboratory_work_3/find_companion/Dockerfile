FROM python:3.10-slim

WORKDIR /find_companion

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./alembic.ini .
COPY ./alembic ./alembic
COPY ./app ./app

