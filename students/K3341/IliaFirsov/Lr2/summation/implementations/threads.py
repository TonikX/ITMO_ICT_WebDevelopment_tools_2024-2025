import threading
from summation.abstractions import SummationImplementation
from summation.utils import ColorLog

class ThreadSummation(SummationImplementation):
    def __init__(self):
        self.total = 0
        self.lock = threading.Lock()

    def worker(self, start: int, end: int, idx: int):
        print(ColorLog.blue(f"[Thread {idx}] Starting: {start} to {end}"))
        local_sum = sum(range(start, end))
        print(ColorLog.blue(f"[Thread {idx}] Finished: {start} to {end}"))
        with self.lock:
            self.total += local_sum

    def calculate_sum(self, n: int, num_tasks: int) -> int:
        threads = []
        step = n // num_tasks

        for i in range(num_tasks):
            start = i * step
            end = (i + 1) * step if i != num_tasks - 1 else n
            t = threading.Thread(target=self.worker, args=(start, end, i))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        return self.total
