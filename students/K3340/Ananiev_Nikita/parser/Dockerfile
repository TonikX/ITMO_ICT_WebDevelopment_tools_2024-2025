FROM python:3.11-slim

WORKDIR /parser

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

COPY parser.env .env

EXPOSE 4242

CMD ["uvicorn", "parser_app:app", "--host", "0.0.0.0", "--port", "4242", "--reload"]
