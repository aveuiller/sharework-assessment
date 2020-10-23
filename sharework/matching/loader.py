"""
This module defines the ways of loading data.
"""
import logging
import os
import sqlite3
from abc import ABC
from csv import DictReader
from logging import config
from typing import Generator

from sharework import RESOURCES_DIR
from sharework.matching.model import Company

config.fileConfig(os.path.join(RESOURCES_DIR, "logging.config"))
logger = logging.getLogger(__name__)


class DataLoader(ABC):

    def load(self) -> Generator[Company, None, None]:
        """Load all data from the source as a generator of Companies.

        :return: A Generator of Company to consume.
        """
        raise NotImplementedError


class CSVDataLoader(DataLoader):
    FIELDS = [
        "source_id", "name", "website", "email",
        "phone", "address", "postal_code", "city", "country"
    ]

    def __init__(self, path: str, shorten=True) -> None:
        """Load all companies from the given CSV file.

        :param path: Path to the file.
        :param shorten: Shorten the source name to the last element
        in the path.
        """
        super().__init__()
        self.path = path
        self.shorten = shorten

    def load(self) -> Generator[Company, None, None]:
        with open(self.path, 'r') as file:
            reader = DictReader(file, fieldnames=self.FIELDS)
            for line in reader:
                source = self.path
                if self.shorten:
                    source = source.split(os.path.sep)[-1]

                line.update({"source_name": source})
                yield Company(**line)


class SQLiteDataLoader(DataLoader):
    def __init__(self, db_path: str, source_name: str) -> None:
        """Load all data from a SQLite database,
        with the source matching the given name.

        :param db_path: Path of the sqlite file.
        :param source_name: Name of the source to query.
        """
        super().__init__()
        self.db_path = db_path
        self.source_name = source_name

    def load(self) -> Generator[Company, None, None]:
        sql = "SELECT * FROM companies WHERE source_name = ?"
        result = self.new_connection().execute(sql, (self.source_name,))

        for row in result:
            # Skip id on the Company constructor.
            # This works because the constructor has the same order as the
            # table. this is quite a weak binding and may be better with a
            # strong naming in the retrieved values.
            yield Company(*row[1:])

    def new_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
