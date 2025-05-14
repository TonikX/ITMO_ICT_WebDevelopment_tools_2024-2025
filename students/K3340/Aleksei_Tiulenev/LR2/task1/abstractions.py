from typing import Protocol

class SummationImplementation(Protocol):
    def calculate_sum(self, n: int, num_tasks: int) -> int:
        ...
