import unittest
from unittest.mock import patch

from sharework.backend import init_flask_api
from sharework.backend.models import Company, Match


class CompanyViewsTestCase(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.app = init_flask_api().test_client()
        self.company_1 = Company(
            id=1,
            source_id=1,
            source_name="dataset_A",
        )
        self.company_2 = Company(
            id=2,
            source_id=2,
            source_name="dataset_A",
        )

    def tearDown(self) -> None:
        super().tearDown()

    @patch('sharework.backend.models.Company.fetch_all')
    def test_index(self, fetch_all_mock):
        fetch_all_mock.return_value = [self.company_1, self.company_2]
        response = self.app.get(
            '/company',
            headers={"Content-Type": "application/json"},
        )

        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertEqual(json[0]['id'], self.company_1.id)
        self.assertEqual(json[1]['id'], self.company_2.id)

    @patch('sharework.backend.models.Company.fetch_one')
    def test_get_one(self, fetch_one_mock):
        fetch_one_mock.return_value = self.company_1
        response = self.app.get(
            '/company/1',
            headers={"Content-Type": "application/json"},
        )

        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertEqual(json['id'], self.company_1.id)

    @patch('sharework.backend.models.Company.fetch_one')
    def test_get_none(self, fetch_one_mock):
        fetch_one_mock.return_value = None
        response = self.app.get(
            '/company/1',
            headers={"Content-Type": "application/json"},
        )

        self.assertEqual(404, response.status_code)


class MatchViewsTestCase(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.app = init_flask_api().test_client()
        self.company_1 = Company(
            id=1,
            source_id=1,
            source_name="dataset_A",
        )
        self.company_2 = Company(
            id=2,
            source_id=2,
            source_name="dataset_A",
        )

        self.match = Match(
            id=1,
            left_company_id=self.company_1.id,
            right_company_id=self.company_2.id,
        )

    def tearDown(self) -> None:
        super().tearDown()

    @patch('sharework.backend.models.Match.fetch_one')
    def test_get_one(self, fetch_one_mock):
        fetch_one_mock.return_value = self.match
        response = self.app.get(
            '/match/1',
            headers={"Content-Type": "application/json"},
        )

        self.assertEqual(200, response.status_code)
        json = response.json
        self.assertEqual(json['id'], self.company_1.id)

    @patch('sharework.backend.models.Match.fetch_one')
    def test_get_none(self, fetch_one_mock):
        fetch_one_mock.return_value = None
        response = self.app.get(
            '/match/1',
            headers={"Content-Type": "application/json"},
        )

        self.assertEqual(404, response.status_code)

    @patch('sharework.backend.models.Match.fetch_one')
    def test_delete_one(self, fetch_one_mock):
        fetch_one_mock.return_value = None
        response = self.app.delete(
            '/match/1',
            headers={"Content-Type": "application/json"},
        )

        self.assertEqual(404, response.status_code)

    @patch('sharework.backend.models.Match.fetch_one')
    @patch('sharework.backend.models.Match.delete')
    def test_delete_none(self, fetch_one_mock, delete_mock):
        fetch_one_mock.return_value = self.match
        response = self.app.delete(
            '/match/1',
            headers={"Content-Type": "application/json"},
        )

        self.assertEqual(200, response.status_code)
        delete_mock.assert_called_once()
