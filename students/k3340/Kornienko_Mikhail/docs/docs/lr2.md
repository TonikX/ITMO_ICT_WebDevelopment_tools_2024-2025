# Отчет по лабораторной работе №2

## Задание 1

### Результаты

1. Threading

```python
Sum: 500000000500000000
Execution Time: 19.62 seconds
```

2. Multiprocessing

```python
Sum: 500000000500000000
Execution Duration: 5.94 seconds
```

3. Async

```python
Sum: 500000000500000000
Execution Duration: 21.17 seconds
```

## Задание 2

Использовал сервис: https://timus.online

Парсинг задачи:
```python
import requests
from bs4 import BeautifulSoup
from sqlmodel import SQLModel, create_engine, Session, select
from models import *

db_url = 'postgresql://dbuser:12345678@localhost:25432/db'
engine = create_engine(db_url, echo=True)
SQLModel.metadata.create_all(engine)


def parse_task(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find('h2', class_='problem_title')

    text = ''
    texts = soup.find_all('div', class_='problem_par_normal')
    for t in texts:
        text += t.text.strip() + '\n'

    return title.text, text

def save_task(title, text):
    with Session(engine) as session:
        task = Task(
            title=title,
            description=text,
        )
        session.add(task)
        session.commit()

def parse_and_save(url):
    title, text = parse_task(url)
    save_task(title, text)
```

### Результаты

1. Threading

```python
Total execution time: 5.68 seconds
```

2. Multiprocessing

```python
Total execution time: 5.54 seconds
```

3. Async

```python
Total execution time: 0.86 seconds
```