"""
This module defines the matcher algorithm and imports all needed criterion.

# TODO: We may want to have an external criterion config. with weight.
"""
import logging
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Generator, List

from sharework.matching.criterion import (
    AddressCriterion, CompanyCriterion,
    DomainNameCriterion, FieldCriterion, NameContainedCriterion, PhoneCriterion
)
from sharework.matching.loader import DataLoader
from sharework.matching.model import Company, CompanyMatch

logger = logging.getLogger()


class CompanyMatcher:
    DEFAULT_CRITERIA = [
        DomainNameCriterion(5),
        FieldCriterion("name", 5),
        AddressCriterion(3),
        PhoneCriterion(3),
        NameContainedCriterion(1),
    ]

    def __init__(self, criteria: List[CompanyCriterion] = None,
                 strict: bool = True) -> None:
        """Define the percentage of match between two companies

        :param criteria: The list of criterion to use on matching.
        :param strict: We want a strict match on all fields. If True,
        the weight of criterion with missing data is still added to the total
        weight, thus making it harder to match companies when missing data.
        """
        super().__init__()
        if not criteria:
            criteria = self.DEFAULT_CRITERIA
        self.criteria = criteria
        self.strict = strict

    def match(self, one: Company, two: Company) -> CompanyMatch:
        """Compute if two company seems to be the same

        :param one: The first company to match.
        :param two: The second company to match.
        :return: The rate of matching between two companies from 0 to 1.
        """
        logger.debug(f"Comparing {one.name} with {two.name}")

        total_weight = 0
        current_score = 0
        successes = []
        for criterion in self.criteria:
            match = criterion.match(one, two)
            if self.strict or match is not None:
                total_weight += criterion.weight

            if match:
                current_score += criterion.weight
                successes.append(criterion.name)

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
