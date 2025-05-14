import asyncio
from abstractions import SummationImplementation
from utils import ColorLog

class AsyncSummation(SummationImplementation):
    async def worker(self, start: int, end: int, idx: int) -> int:
        print(ColorLog.yellow(f"[Задача {idx}] Старт: {start} до {end}"))
        result = sum(range(start, end))
        print(ColorLog.yellow(f"[Задача {idx}] Финиш: {start} до {end}"))
        return result

    def calculate_sum(self, n: int, num_tasks: int) -> int:
        step = n // num_tasks
        tasks = []

        async def run():
            for i in range(num_tasks):
                start = i * step
                end = (i + 1) * step if i != num_tasks - 1 else n
                tasks.append(asyncio.create_task(self.worker(start, end, i)))
            results = await asyncio.gather(*tasks)
            return sum(results)

        return asyncio.run(run())
