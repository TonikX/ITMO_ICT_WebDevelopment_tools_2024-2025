FROM python:3.13.3-alpine

WORKDIR /usr/src/app

RUN apk --no-cache add postgresql-dev

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .