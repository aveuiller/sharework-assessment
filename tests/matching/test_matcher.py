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

    @property
    def name(self):
        return self.__class__.__name__


class FailureCriterion(CompanyCriterion):

    def match(self, one: Company, two: Company) -> Optional[bool]:
        return False

    @property
    def name(self):
        return self.__class__.__name__


class UnsureCriterion(CompanyCriterion):

    def match(self, one: Company, two: Company) -> Optional[bool]:
        return None

    @property
    def name(self):
        return self.__class__.__name__


class CompanyMatcherTestCase(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.one = Mock(spec=Company)
        self.one.name = '1'
        self.two = Mock(spec=Company)
        self.two.name = '2'

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
        ], strict=False)

        match = matcher.match(self.one, self.two)

        self.assertEqual(0.5, match.score)
        self.assertEqual(self.one, match.company_a)
        self.assertEqual(self.two, match.company_b)
        self.assertEqual([SuccessCriterion.__name__],
                         match.success_criteria)

    def test_matcher_percentage_strict(self):
        matcher = CompanyMatcher(criteria=[
            SuccessCriterion(5),
            UnsureCriterion(5),
        ], strict=True)

        match = matcher.match(self.one, self.two)

        self.assertEqual(0.5, match.score)
        self.assertEqual(self.one, match.company_a)
        self.assertEqual(self.two, match.company_b)
        self.assertEqual([SuccessCriterion.__name__],
                         match.success_criteria)

    def test_matcher_percentage_success_not_strict(self):
        matcher = CompanyMatcher(criteria=[
            SuccessCriterion(5),
            UnsureCriterion(5),
        ], strict=False)

        match = matcher.match(self.one, self.two)
        self.assertEqual(1.0, match.score)
        self.assertEqual(self.one, match.company_a)
        self.assertEqual(self.two, match.company_b)
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
