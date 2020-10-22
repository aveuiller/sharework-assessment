import logging
import os
from logging import config

from sharework import DATA_DIR, RESOURCES_DIR
from sharework.matching.loader import CSVDataLoader
from sharework.matching.matcher import SourcesMatcher
from sharework.matching.persistence import CSVDataDumper

config.fileConfig(os.path.join(RESOURCES_DIR, "logging.config"))
logger = logging.getLogger(__name__)


def main():
    # TODO: Add args to control data loading, threshold and timeout.
    # TODO: Add args to control computing threshold and timeout.
    # TODO: Add args to control data persistence.
    timeout_seconds = 60
    threshold = 0.7
    source_a = CSVDataLoader(os.path.join(DATA_DIR, "dataset_A.csv"))
    source_b = CSVDataLoader(os.path.join(DATA_DIR, "dataset_B.csv"))
    comparator = SourcesMatcher(source_a, source_b)
    dumper = CSVDataDumper(os.path.join(DATA_DIR, "out.csv"))

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
                            f"and {match.company_b.name}")
                dumper.add(match)

    dumper.flush()

    comparator.stop()
    logger.info("Matching done.")


if __name__ == '__main__':
    main()
