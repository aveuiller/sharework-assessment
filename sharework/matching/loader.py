"""
This module defines the ways of loading data.
"""
from abc import ABC
from csv import DictReader
from typing import Generator

from sharework.matching.model import Company


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

    def __init__(self, path: str) -> None:
        """Load all companies from the given CSV file.

        :param path: Path to the file.
        """
        super().__init__()
        self.path = path

    def load(self) -> Generator[Company, None, None]:
        with open(self.path, 'r') as file:
            reader = DictReader(file, fieldnames=self.FIELDS)
            for line in reader:
                line.update({"source_name": self.path})
                yield Company(**line)


class SQLiteDataLoader(DataLoader):
    def __init__(self, db_path: str, source_name: str) -> None:
        """Load all data from a SQLite database,
        with the source matching the given name.

        TODO: Implement me

        :param db_path: Path of the sqlite file.
        :param source_name: Name of the source to query.
        """
        super().__init__()
        self.db_path = db_path

    def load(self) -> Generator[Company, None, None]:
        pass
