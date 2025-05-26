# Различия между threading, multiprocessing и async в Python

## CPU Bound Tasks

Напишите три различных программы на Python, использующие каждый из подходов: threading, multiprocessing и async. Каждая программа должна решать считать сумму всех чисел от 1 до 10000000000000. Разделите вычисления на несколько параллельных задач для ускорения выполнения.

---

### Multiprocessing

```python
MAX_NUMBER = 1_000_000_000
NUM_PROCESSES = multiprocessing.cpu_count()

def partial_sum(start, end):
    return sum(range(start, end + 1))

def calculate_sum():
    step = MAX_NUMBER // NUM_PROCESSES
    ranges = []

    for i in range(NUM_PROCESSES):
        start = i * step + 1
        end = (i + 1) * step if i < NUM_PROCESSES - 1 else MAX_NUMBER
        ranges.append((start, end))

    with multiprocessing.Pool(processes=NUM_PROCESSES) as pool:
        results = pool.starmap(partial_sum, ranges)

    return sum(results)

```
 - Создаётся пул процессов, каждый из которых получает свою часть диапазона чисел.
 - starmap вызывает partial_sum с распаковкой аргументов (start, end) из кортежей ranges.
 - Каждый процесс работает независимо, используя отдельный CPU-поток (реальное распараллеливание).
 - По завершении работы все результаты (частичные суммы) собираются и складываются в основной процесс.

### Async
```python
def blocking_sum(start, end):
    return sum(range(start, end + 1))

async def async_partial_sum(executor, start, end):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, blocking_sum, start, end)

async def calculate_sum():
    step = MAX_NUMBER // NUM_TASKS
    ranges = []

    for i in range(NUM_TASKS):
        start = i * step + 1
        end = (i + 1) * step if i < NUM_TASKS - 1 else MAX_NUMBER
        ranges.append((start, end))

    results = []
    with ThreadPoolExecutor(max_workers=NUM_TASKS) as executor:
        tasks = [
            async_partial_sum(executor, start, end)
            for start, end in ranges
        ]
        results = await asyncio.gather(*tasks)

    return sum(results)
```
 - Основной поток управляет задачами.
 - Вычисления происходят в отдельных рабочих потоках, не блокируя основной.

### Threading
```python
NUM_THREADS = 24
MAX_NUMBER = 1_000_000_000

total_sum = 0
lock = threading.Lock()

def partial_sum(start, end):
    global total_sum
    local_sum = sum(range(start, end + 1))
    with lock:
        total_sum += local_sum

def calculate_sum():
    global total_sum
    total_sum = 0
    threads = []
    step = MAX_NUMBER // NUM_THREADS

    for i in range(NUM_THREADS):
        start = i * step + 1
        end = (i + 1) * step if i < NUM_THREADS - 1 else MAX_NUMBER
        t = threading.Thread(target=partial_sum, args=(start, end))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return total_sum
```

partial_sum() :

 - Считает сумму диапазона start...end.
 - Иcпользует lock, чтобы обезопасить доступ к общей переменной total_sum.
 - Э критически важно, иначе потоки могут перезаписывать значение друг друга (condition race).

calculate_sum() :

 - 	Делит диапазон на NUM_THREADS кусков.
 - Сдаёт Thread для каждой части.
 - В потоки запускаются почти одновременно и работают параллельно.
 - Сомощью join() главный поток ждёт завершения всех потоков, прежде чем возвращать результат.

## IO Bound Tasks
Напишите программу на Python для параллельного парсинга нескольких веб-страниц с сохранением данных в базу данных с использованием подходов threading, multiprocessing и async. Каждая программа должна парсить информацию с нескольких веб-сайтов, сохранять их в базу данных.

### Multiprocessing 
```python
def create_user(username):
    user_data = {
        "username": username,
        "email": f"{username.strip()}@example.com",
        "password": "defaultpassword123"
    }
    try:
        response = requests.post(API_URL, json=user_data)
        print(f"[{username}] Status: {response.status_code}")
        print(f"Response Text: {response.text}")

        if response.headers.get("content-type") == "application/json":
            print("Parsed JSON:", response.json())
        else:
            print("Non-JSON response received")

    except Exception as e:
        print(f"Error creating {username} : {e}")

def worker(url):
    try:
        username = grab_name(url)
        create_user(username)
    except Exception as e:
        print(f"Error processing {url}: {e}")

def main():
    processes = []

    for url in urls:
        p = multiprocessing.Process(target=worker, args=(url,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
```
Каждый worker работает независимо и выполняется в отдельном процессе 
main() :

 - Проходит по списку urls.
 - Для каждого URL создаётся новый процесс (multiprocessing.Process).
 - В процессы запускаются параллельно (p.start()).
 - После запуска всех процессов, main() ждёт их завершения (p.join()).

### Async
```python
async def grab_name(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            text = await response.text()

    soup = BeautifulSoup(text, "html.parser")
    name = soup.find_all("a", class_="tm-user-info__username")[0].text
    print(name)
    return name

async def create_user(session, username):
    user_data = {
        "username": username,
        "email": f"{username.strip()}@example.com",
        "password": "defaultpassword123"
    }
    try:
        async with session.post(API_URL, json=user_data) as response:
            text = await response.text()
            print(f"[{username}] Status: {response.status}")
            print(f"Response Text: {text}")

            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                json_response = await response.json()
                print("Parsed JSON:", json_response)
            else:
                print("Non-JSON response received")

    except Exception as e:
        print(f"Error creating {username} : {e}")

async def worker(session, url):
    try:
        username = await grab_name(url)
        await create_user(session, username)
    except Exception as e:
        print(f"Error processing {url}: {e}")

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(worker(session, url))
        await asyncio.gather(*tasks)
```

Отдельная асинхронная функция grab_name

main() :

- Создаёт один ClientSession на все запросы — это правильно.
- Cоздаёт список задач worker(...).
- asyncio.gather(...) запускает все задачи одновременно и ждёт завершения.

### Threading
```python
def create_user(username):
    user_data = {
        "username": username,
        "email": f"{username.strip()}@example.com",
        "password": "defaultpassword123"
    }
    try:
        response = requests.post(API_URL, json=user_data)
        print(f"[{username}] Status: {response.status_code}")
        print(f"Response Text: {response.text}")  # <- see what's actually returned

        # Only try to parse JSON if response looks OK
        if response.headers.get("content-type") == "application/json":
            print("Parsed JSON:", response.json())
        else:
            print("Non-JSON response received")

    except Exception as e:
        print(f"Error creating {username} : {e}")

def worker(url):
    try:
        username = grab_name(url)
        create_user(username)
    except Exception as e:
        print(f"Error processing {url}: {e}")

def main():
    threads = []

    for url in urls:
        t = threading.Thread(target=worker, args=(url,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
```
main() :
 - Создаёт поток (threading.Thread) для каждого url.
 - Каждый поток вызывает worker(url) и запускается параллельно.
 - После запуска всех потоков, основной поток ждёт их завершения через .join().

## Результаты

| Способ          | CPU bound | IO Bound |
|-----------------|-----------|----------|
| Multiprocessing | 2.52      | 1.77     |
| Async           | 9.94      | 0.84     |
| Threading       | 9.91      | 1.01     |