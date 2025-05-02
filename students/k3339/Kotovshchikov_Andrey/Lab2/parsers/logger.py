import logging
import sys


def setup_logger() -> None:
    formatter = logging.Formatter(
        fmt="[%(levelname)s] [%(asctime)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logging.basicConfig(
        handlers=[console],
        level=logging.INFO,
    )
