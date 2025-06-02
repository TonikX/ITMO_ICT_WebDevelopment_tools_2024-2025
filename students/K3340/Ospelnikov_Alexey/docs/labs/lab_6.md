# Лабораторная работа №6


## Задача 1
Различия между threading, multiprocessing и async в Python
Задача: Напишите три различных программы на Python, использующие каждый из подходов: threading, multiprocessing и async. Каждая программа должна решать считать сумму всех чисел от 1 до 10000000000000. Разделите вычисления на несколько параллельных задач для ускорения выполнения.

Подробности задания:

1. Напишите программу на Python для каждого подхода: threading, multiprocessing и async.
2. Каждая программа должна содержать функцию calculate_sum(), которая будет выполнять вычисления.
3. Для threading используйте модуль threading, для multiprocessing - модуль multiprocessing, а для async - ключевые слова async/await и модуль asyncio.
4. Каждая программа должна разбить задачу на несколько подзадач и выполнять их параллельно.
5. Замерьте время выполнения каждой программы и сравните результаты.


Обычный подсчет
```python
for max_value in range(5, 10):
    t = time.time()
    cnt = 0
    for i in range(1, 10 ** max_value + 1):
        cnt += i
    
    print("Counter value:", cnt)
    print("Time:", time.time() - t)
    print("--\--\--\--\--\--\--\--\--")
```


Threading:
```python
n = 1_000_000_000
sums = []
lock = threading.Lock()

def counter(begin, shift):
    global sums
    part = sum(range(begin, n, shift))
    lock.acquire()
    sums.append(part)
    lock.release()

def calculate_sum():
    thread_count = 100
    threads = [threading.Thread(target=counter, args=(i, thread_count)) for i in range(thread_count)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    start_time = time.time()
    calculate_sum()
    print("Сумма:", sum(sums), "Время:", time.time() - start_time)
```

Multiprocessing:
```python
sums = []
n = 1_000_000_000

def counter(x):
    return sum(range(x[0], n, x[1]))


def calculate_sums():
    process_count = 10
    with multiprocessing.Pool(processes=process_count) as pool:
        it = pool.imap_unordered(counter, [(i, process_count) for i in range(process_count)], chunksize=1)
        return sum(it)


if __name__ == '__main__':
    start = time.time()
    result = calculate_sums()
    print("Сумма:", result, "Время:", time.time() - start)
```


Async:
```python
n = 1_000_000_000

async def counter(begin, shift):
    return sum(range(begin, n, shift))

async def calculate_sum():
    coroutines_count = 100
    tasks = [counter(i, coroutines_count) for i in range(coroutines_count)]
    return await asyncio.gather(*tasks)

if __name__ == '__main__':
    start = time.time()
    sums = asyncio.run(calculate_sum())
    print("Сумма:", sum(sums), "Время:", time.time() - start)
```

### Результаты 

| **Метод**       | **Время выполнения (сек.)** |
|-----------------|:---------------------:|
| Sum             | 32.69                 |
| Threading       | 32.49                 |
| Multiprocessing | 6.07                  |
| Async           | 35.32                 |

### Выводы

1. В подсчете использование threading не дает почти никакого прироста по сравнению с однопотоком, как и Async
2. Multiprocessing с большим преимуществом выигрывает в операциях подсчета



## Задача 2

Параллельный парсинг веб-страниц с сохранением в базу данных
Задача: Напишите программу на Python для параллельного парсинга нескольких веб-страниц с сохранением данных в базу данных с использованием подходов threading, multiprocessing и async. Каждая программа должна парсить информацию с нескольких веб-сайтов, сохранять их в базу данных.

Подробности задания:

1. Напишите три различных программы на Python, использующие каждый из подходов: threading, multiprocessing и async.
2. Каждая программа должна содержать функцию parse_and_save(url), которая будет загружать HTML-страницу по указанному URL, парсить ее, сохранять заголовок страницы в базу данных и выводить результат на экран.
3. Используйте базу данных из лабораторной работы номер 1 для заполенния ее данными. Если Вы не понимаете, какие таблицы и откуда Вы могли бы заполнить с помощью парсинга, напишите преподавателю в общем чате потока.
4. Для threading используйте модуль threading, для multiprocessing - модуль multiprocessing, а для async - ключевые слова async/await и модуль aiohttp для асинхронных запросов.
5. Создайте список нескольких URL-адресов веб-страниц для парсинга и разделите его на равные части для параллельного парсинга.
6. Запустите параллельный парсинг для каждой программы и сохраните данные в базу данных.
7. Замерьте время выполнения каждой программы и сравните результаты.
Дополнительные требования:

Сделайте документацию, содержащую описание каждой программы, используемые подходы и их особенности.
Включите в документацию таблицы, отображающие время выполнения каждой программы.
Прокомментируйте результаты сравнения времени выполнения программ на основе разных подходов.

Список сайтов:

1. <https://www.leadertask.ru/blog/celi-na-etot-god>
2. <https://singularity-app.ru/blog/tseli-na-god/?ysclid=maut5kcczr776505947>
3. <https://instalook.ru/blog/spisok-celey-na--god?ysclid=mauug5wya098753197>
4. <https://www.coaching-online.org/monthly-goals/>
5. <https://facedragons.com/personal-development/list-of-goal-ideas/>

Главный файл:
```python
def get_sqlalchemy_engine():
    return create_engine(sqlalchemy_url)

def test_connection():
    engine = get_sqlalchemy_engine()
    with engine.connect() as connection:
        print("Подключение к базе данных успешно установлено!")
        
        return True

if __name__ == "__main__":
    test_connection()
    run_parser(sqlalchemy_url, links) 
    run_threading_parser(sqlalchemy_url, links)
    run_multiprocessing_parser(sqlalchemy_url, links)    
    run_async_parser(sqlalchemy_url, links) 
```

Обычный парсинг:
```python
def save(engine, task_table, task_name):
    
    with engine.connect() as connection:
        try:
            stmt = insert(task_table).values(
                name=task_name,
                deadline='2026-01-01 00:00:00.000',
                status='in_progress',
                priority='medium',
                created_by=0
            )
            
            result = connection.execute(stmt)
            connection.commit()
            return result
        except Exception as e:
            connection.rollback()
            raise
        engine.dispose()

def parse_and_save(sqlalchemy_url, url):
    engine = create_engine(sqlalchemy_url)
    metadata = MetaData()
    task_table = Table(
        'task', 
        metadata,
        autoload_with=engine
    )        
    resp = req.get(url)
 
    soup = BeautifulSoup(resp.text, 'html.parser')
    if url in [
            'https://www.leadertask.ru/blog/celi-na-etot-god',
            'https://www.makingsenseofcents.com/2022/12/goal-ideas.html',
            'https://facedragons.com/personal-development/list-of-goal-ideas/'
            ]:
        soup = soup.find_all('ul', {'class': 'wp-block-list'})
    else:
        soup = soup.find_all('ol')
    tasks = []
    for tag in soup:
        for task_index in tag.text.splitlines():
            if task_index != '':
                tasks.append(task_index)
    save(engine, task_table, tasks)      
        
def process_urls(urls, sqlalchemy_url):
    for url in urls:
        parse_and_save(sqlalchemy_url, url)
        
def parser(sqlalchemy_url, urls):
    start_time = time.time()
    process_urls(urls, sqlalchemy_url)
    
    elapsed_time = time.time() - start_time
    print(f"Parser: {elapsed_time:.2f} сек.")
    
    
def run_parser(sqlalchemy_url, urls):
    parser(sqlalchemy_url, urls)
```


Threading:
```python
def save(engine, task_table, task_name):
    
    with engine.connect() as connection:
        try:
            stmt = insert(task_table).values(
                name=task_name,
                deadline='2026-01-01 00:00:00.000',
                status='in_progress',
                priority='medium',
                created_by=0
            )
            
            result = connection.execute(stmt)
            connection.commit()
            return result
        except Exception as e:
            connection.rollback()
            raise
        engine.dispose()

def parse_and_save(sqlalchemy_url, url):
    engine = create_engine(sqlalchemy_url)
    metadata = MetaData()
    task_table = Table(
        'task', 
        metadata,
        autoload_with=engine
    )        
    resp = req.get(url)
 
    soup = BeautifulSoup(resp.text, 'html.parser')
    if url in [
            'https://www.leadertask.ru/blog/celi-na-etot-god',
            'https://www.makingsenseofcents.com/2022/12/goal-ideas.html',
            'https://facedragons.com/personal-development/list-of-goal-ideas/'
            ]:
        soup = soup.find_all('ul', {'class': 'wp-block-list'})
    else:
        soup = soup.find_all('ol')
    
    tasks = []
    for tag in soup:
        for task_index in tag.text.splitlines():
            if task_index != '':
                tasks.append(task_index)
    save(engine, task_table, tasks)  
                
    
def threading_parser(sqlalchemy_url, urls):
    start_time = time.time()
    num_threads = 6
    chunk_size = len(urls) // num_threads
    threads = []
    
    for i in range(num_threads):
        start = i * chunk_size
        end = start + chunk_size if i < num_threads - 1 else len(urls)
        thread_urls = urls[start:end]
        
        thread = threading.Thread(
            target=lambda urls: [parse_and_save(sqlalchemy_url, url) for url in urls],
            args=(thread_urls,),
            name=f"Thread-{i+1}"
        )
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    elapsed_time = time.time() - start_time
    print(f"Threading: {elapsed_time:.2f} сек.")

def run_threading_parser(sqlalchemy_url, urls):
    threading_parser(sqlalchemy_url, urls)
```



Multiprocessing:
```python
def save(engine, task_table, task_name):
    
    with engine.connect() as connection:
        try:
            stmt = insert(task_table).values(
                name=task_name,
                deadline='2026-01-01 00:00:00.000',
                status='in_progress',
                priority='medium',
                created_by=0
            )
            
            result = connection.execute(stmt)
            connection.commit()
            return result
        except Exception as e:
            connection.rollback()
            raise
        engine.dispose()

def parse_and_save(sqlalchemy_url, url):
    engine = create_engine(sqlalchemy_url)
    metadata = MetaData()
    task_table = Table(
        'task', 
        metadata,
        autoload_with=engine
    )        
    resp = req.get(url)
 
    soup = BeautifulSoup(resp.text, 'html.parser')
    if url in [
            'https://www.leadertask.ru/blog/celi-na-etot-god',
            'https://www.makingsenseofcents.com/2022/12/goal-ideas.html',
            'https://facedragons.com/personal-development/list-of-goal-ideas/'
            ]:
        soup = soup.find_all('ul', {'class': 'wp-block-list'})
    else:
        soup = soup.find_all('ol')
    tasks = []
    for tag in soup:
        for task_index in tag.text.splitlines():
            if task_index != '':
                tasks.append(task_index)
    save(engine, task_table, tasks)       
        
def process_urls(urls, sqlalchemy_url):
    for url in urls:
        parse_and_save(sqlalchemy_url, url)
        
def multiprocessing_parser(sqlalchemy_url, urls):
    start_time = time.time()
    num_processes = 5
    
    chunk_size = len(urls) // num_processes
    chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]
    
    processes = []
    for chunk in chunks:
        process = multiprocessing.Process(
            target=process_urls,
            args=(chunk, sqlalchemy_url)
        )
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join()
    
    elapsed_time = time.time() - start_time
    print(f"Multiprocessing: {elapsed_time:.2f} сек.")
    
    
def run_multiprocessing_parser(sqlalchemy_url, urls):
    multiprocessing_parser(sqlalchemy_url, urls)
```


Async:
```python
async def save(engine, task_table, tasks):
    
    with engine.connect() as connection:
        try:
            for task_i in tasks:
                stmt = insert(task_table).values(
                    name=task_i,
                    deadline='2026-01-01 00:00:00.000',
                    status='in_progress',
                    priority='medium',
                    created_by=0
                )
                
                result = connection.execute(stmt)
                connection.commit()
                return result
        except Exception as e:
            connection.rollback()
            raise
        engine.dispose()

async def parse_and_save(sqlalchemy_url, session, url):
    engine = create_engine(sqlalchemy_url)
    
    metadata = MetaData()
    task_table = Table(
        'task', 
        metadata,
        autoload_with=engine
    )        
    try:
        async with session.get(url, timeout=10) as response:
            html = await response.text()        
        soup = BeautifulSoup(html, 'html.parser')
        if url in [
            'https://www.leadertask.ru/blog/celi-na-etot-god',
            'https://www.makingsenseofcents.com/2022/12/goal-ideas.html',
            'https://facedragons.com/personal-development/list-of-goal-ideas/'
            ]:
            soup = soup.find_all('ul', {'class': 'wp-block-list'})
        else:
            soup = soup.find_all('ol')
        tasks = []
        for tag in soup:
            for task_index in tag.text.splitlines():
                if task_index != '':
                    tasks.append(task_index)
        await save(engine, task_table, tasks)
    
    except Exception as e:
        print(f"Error parsing {url}: {e}")

async def async_parser(sqlalchemy_url, urls):
    start_time = time.time()
    
    connector = aiohttp.TCPConnector()
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [parse_and_save(sqlalchemy_url, session, url) for url in urls]
        await asyncio.gather(*tasks)
    
    elapsed_time = time.time() - start_time
    print(f"Async: {elapsed_time:.2f} сек.")

def run_async_parser(sqlalchemy_url, sample_urls):
    asyncio.run(async_parser(sqlalchemy_url, sample_urls))
```

### Результаты

| **Метод**           | **Время выполнения (сек.)** |
|-----------------|:---------------------:|
| Parser          | 13.99                 |
| Threading       | 12.99                 |
| Multiprocessing | 6.38                  |
| Async           | 3.73                  |

### Выводы

1. В парсинге использование threading не дает почти никакого прироста по сравнению с однопотоком
2. Async с большим преимуществом выигрывает в подобных парсингу операциях
3. Multiprocessing - неплохой выбор
