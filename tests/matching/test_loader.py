import os
import unittest

from sharework.matching import CSVDataLoader
from sharework.matching.loader import SQLiteDataLoader
from sharework.matching.model import Company
from tests import RESOURCES_DIR


class CSVLoaderTestCase(unittest.TestCase):
    def test_loaded(self):
        loader = CSVDataLoader(os.path.join(RESOURCES_DIR, "dataset.csv"))
        expected_1 = Company(
            source_id='1',
            source_name="dataset.csv",
            name="A",
            website="url.com",
            email="a@b.com",
            phone="+33123456789",
            address="1 rue de l'allée",
            postal_code="75015.0",
            city="Paris",
            country="France"
        )
        expected_2 = Company(
            source_id='2',
            source_name="dataset.csv",
            name="B",
            website="",
            email="",
            phone="",
            address="",
            postal_code="33000.0",
            city="",
            country="France"
        )

        self.assertEqual([expected_1, expected_2], list(loader.load()))


class SQLiteLoaderTestCase(unittest.TestCase):
    def test_loaded(self):
        path = os.path.join(RESOURCES_DIR, "dataset.sqlite")
        loader = SQLiteDataLoader(path, "dataset.csv")
        expected_1 = Company(
            source_id=1,
            source_name="dataset.csv",
            name="A",
            website="url.com",
            email="a@b.com",
            phone="+33123456789",
            address="1 rue de l'allée",
            postal_code="75015.0",
            city="Paris",
            country="France"
        )
        expected_2 = Company(
            source_id=2,
            source_name="dataset.csv",
            name="B",
            website="",
            email="",
            phone="",
            address="",
            postal_code="33000.0",
            city="",
            country="France"
        )

        self.assertEqual([expected_1, expected_2], list(loader.load()))
