# Задание 2: Парсинг веб-страниц

## Описание задачи
Написать три программы для параллельного парсинга веб-страниц с сохранением данных в SQLite базу данных:

- Threading с requests
- Multiprocessing с requests
- Async с aiohttp

## Требования
1. Каждая программа должна содержать функцию `parse_and_save(url)`
2. Парсить заголовки страниц (`<title>` тег)
3. Сохранять результаты в базу данных SQLite
4. Обработать несколько URL параллельно
5. Замерить время выполнения

## Список тестируемых URL
```python
urls = [
    'https://httpbin.org/html',
    'https://httpbin.org/json', 
    'https://jsonplaceholder.typicode.com/',
    'https://httpbin.org/status/200',
    'https://httpbin.org/headers',
    'https://httpbin.org/ip',
    'https://httpbin.org/user-agent',
    'https://httpbin.org/delay/1'
]
```

## Структура базы данных
```sql
CREATE TABLE pages (
    id INTEGER PRIMARY KEY,
    url TEXT,
    title TEXT
)
```

## Ожидаемые результаты
- **Async** должен показать лучшие результаты для I/O операций
- **Threading** также эффективен для сетевых запросов
- **Multiprocessing** может быть избыточным для I/O задач