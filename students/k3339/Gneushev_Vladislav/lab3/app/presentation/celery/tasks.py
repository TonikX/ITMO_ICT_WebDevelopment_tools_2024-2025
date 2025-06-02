from app.celery.app import celery_app, container
from app.services.bus_parser import BusParserService
import asyncio

from app.services.buses import BusService


async def _parse_and_save_bus_types(url: str):
    async with container() as c:
        parser_service = await c.get(BusParserService)
        bus_service = await c.get(BusService)

        bus_types = parser_service.fetch_bus_types(url)
        await bus_service.add_bus_types(bus_types)


@celery_app.task(name="parse_bus_types")
def parse_and_save_bus_types(url: str) -> dict:
    asyncio.run(_parse_and_save_bus_types(url))
