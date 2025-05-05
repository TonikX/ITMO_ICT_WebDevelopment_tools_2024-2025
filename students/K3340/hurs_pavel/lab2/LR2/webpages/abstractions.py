from typing import Protocol, List


class ParserImplementation(Protocol):
    def parse_and_save_all(self, urls: List[str], num_tasks: int) -> None:
        ...
