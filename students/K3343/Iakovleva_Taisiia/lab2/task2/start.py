import subprocess, sys, re, time

CASES = [
    ("async_parser.py",        "Asyncio"),
    ("threading_parser.py",    "Threading"),
    ("multiprocessing_parser.py","Multiprocessing")
]

def run(file, name):
    start = time.perf_counter()
    out = subprocess.check_output([sys.executable, file], text=True)
    dt = time.perf_counter() - start
    m = re.search(r"([0-9.]+)s", out.splitlines()[-1])
    return float(m.group(1)) if m else dt

if __name__ == "__main__":
    print("results:")
    for file, name in CASES:
        print(f"{name:<15}: {run(file, name):.2f} s")
