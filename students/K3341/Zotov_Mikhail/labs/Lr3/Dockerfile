FROM python:3.13

WORKDIR /code

COPY requirements .

RUN pip install --no-cache-dir --upgrade -r /code/requirements

COPY . .

#CMD ["uvicorn", "Lr3.main:app", "--host", "0.0.0.0", "--port", "8000"]