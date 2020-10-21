"""
This module defines the matcher algorithm and imports all needed criterion.

# TODO: We may want to have an external criterion config. with weight.
"""
from typing import List

from sharework.matching.criterion import (
    AddressCriterion, CompanyCriterion,
    DomainNameCriterion, FieldCriterion, NameContainedCriterion, PhoneCriterion
)
from sharework.matching.persistence import Company


class CompanyMatcher:
    DEFAULT_CRITERIA = [
        DomainNameCriterion(5),
        FieldCriterion("name", 3),
        AddressCriterion(3),
        PhoneCriterion(3),
        NameContainedCriterion(1),
    ]

    def __init__(self, criteria: List[CompanyCriterion] = None) -> None:
        super().__init__()
        if not criteria:
            criteria = self.DEFAULT_CRITERIA
        self.criteria = criteria

    def match(self, one: Company, two: Company) -> float:
        """Compute if two company seems to be the same

        :param one: The first company to match.
        :param two: The second company to match.
        :return: The rate of matching between two companies from 0 to 1.
        """
        total_weight = 0
        current_score = 0
        for criterion in self.criteria:
            match = criterion.match(one, two)
            # We take the criterion into account
            # if the comparison could actually be done.
            if match is not None:
                total_weight += criterion.weight

            if match:
                current_score += criterion.weight

        return current_score / total_weight
