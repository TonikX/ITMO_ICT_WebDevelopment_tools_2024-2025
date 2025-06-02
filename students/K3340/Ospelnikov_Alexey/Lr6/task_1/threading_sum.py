import threading
import time

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