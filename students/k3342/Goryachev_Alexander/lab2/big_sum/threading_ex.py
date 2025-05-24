import threading
import time

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

if __name__ == "__main__":
    start_time = time.time()
    result = calculate_sum()
    end_time = time.time()

    print(f"Сумма от 1 до {MAX_NUMBER}: {result}")
    print(f"Время выполнения: {end_time - start_time:.2f} секунд")
#9.91