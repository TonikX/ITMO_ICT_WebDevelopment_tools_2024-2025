FROM python:3.13-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --index-url=https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

CMD ["uvicorn", "main_app.main:app", "--host", "0.0.0.0", "--port", "8000"]