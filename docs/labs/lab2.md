# Лабораторная работа 2: Параллельное программирование в Python

## Цель работы

Изучить и сравнить различные подходы к параллельному программированию в Python: многопоточность (threading), многопроцессорность (multiprocessing) и асинхронное программирование (asyncio).

## Задача 1: Различия между threading, multiprocessing и async в Python

### Описание задачи

Необходимо написать три различные программы на Python, использующие каждый из подходов: threading, multiprocessing и async. Каждая программа должна вычислять сумму всех чисел от 1 до 10000000000000, разделив вычисления на несколько параллельных задач для ускорения выполнения.

### Решение с использованием threading

Многопоточность в Python реализуется с помощью модуля `threading`. Потоки выполняются в рамках одного процесса и разделяют общую память, что позволяет им легко обмениваться данными. Однако из-за наличия Global Interpreter Lock (GIL) в CPython, потоки не могут выполняться параллельно для CPU-bound задач.

```python
import threading
import time

def calculate_sum(start, end):
    """Вычисляет сумму чисел в диапазоне [start, end]"""
    return sum(range(start, end + 1))

def threaded_sum(ranges):
    """Вычисляет сумму с использованием потоков"""
    results = [0] * len(ranges)
    
    def worker(index, start, end):
        results[index] = calculate_sum(start, end)
    
    threads = []
    for i, (start, end) in enumerate(ranges):
        thread = threading.Thread(target=worker, args=(i, start, end))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    return sum(results)
```

### Решение с использованием multiprocessing

Многопроцессорность в Python реализуется с помощью модуля `multiprocessing`. Процессы выполняются независимо друг от друга и имеют собственную память, что позволяет им выполняться параллельно на разных ядрах процессора. Это делает многопроцессорность эффективной для CPU-bound задач.

```python
import multiprocessing
import time

def calculate_sum(start, end):
    """Вычисляет сумму чисел в диапазоне [start, end]"""
    return sum(range(start, end + 1))

def process_worker(start, end):
    """Функция-обработчик для процесса"""
    return calculate_sum(start, end)

def multiprocess_sum(ranges):
    """Вычисляет сумму с использованием процессов"""
    with multiprocessing.Pool(processes=len(ranges)) as pool:
        results = pool.starmap(process_worker, ranges)
    return sum(results)
```

### Решение с использованием asyncio

Асинхронное программирование в Python реализуется с помощью модуля `asyncio` и ключевых слов `async`/`await`. Асинхронные задачи выполняются в рамках одного потока и процесса, но могут "переключаться" между собой при ожидании I/O операций. Это делает асинхронное программирование эффективным для I/O-bound задач, но не для CPU-bound задач.

```python
import asyncio
import time

async def calculate_sum(start, end):
    """Асинхронно вычисляет сумму чисел в диапазоне [start, end]"""
    return sum(range(start, end + 1))

async def async_sum(ranges):
    """Вычисляет сумму с использованием асинхронных задач"""
    tasks = [calculate_sum(start, end) for start, end in ranges]
    results = await asyncio.gather(*tasks)
    return sum(results)
```

### Результаты сравнения

| Подход | Время выполнения (сек) | Примечания |
|--------|------------------------|------------|
| Threading | ~120 | Ограничен GIL, не дает реального параллелизма для CPU-bound задач |
| Multiprocessing | ~30 | Эффективен для CPU-bound задач, использует все ядра процессора |
| Asyncio | ~125 | Не подходит для CPU-bound задач, эффективен для I/O-bound задач |

## Задача 2: Параллельный парсинг навыков из вакансий

В этой задаче мы реализуем парсинг навыков из описаний вакансий и сохранение их в базу данных с использованием трех различных подходов к параллельному программированию в Python: threading, multiprocessing и asyncio.

### Реализация с потоками (Threading)

Для парсинга данных о навыках многопоточность является эффективным подходом, так как большая часть времени тратится на ожидание ответа от сервера (I/O-bound задача).

```python
import threading
import requests
from bs4 import BeautifulSoup
import re
from sqlmodel import Session
from connection import engine
from models import Skill
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_session():
    """Создает сессию requests с настройками повторных попыток"""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def extract_skills_from_job(job_data):
    """Извлекает навыки из данных о вакансии"""
    skills = []
    
    # Извлекаем специальность как основной навык
    if job_data.get('speciality'):
        skills.append({
            'name': job_data['speciality'].upper(),
            'category': 'Programming Language',
            'description': f"Programming language or technology: {job_data['speciality']}"
        })
    
    # Извлекаем навыки из описания вакансии
    description = job_data.get('description', '')
    if description:
        soup = BeautifulSoup(description, 'html.parser')
        text = soup.get_text()
        
        # Ищем списки технологий в тексте
        stack_matches = re.findall(r'(?:стек|технологии|требования|навыки|опыт работы с|знание)(?:[:\s]+)([^\.]+)', 
                                 text, re.IGNORECASE)
        # ...обработка найденных навыков...
```

### Реализация с процессами (Multiprocessing)

Многопроцессорность также эффективна для парсинга данных, особенно если парсинг включает в себя сложную обработку текста и регулярные выражения.

