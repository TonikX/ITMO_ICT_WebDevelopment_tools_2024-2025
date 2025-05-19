import time
import threading

MAX_VALUE = 10**9
THREAD_COUNT = 100
sums = []
lock = threading.Lock()

def partial_sum(start, step):
    global sums
    part = sum(range(start, MAX_VALUE, step))
    lock.acquire()
    sums.append(part)
    lock.release()

def calculate_sum():
    threads = [
        threading.Thread(target=partial_sum, args=(i, THREAD_COUNT)) 
        for i in range(THREAD_COUNT)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    start = time.time()
    calculate_sum()
    duration = time.time() - start
    print(f"Итоговая сумма:", sum(sums))
    print(f"Затрачено времени: {duration:.3f} сек")