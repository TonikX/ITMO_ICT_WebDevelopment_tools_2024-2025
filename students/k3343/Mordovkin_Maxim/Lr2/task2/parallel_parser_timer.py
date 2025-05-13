import asyncio
from threading_parser import run_thread
from multiprocessing_parser import run_mp
from asyncio_parser import run_async

def main():
    print("=== threading ===")
    t = run_thread()
    print(f"time:   {t:.3f} с\n")

    print("=== multiprocessing ===")
    m = run_mp()
    print(f"time:   {m:.3f} с\n")

    print("=== asyncio ===")
    a = asyncio.run(run_async())
    print(f"time:   {a:.3f} с\n")

    print("=== compare ===")
    print(f"threading      : {t:.3f} с")
    print(f"multiprocessing: {m:.3f} с")
    print(f"asyncio        : {a:.3f} с")

if __name__ == "__main__":
    main()
