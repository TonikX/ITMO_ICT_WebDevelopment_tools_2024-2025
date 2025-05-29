FROM python:3.11-slim

WORKDIR /parser

COPY requirements.txt /parser/

RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r /parser/requirements.txt

COPY ./parser /parser

EXPOSE 8001

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]