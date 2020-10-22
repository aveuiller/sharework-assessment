import unittest
from typing import Optional
from unittest.mock import Mock

from sharework.matching.criterion import CompanyCriterion
from sharework.matching.loader import DataLoader
from sharework.matching.matcher import CompanyMatcher, SourcesMatcher
from sharework.matching.model import Company


class SuccessCriterion(CompanyCriterion):

    def match(self, one: Company, two: Company) -> Optional[bool]:
        return True


class FailureCriterion(CompanyCriterion):

    def match(self, one: Company, two: Company) -> Optional[bool]:
        return False


class UnsureCriterion(CompanyCriterion):

    def match(self, one: Company, two: Company) -> Optional[bool]:
        return None


class CompanyMatcherTestCase(unittest.TestCase):
    def test_matcher_percentage(self):
        matcher = CompanyMatcher(criteria=[
            SuccessCriterion(5),
            FailureCriterion(5),
            UnsureCriterion(50),
            UnsureCriterion(50),
            UnsureCriterion(50),
            UnsureCriterion(50),
            UnsureCriterion(1),
            UnsureCriterion(10),
        ])
        one = Mock(spec=Company)
        one.name = '1'
        two = Mock(spec=Company)
        two.name = '2'
        match = matcher.match(one, two)
        self.assertEqual(0.5, match.score)
        self.assertEqual(one, match.company_a)
        self.assertEqual(two, match.company_b)
        self.assertEqual([SuccessCriterion.__name__],
                         match.success_criteria)


class SourcesMatcherTestCase(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.company_1 = Mock(spec=Company)
        self.company_1.name = '1'
        self.company_2 = Mock(spec=Company)
        self.company_2.name = '2'
        self.company_3 = Mock(spec=Company)
        self.company_3.name = '3'
        self.company_4 = Mock(spec=Company)
        self.company_4.name = '4'
        self.company_5 = Mock(spec=Company)
        self.company_5.name = '5'
        self.success_matcher = CompanyMatcher([SuccessCriterion(1)])

    def test_cartesian_product(self):
        source_a = Mock(spec=DataLoader())
        source_a.load.return_value = (self.company_1, self.company_2)
        source_b = Mock(spec=DataLoader())
        source_b.load.return_value = (self.company_3,
                                      self.company_4,
                                      self.company_5)

        matcher = SourcesMatcher(source_a, source_b,
                                 matcher=self.success_matcher)

        result = matcher.compare()

        expected_matching = [
            (self.company_1, self.company_3),
            (self.company_1, self.company_4),
            (self.company_1, self.company_5),
            (self.company_2, self.company_3),
            (self.company_2, self.company_4),
            (self.company_2, self.company_5),
        ]

        for match, expected in zip(result, expected_matching):
            result = match.result()
            self.assertIsNotNone(result)
            self.assertEqual(expected[0], result.company_a)
            self.assertEqual(expected[1], result.company_b)
            self.assertEqual(1.0, result.score)
            self.assertEqual([SuccessCriterion.__name__],
                             result.success_criteria)
