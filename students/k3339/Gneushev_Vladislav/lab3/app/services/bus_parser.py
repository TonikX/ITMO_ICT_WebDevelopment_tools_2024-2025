import random
import requests

from app.domain.entities.buses import BusType
from app.infrastructure.parsing import parse_car_types_from_html
from app.infrastructure.database.repositories.buses import BusRepository

MIN_CAPACITY = 10
MAX_CAPACITY = 100


class BusParserService:
    def __init__(self, bus_repository: BusRepository):
        self._bus_repository = bus_repository

    def _get_random_capacity(self) -> int:
        return random.randint(MIN_CAPACITY, MAX_CAPACITY)

    def fetch_bus_types(self, url: str) -> list[BusType]:
        html_content = requests.get(url).text

        raw_bus_types = parse_car_types_from_html(html_content)
        return [
            BusType(
                id=None,
                name=name,
                people_capacity=self._get_random_capacity()
            )
            for name in raw_bus_types
        ]