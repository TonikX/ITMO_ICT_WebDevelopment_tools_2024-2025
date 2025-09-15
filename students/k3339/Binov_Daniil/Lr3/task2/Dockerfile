FROM python:3.9-slim

WORKDIR /parser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY parser_app.py .

CMD ["uvicorn", "parser_app:app", "--host", "0.0.0.0", "--port", "8001"]