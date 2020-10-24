import os
import sqlite3
import unittest
from datetime import datetime

from sharework.backend.models import Base, Company, Match
from tests import RESOURCES_DIR


class ModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        timestamp = datetime.now().timestamp()
        self.db_file = f"/tmp/test_sharework_{timestamp}.sqlite"
        # Prepend protocol for sqlalchemy
        self.db_path = f"sqlite:///{self.db_file}"

        self.connection = sqlite3.connect(self.db_file)
        init_path = os.path.join(RESOURCES_DIR, "backend", "init_test_db.sql")
        with open(init_path, "r") as sql:
            self.connection.executescript(sql.read())
            self.connection.commit()
        self.connection.close()

    def tearDown(self) -> None:
        super().tearDown()
        os.remove(self.db_file)


class CompanyTestCase(ModelTestCase):

    def setUp(self) -> None:
        super().setUp()
        Company.SQL_ENGINE = None
        self.session = Company.get_sql_session(self.db_path)
        self.company_1 = Company(source_id=1, source_name="testA", name="A")
        self.company_2 = Company(source_id=2, source_name="testB", name="B")

        self.session.add(self.company_1)
        self.session.add(self.company_2)
        self.session.commit()

    def tearDown(self) -> None:
        super().tearDown()
        self.session.close()

    def test_fetch_all_company(self):
        companies = Company.fetch_all(self.session, 5, 0)

        self.assertEqual(2, len(companies))

    def test_fetch_one_company(self):
        returned = Company.fetch_one(self.session, 1)

        self.assertEqual(self.company_1.name, returned.name)

    def test_fetch_one_not_found(self):
        returned = Company.fetch_one(self.session, 3)

        self.assertIsNone(returned)


class MatchTestCase(ModelTestCase):

    def setUp(self) -> None:
        super().setUp()
        Company.SQL_ENGINE = None
        self.session = Company.get_sql_session(self.db_path)
        self.company_1 = Company(source_id=1, source_name="testA", name="A")
        self.company_2 = Company(source_id=2, source_name="testB", name="B")

        self.session.add(self.company_1)
        self.session.add(self.company_2)

        self.match = Match(id=1,
                           left_company=self.company_1,
                           right_company=self.company_2)
        self.session.add(self.match)
        self.session.commit()

    def tearDown(self) -> None:
        super().tearDown()
        self.session.close()

    def test_fetch_one_match(self):
        returned = Match.fetch_one(self.session, 1)

        self.assertIsNotNone(returned)
        self.assertEqual(self.match.id, returned.id)
        self.assertEqual(self.match.left_company_id, returned.left_company_id)
        self.assertEqual(self.match.right_company_id,
                         returned.right_company_id)

    def test_fetch_one_not_found(self):
        returned = Match.fetch_one(self.session, 3)

        self.assertIsNone(returned)

    def test_delete(self):
        self.match.delete(self.session)
        self.session.commit()

        self.assertIsNone(Match.fetch_one(self.session, self.match.id))
