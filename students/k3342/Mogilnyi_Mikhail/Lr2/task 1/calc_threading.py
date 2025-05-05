import threading

def calculate_sum(start, end, result, index):
    result[index] = sum(range(start, end))

def main():
    total = 10**9
    num_threads = 5
    chunk_size = total // num_threads
    threads = []
    results = [0] * num_threads


    for i in range(num_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size + 1
        thread = threading.Thread(target=calculate_sum, args=(start, end, results, i))
        threads.append(thread)
        thread.start()

    for t in threads:
        t.join()

    total_sum = sum(results)

    print(f"Вычисленная сумма: {total_sum}")

if __name__ == "__main__":
    main()
