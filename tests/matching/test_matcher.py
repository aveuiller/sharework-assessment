import unittest
from typing import Optional
from unittest.mock import Mock

from sharework.matching.criterion import CompanyCriterion
from sharework.matching.matcher import CompanyMatcher
from sharework.matching.persistence import Company


class SuccessCriterion(CompanyCriterion):

    def match(self, one: Company, two: Company) -> Optional[bool]:
        return True


class FailureCriterion(CompanyCriterion):

    def match(self, one: Company, two: Company) -> Optional[bool]:
        return False


class UnsureCriterion(CompanyCriterion):

    def match(self, one: Company, two: Company) -> Optional[bool]:
        return None


class MatcherTestCase(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()

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
        self.assertEqual(0.5, matcher.match(Mock(), Mock()))
