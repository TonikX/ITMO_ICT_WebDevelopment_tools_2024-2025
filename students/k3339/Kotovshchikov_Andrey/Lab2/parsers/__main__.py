import asyncio
import logging
import pathlib
import time
from functools import cached_property
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, CliApp

from parsers.asyncio import main as asyncio_main
from parsers.logger import setup_logger
from parsers.processes import main as process_main
from parsers.threads import main as threads_main

logger = logging.getLogger(__name__)


class ParserSettings(BaseSettings):
    concurency: Literal["asyncio", "processes", "threads"] = "asyncio"
    urls_path: pathlib.Path

    @computed_field
    @cached_property
    def urls(self) -> set[str]:
        urls: set[str] = set()
        for url in self.urls_path.read_text().splitlines():
            if not url:
                continue

            urls.add(url.strip())

        return urls


def main() -> None:
    setup_logger()
    start_parser = None

    cli = CliApp.run(ParserSettings)
    if cli.concurency == "asyncio":
        start_parser = lambda: asyncio.run(asyncio_main(cli.urls))
    elif cli.concurency == "threads":
        start_parser = lambda: threads_main(cli.urls)
    elif cli.concurency == "processes":
        start_parser = lambda: process_main(cli.urls)

    if start_parser is None:
        raise ValueError("Invalid concurency param")

    logger.info("Start %s parser", cli.concurency)
    start_time = time.perf_counter()
    start_parser()

    logger.info(
        "Stop %s parser | Time: %s",
        cli.concurency,
        time.perf_counter() - start_time,
    )


if __name__ == "__main__":
    main()
