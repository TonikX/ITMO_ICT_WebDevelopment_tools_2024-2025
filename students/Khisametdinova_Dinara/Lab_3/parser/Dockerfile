FROM python:3.11-slim

WORKDIR /parser
#ENV PYTHONPATH=/parser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
