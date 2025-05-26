FROM python:3.13

WORKDIR /code

COPY requirements .

RUN pip install --no-cache-dir --upgrade -r /code/requirements

COPY ./Lr1 /code/Lr1

CMD ["uvicorn", "Lr1.main:app", "--host", "0.0.0.0", "--port", "8000"]