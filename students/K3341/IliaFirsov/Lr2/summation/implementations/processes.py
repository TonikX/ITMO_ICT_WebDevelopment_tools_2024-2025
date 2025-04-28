import multiprocessing
from summation.abstractions import SummationImplementation
from summation.utils import ColorLog

class ProcessSummation(SummationImplementation):
    def worker(self, start: int, end: int, conn, idx: int):
        print(ColorLog.green(f"[Process {idx}] Starting: {start} to {end}"))
        conn.send(sum(range(start, end)))
        print(ColorLog.green(f"[Process {idx}] Finished: {start} to {end}"))
        conn.close()

    def calculate_sum(self, n: int, num_tasks: int) -> int:
        processes = []
        parent_conns = []
        step = n // num_tasks

        for i in range(num_tasks):
            start = i * step
            end = (i + 1) * step if i != num_tasks - 1 else n
            parent_conn, child_conn = multiprocessing.Pipe()
            p = multiprocessing.Process(target=self.worker, args=(start, end, child_conn, i))
            processes.append(p)
            parent_conns.append(parent_conn)
            p.start()

        total = sum(conn.recv() for conn in parent_conns)

        for p in processes:
            p.join()

        return total