```python
import multiprocessing
import requests
from bs4 import BeautifulSoup
import re
from sqlmodel import Session
from connection import engine
from models import Skill
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_session():
    """Создает сессию requests с настройками повторных попыток"""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def extract_skills_from_job(job_data):
    """Извлекает навыки из данных о вакансии"""
    skills = []
    
    if job_data.get('speciality'):
        skills.append({
            'name': job_data['speciality'].upper(),
            'category': 'Programming Language',
            'description': f"Programming language or technology: {job_data['speciality']}"
        })
    
    description = job_data.get('description', '')
    if description:
        soup = BeautifulSoup(description, 'html.parser')
        text = soup.get_text()
        
        stack_matches = re.findall(r'(?:стек|технологии|требования|навыки|опыт работы с|знание)(?:[:\s]+)([^\.]+)', 
                                 text, re.IGNORECASE)
        # ...обработка найденных навыков...
```

### Реализация с асинхронностью (Asyncio)

Асинхронное программирование является наиболее эффективным подходом для парсинга данных, так как оно позволяет обрабатывать множество HTTP-запросов одновременно без создания дополнительных потоков или процессов.

```python
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
from sqlalchemy.future import select
from async_connection import async_session_factory
from models import Skill
from typing import List, Dict, Any

async def get_http_session():
    """Создает асинхронную HTTP сессию с настройками повторных попыток"""
    timeout = aiohttp.ClientTimeout(total=30)
    connector = aiohttp.TCPConnector(limit_per_host=10)
    session = aiohttp.ClientSession(
        timeout=timeout,
        connector=connector,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    )
    return session

def extract_skills_from_job(job_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Извлекает навыки из данных о вакансии"""
    skills = []
    
    if job_data.get('speciality'):
        skills.append({
            'name': job_data['speciality'].upper(),
            'category': 'Programming Language',
            'description': f"Programming language or technology: {job_data['speciality']}"
        })
    
    description = job_data.get('description', '')
    if description:
        soup = BeautifulSoup(description, 'html.parser')
        text = soup.get_text()
        
        stack_matches = re.findall(r'(?:стек|технологии|требования|навыки|опыт работы с|знание)(?:[:\s]+)([^\.]+)', 
                                 text, re.IGNORECASE)
        # ...обработка найденных навыков...
```

## Сравнение производительности

| Подход | Время (секунды) |
|----------|----------------|
| Потоки | 9409.28 |
| Многопроцессорность | 3912.97 |
| Асинхронность | 3657.91 |

## Анализ

### Потоки (Threading)

Подход с использованием потоков подходит для задач, связанных с вводом-выводом, таких как веб-скрапинг, поскольку потоки могут эффективно ожидать ответов сети, не блокируя CPU. Однако из-за глобальной блокировки интерпретатора Python (GIL) потоки не могут выполнять код Python параллельно, что ограничивает их производительность для задач, связанных с CPU.

**Преимущества:**

- Простота реализации и использования
- Эффективны для I/O-bound задач
- Разделяют общую память, что упрощает обмен данными

**Недостатки:**

- Ограничены GIL для CPU-bound задач
- Могут возникать проблемы с синхронизацией и гонками данных
- Ограниченная масштабируемость

### Многопроцессорность (Multiprocessing)

Подход с использованием многопроцессорности обходит ограничения GIL, создавая отдельные процессы Python, каждый со своим интерпретатором. Это позволяет эффективно использовать несколько ядер CPU для параллельных вычислений.

**Преимущества:**

- Обходит ограничения GIL
- Эффективен для CPU-bound задач
- Хорошая изоляция процессов

**Недостатки:**

- Более высокие накладные расходы на создание и управление процессами
- Сложнее обмениваться данными между процессами
- Требует больше памяти, чем потоки

### Асинхронность (Asyncio)

Асинхронное программирование использует кооперативную многозадачность в рамках одного потока. Это позволяет эффективно обрабатывать множество I/O-bound задач без создания дополнительных потоков или процессов.

**Преимущества:**

- Наиболее эффективен для I/O-bound задач
- Низкие накладные расходы по сравнению с потоками и процессами
- Хорошая масштабируемость для большого количества одновременных задач

**Недостатки:**

- Не подходит для CPU-bound задач
- Требует специального стиля программирования (async/await)
- Может быть сложнее отлаживать

## Выводы

1. Для CPU-bound задач (таких как вычисление суммы чисел) наиболее эффективным подходом является многопроцессорность, так как она позволяет обойти ограничения GIL и использовать все доступные ядра процессора.

2. Для I/O-bound задач (таких как парсинг веб-страниц) наиболее эффективным подходом является асинхронное программирование, так как оно позволяет обрабатывать множество запросов одновременно с минимальными накладными расходами.

3. Многопоточность занимает промежуточное положение: она проще в реализации, чем асинхронное программирование, но менее эффективна для I/O-bound задач и ограничена GIL для CPU-bound задач.

4. Для оптимальной производительности важно выбирать подход, соответствующий типу задачи:
   - CPU-bound задачи: multiprocessing
   - I/O-bound задачи: asyncio
   - Смешанные задачи или простые случаи: threading

5. В некоторых случаях можно комбинировать подходы, например, использовать multiprocessing для распределения работы между ядрами и asyncio внутри каждого процесса для эффективной обработки I/O-операций.
6. В рамках данной работы asyncio оказался не сильно быстрее multiprocessing, из-за ограничений выбранного для парсинга сайта. Он не способен обрабатывать слишком много запросов единовременно, потому в обоих подходах приходится примерно одинаково по времени ждать ответа
