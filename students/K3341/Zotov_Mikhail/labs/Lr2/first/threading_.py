import threading
import time


def calculate_sum(a, b):
    s = 0
    for i in range(a, b + 1):
        s += i
    results.append(s)


def main(n, count_of_threads):
    start_time = time.time()
    size = n // count_of_threads
    threads = []
    for i in range(count_of_threads):
        a = i * size + 1
        b = (i + 1) * size if (i + 1) * size < n else n
        thread = threading.Thread(target=calculate_sum, args=(a, b))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    total = sum(results)
    print('Result:', total)
    end_time = time.time()
    print('Total time:', end_time - start_time)


if __name__ == '__main__':
    results = []
    main(10 ** 9, 10)
