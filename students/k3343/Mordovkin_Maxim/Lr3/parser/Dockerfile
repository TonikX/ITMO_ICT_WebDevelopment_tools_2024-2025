FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY parser.py ./

EXPOSE 8001

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "parser:app", "--host", "0.0.0.0", "--port", "8001"]
