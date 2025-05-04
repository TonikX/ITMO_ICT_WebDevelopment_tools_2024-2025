import logging
from dataclasses import dataclass
from typing import Dict, List
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ParserStats:
    name: str
    start_time: float
    end_time: float
    tasks_parsed: int
    errors: List[str]

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

class SummaryLogger:
    def __init__(self):
        self.stats: Dict[str, ParserStats] = {}
        self.total_tasks = 0
        self.total_errors = 0
        self.start_time = time.time()

    def add_parser_stats(self, name: str, start_time: float, end_time: float, tasks_parsed: int, errors: List[str]):
        self.stats[name] = ParserStats(name, start_time, end_time, tasks_parsed, errors)
        self.total_tasks += tasks_parsed
        self.total_errors += len(errors)

    def print_summary(self):
        logger.info("\n=== PARSING SUMMARY ===")
        logger.info(f"Total time: {time.time() - self.start_time:.2f} seconds")
        logger.info(f"Total tasks parsed: {self.total_tasks}")
        logger.info(f"Total errors: {self.total_errors}")
        
        logger.info("\n=== PARSER DETAILS ===")
        for stats in self.stats.values():
            logger.info(f"\nParser: {stats.name}")
            logger.info(f"Duration: {stats.duration:.2f} seconds")
            logger.info(f"Tasks parsed: {stats.tasks_parsed}")
            if stats.errors:
                logger.info("Errors encountered:")
                for error in stats.errors:
                    logger.info(f"  - {error}")
            logger.info(f"Average speed: {stats.tasks_parsed / stats.duration:.2f} tasks/second")

# Global summary logger instance
summary_logger = SummaryLogger() 