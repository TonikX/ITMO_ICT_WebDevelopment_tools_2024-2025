import time
import subprocess


def run_parser(name: str, command: list):
    start = time.time()
    subprocess.run(command)
    end = time.time()
    duration = end - start
    return name, duration


def main():
    results = []

    # threading
    results.append(run_parser("Threading", ["python", "parse_threading.py"]))

    # multiprocessing
    results.append(run_parser("Multiprocessing", ["python", "parse_multiprocessing.py"]))

    # asyncio
    results.append(run_parser("Asyncio", ["python", "parse_asyncio.py"]))

    # Итоговая таблица
    print("\nСравнение времени выполнения:")
    print(f"{'Метод':<20} | {'Время (сек.)':>12}")
    print("-" * 35)
    for name, duration in results:
        print(f"{name:<20} | {duration:>12.2f}")
    print("-" * 35)


if __name__ == "__main__":
    main()
