"""
This module defines the matcher algorithm and imports all needed criterion.

# TODO: We may want to have an external criterion config. with weight.
"""
import logging
import os
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from logging import config
from typing import Generator, List

from sharework import RESOURCES_DIR
from sharework.matching.criterion import (
    AddressCriterion, CompanyCriterion,
    DomainNameCriterion, FieldCriterion, NameContainedCriterion, PhoneCriterion
)
from sharework.matching.loader import DataLoader
from sharework.matching.model import Company, CompanyMatch

config.fileConfig(os.path.join(RESOURCES_DIR, "logging.config"))
logger = logging.getLogger(__name__)


class CompanyMatcher:
    DEFAULT_CRITERIA = [
        DomainNameCriterion(5),
        FieldCriterion("name", 3),
        AddressCriterion(3),
        PhoneCriterion(3),
        NameContainedCriterion(1),
    ]

    def __init__(self, criteria: List[CompanyCriterion] = None) -> None:
        """Define the percentage of match between two companies"""
        super().__init__()
        if not criteria:
            criteria = self.DEFAULT_CRITERIA
        self.criteria = criteria

    def match(self, one: Company, two: Company) -> CompanyMatch:
        """Compute if two company seems to be the same

        :param one: The first company to match.
        :param two: The second company to match.
        :return: The rate of matching between two companies from 0 to 1.
        """
        logger.info(f"Comparing {one.name} with {two.name}")

        total_weight = 0
        current_score = 0
        successes = []
        for criterion in self.criteria:
            match = criterion.match(one, two)
            # We take the criterion into account
            # if the comparison could actually be done.
            if match is not None:
                total_weight += criterion.weight

            if match:
                current_score += criterion.weight
                successes.append(criterion.__class__.__name__)

        return CompanyMatch(one, two, current_score / total_weight, successes)


class SourcesMatcher:
    def __init__(self,
                 source_a: DataLoader,
                 source_b: DataLoader,
                 matcher: CompanyMatcher = None,
                 worker_amount: int = 20) -> None:
        """
        Create matches between two companies data sources

        ..attr THRESHOLD:
            Percentage of identity from which two companies can be
            considered equals.

        :param source_a: A generator of companies from the first data source
        :param source_b: A generator of companies from the second data source
        """
        super().__init__()
        self.source_a = source_a
        self.source_b = source_b
        self.pool = ThreadPoolExecutor(max_workers=worker_amount)
        self.matcher = CompanyMatcher() if matcher is None else matcher

    def compare(self) -> Generator[Future, None, None]:
        """Compare all data sources and returns the result as a list of
        futures CompanyMatch.

        :return: A Generator containing Futures of CompanyMatch
        """
        for company_a in self.source_a.load():
            for company_b in self.source_b.load():
                yield self.pool.submit(self.matcher.match,
                                       company_a, company_b)

    def stop(self):
        """Stop the matcher and all associated operations."""
        self.pool.shutdown()
