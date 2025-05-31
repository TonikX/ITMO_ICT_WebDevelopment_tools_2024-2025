# Парсинг и работа с БД

Для парсинга был выбран сайт https://sletat.ru/. А именно страницы https://sletat.ru/tours/turkey/.

Список ссылок для парсинга:
```python
urls = [
    "https://sletat.ru/tours/turkey/",
    "https://sletat.ru/tours/uae/",
    "https://sletat.ru/tours/egypt/",
    "https://sletat.ru/tours/vietnam/",
    "https://sletat.ru/tours/thailand/",
    "https://sletat.ru/tours/maldives/",
    "https://sletat.ru/tours/russia/",
    "https://sletat.ru/tours/cuba/",
    "https://sletat.ru/tours/sri_lanka/",
    "https://sletat.ru/tours/china/",
    "https://sletat.ru/tours/abkhazia/",
]
```

## Результаты

1. Threading
```python
Threading total time: 5.42s
```

2. Multiprocessing

```python
Multiprocessing total time: 5.31s
```

3. Async

```python
Async total time: 2.21s
```

# Вывод

Будет некорректно сделать вывод, что эффективнее всего асинхронный подход, так как было слишком мало данных для парсинга и сохранения и подходы с потоками и процессами оказались невыигрышными, так как они требуют дополнительного времени на подготовительную работу.