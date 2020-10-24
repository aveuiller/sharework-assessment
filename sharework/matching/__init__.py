import logging
import os
from logging import config
from typing import Tuple

from sharework import DATA_DIR, RESOURCES_DIR
from sharework.matching.loader import (
    CSVDataLoader, DataLoader,
    SQLiteDataLoader
)
from sharework.matching.matcher import SourcesMatcher
from sharework.matching.persistence import CSVDataDumper, SqliteDataDumper

config.fileConfig(os.path.join(RESOURCES_DIR, "logging.config"))
logger = logging.getLogger()


def main():
    # TODO: Add args to control data loading.
    # TODO: Add args to control computing threshold and timeout.
    # TODO: Add args to control comparison strictness and workers.
    # TODO: Add args to control data persistence.
    timeout_seconds = 60
    threshold = 0.7

    # Use CSV
    # source_a, source_b = _csv_loaders()
    # dumper = CSVDataDumper(os.path.join(DATA_DIR, "out.csv"))

    # Use SQLite
    source_a, source_b = _sqlite_loaders()
    dumper = SqliteDataDumper(os.path.join(DATA_DIR, "matching_base.sqlite3"))

    comparator = SourcesMatcher(source_a, source_b, worker_amount=5)
    comparator.matcher.strict = True
    logger.info("Starting datasource comparison")
    for future in comparator.compare():
        try:
            match = future.result(timeout=timeout_seconds)
        except TimeoutError:
            logger.error("We have some performance issues on comparison")
        else:
            if match.score >= threshold:
                logger.info(f"We have a match "
                            f"between {match.company_a.name} "
                            f"and {match.company_b.name} ({match.score})")
                dumper.add(match)

    dumper.flush()

    comparator.stop()
    logger.info("Matching done.")


def _sqlite_loaders() -> Tuple[DataLoader, DataLoader]:
    db_path = os.path.join(DATA_DIR, "matching_base.sqlite3")
    source_a = SQLiteDataLoader(db_path, "dataset_A.csv")
    source_b = SQLiteDataLoader(db_path, "dataset_B.csv")
    return source_a, source_b


def _csv_loaders() -> Tuple[DataLoader, DataLoader]:
    source_a = CSVDataLoader(os.path.join(DATA_DIR, "dataset_A.csv"))
    source_b = CSVDataLoader(os.path.join(DATA_DIR, "dataset_B.csv"))
    return source_a, source_b


if __name__ == '__main__':
    main()
