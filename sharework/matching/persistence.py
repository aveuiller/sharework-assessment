"""
This module defines the ways of persisting data.
"""
import logging
import os
import sqlite3
from abc import ABC
from csv import DictWriter
from typing import List

from sharework import RESOURCES_DIR
from sharework.matching.model import CompanyMatch

logger = logging.getLogger()


class DataDumper(ABC):
    def add(self, data: CompanyMatch) -> None:
        """Add the CompanyMatch to the persistence.

        :param data: The CompanyMatch to add.
        """
        raise NotImplementedError

    def add_all(self, data: List[CompanyMatch]) -> None:
        """Add the List of CompanyMatch to the persistence.

        :param data: The list of CompanyMatch to add.
        """
        raise NotImplementedError

    def flush(self) -> None:
        """Persist and commit all data contained in the persistence.
        """
        raise NotImplementedError


class CSVDataDumper(DataDumper):
    FIELDS = [
        "company_a_source", "company_a_id",
        "company_b_source", "company_b_id",
        "score", "criteria"
    ]

    def __init__(self, path: str) -> None:
        """Create a new output CSV to contain all matches.

        :param path: Path to the CSV file to generate.
        """
        super().__init__()
        self.output_path = path
        self.lines = []
        self._init_headers()

    def add(self, data: CompanyMatch) -> None:
        self.lines.append({
            "company_a_source": data.company_a.source_name,
            "company_a_id": data.company_a.source_id,
            "company_b_source": data.company_b.source_name,
            "company_b_id": data.company_b.source_id,
            "score": data.score,
            "criteria": ';'.join(data.success_criteria),
        })
        # Avoid keeping an array growing too much in this class.
        # This is a tradeoff between too much IOs and too much memory usage.
        if len(self.lines) > 500:
            logger.info("Flushing current lines...")
            self.flush()

    def add_all(self, data: List[CompanyMatch]) -> None:
        map(self.add, data)

    def flush(self) -> None:
        self.__exec_in_writer(lambda writer: writer.writerows(self.lines))
        self.lines.clear()

    def _init_headers(self) -> None:
        """Add the headers to the output file, automatically called."""
        self.__exec_in_writer(lambda writer: writer.writeheader())

    def __exec_in_writer(self, operation) -> None:
        with open(self.output_path, "a") as output_file:
            writer = DictWriter(output_file, fieldnames=self.FIELDS)
            operation(writer)


class SqliteDataDumper(DataDumper):

    def __init__(self, db_path: str) -> None:
        """Create a new output SQLite to contain all matches.

        :param db_path: Path to the sqlite database to use.
        """
        super().__init__()
        self.db_path = db_path
        self._init_db()
        self.lines = []

    def _init_db(self) -> None:
        """Creates the requires db schema"""
        path = os.path.join(RESOURCES_DIR, "sql", "0_init_matches_table.sql")
        with self.new_connection() as connection:
            with open(path, "r") as script:
                content = script.read()
                connection.executescript(content)
            connection.commit()

    def add(self, data: CompanyMatch) -> None:
        # Not the best way of persisting the criteria, we could have a
        # separate table for that.
        self.lines.append((
            data.company_a.source_name, data.company_a.source_id,
            data.company_b.source_name, data.company_b.source_id,
            data.score, ';'.join(data.success_criteria)
        ))
        if len(self.lines) > 500:
            self.flush()

    def add_all(self, data: List[CompanyMatch]) -> None:
        map(self.add, data)

    def flush(self) -> None:
        sql = """INSERT INTO matches (
            company_a_source, company_a_id,
            company_b_source, company_b_id,
            score, success_criteria
        ) VALUES (?, ?, ?, ?, ?, ?)"""

        with self.new_connection() as connection:
            connection.executemany(sql, self.lines)
            connection.commit()
        self.lines.clear()

    def new_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)
