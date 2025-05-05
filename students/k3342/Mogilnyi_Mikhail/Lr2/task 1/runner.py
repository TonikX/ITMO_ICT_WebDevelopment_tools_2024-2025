import subprocess
import time

PROGRAMS = {
    "Threading": "calc_threading.py",
    "Multiprocessing": "calc_multiprocessing.py",
    "Asyncio": "calc_asyncio.py"
}

def run_program(name, path):
    start_time = time.time()
    subprocess.run(["python", path], check=True)
    elapsed = time.time() - start_time
    print(f"{name} completed in {elapsed:.2f} seconds.\n")
    return elapsed

def main():
    results = {}
    for name, path in PROGRAMS.items():
        elapsed = run_program(name, path)
        results[name] = elapsed

    print("\nСравнение:")
    for name, time_taken in results.items():
        if time_taken is not None:
            print(f"{name:15} — {time_taken:.2f} seconds")
        else:
            print(f"{name:15} — Failed to run")

if __name__ == "__main__":
    main()
