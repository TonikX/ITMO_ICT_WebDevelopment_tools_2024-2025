FROM python:3.13.3-alpine

ARG APP_PORT=8000

WORKDIR /usr/src/app

RUN apk --no-cache add postgresql-dev

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD alembic upgrade head && sleep 5 && uvicorn main:app --host 0.0.0.0 --port ${APP_PORT}
