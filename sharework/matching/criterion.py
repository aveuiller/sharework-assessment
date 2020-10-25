"""
This module defines all available criteria for the company matcher.

This criterion library may grow to a package one day.

Potential future criteria:
    - Search the name within a hamming distance as criterion.
    - Search the email domain part, while excluding all well-known email
    providers. Not implemented since we have no email in the database.
"""

import logging
from abc import ABC
from typing import Optional

import phonenumbers
import pycountry

from sharework.matching.model import Company

logger = logging.getLogger()


class CompanyCriterion(ABC):
    def __init__(self, weight: int) -> None:
        """Generic Criterion class defining contract.

        :param weight: The weight to apply on the criterion.
        """
        super().__init__()
        self.weight = weight

    def match(self, one: Company, two: Company) -> Optional[bool]:
        """Compute if the two given companies are matching given the current
        criterion.

        :param one: The first company to match.
        :param two: The second company to match.
        :return: True if both companies matches for the criterion,
        False otherwise.
        """
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError


class FieldCriterion(CompanyCriterion):
    def __init__(self, field: str, weight: int) -> None:
        """Compare the value of two attributes of a company.

        :param field: The field that should be retrieved on the company.
        :param weight: The weight to apply on the criterion.
        """
        super().__init__(weight)
        self.field = field

    def _normalize(self, field) -> str:
        """Apply transformations on the field to retrieve a uniformized data.

        :param input: The input to normalize.
        :return: The normalized input.
        Cast to lowercase stripped string by default.
        """
        return str(field).lower().strip()

    def _extract_field(self, company: Company) -> str:
        """Extracts the field, asserts its existence, and normalize it.

        :param company: The company from which the field should be extracted.
        :return: The normalized field if existing
        :raises AttributeError: if the field is None or an empty string.
        """
        field = getattr(company, self.field)
        if field is None or not str(field):
            raise AttributeError
        return self._normalize(field)

    def match(self, one: Company, two: Company) -> Optional[bool]:
        """Retrieve the fields and compare them to match the two companies.
        If the given fields does not exist, return None.

        :param one: The first company to match.
        :param two: The second company to match.
        :return: True if both companies matches for the criterion,
        False otherwise.
        """
        try:
            fields = [self._extract_field(company) for company in (one, two)]
        except AttributeError:
            logger.debug(f"Unavailable attribute {self.field}")
            return None
        else:
            return self._compare(*fields)

    def _compare(self, field_one: str, field_two: str) -> bool:
        """Compare the two fields to check if the companies are matching for
        the current criterion.

        :param field_one: First field to compare.
        :param field_two: Second field to compare.
        :return: True if matching, False otherwise. Check equality by default.
        """
        return field_one == field_two

    @property
    def name(self) -> str:
        return f"{self.__class__.__name__}:{self.field}"


class NameContainedCriterion(FieldCriterion):
    def __init__(self, weight: int = 1) -> None:
        """This criterion is a match if we can find the whole name of
         one company in another."""
        super().__init__("name", weight)

    def _compare(self, field_one: str, field_two: str) -> bool:
        return field_one in field_two or field_two in field_one

    @property
    def name(self) -> str:
        return self.__class__.__name__


class PostalCodeCriterion(FieldCriterion):
    def __init__(self, weight: int = 1) -> None:
        """This criterion compares two postal codes identity."""
        super().__init__("postal_code", weight)

    def _normalize(self, field) -> str:
        return super()._normalize(field).replace('.0', '')

    @property
    def name(self) -> str:
        return self.__class__.__name__


class AddressCriterion(CompanyCriterion):
    def __init__(self, weight: int = 3) -> None:
        """This criterion is a match if the complete Address is matching
        between the two companies.
        """
        super().__init__(weight)
        self.criteria = [
            # TODO: We maybe could be more open on the address syntax
            FieldCriterion("address", 1),
            PostalCodeCriterion(),
            FieldCriterion("city", 1),
            FieldCriterion("country", 1),
        ]

    def match(self, one: Company, two: Company) -> Optional[bool]:
        for criterion in self.criteria:
            match = criterion.match(one, two)
            if not match:
                # Either False or None gets returned as-is since
                # we won't have enough data to be certain.
                return match
        return True

    @property
    def name(self) -> str:
        return self.__class__.__name__


class PhoneCriterion(FieldCriterion):
    def __init__(self, weight: int = 3) -> None:
        """This criterion is a match if the complete Address is matching
        between the two companies.
        """
        super().__init__("phone", weight)

    def _normalize(self, field, country: str = None) -> str:
        """Parse the number and output it as an international number.
        We try to parse the number in two times to avoid misleading the library
        in case of a phone number not from the same country as the company HQ.

        :param field: The phone number to normalize.
        :param country: The company HQ country.
        :return: The normalized phone number if parsing successful.
        :raise AttributeError: If we can't parse the phone number correctly.
        """
        try:
            number = phonenumbers.parse(field, None)
        except phonenumbers.phonenumberutil.NumberParseException:
            logger.debug(f"Unable to parse phone {field} without country")
            try:
                country = country.capitalize()
                iso2 = pycountry.countries.get(name=country).alpha_2
                number = phonenumbers.parse(field, iso2)
            except (phonenumbers.phonenumberutil.NumberParseException,
                    KeyError):
                logger.debug(f"Unable to parse phone {field} "
                             f"with country {country}")
                raise AttributeError
        return phonenumbers.format_number(number,
                                          phonenumbers.PhoneNumberFormat.E164)

    def _extract_field(self, company: Company) -> str:
        field = getattr(company, self.field)
        if field is None or not str(field):
            raise AttributeError
        return self._normalize(field, company.country)

    @property
    def name(self) -> str:
        return self.__class__.__name__


class DomainNameCriterion(FieldCriterion):
    def __init__(self, weight: int = 5) -> None:
        """This criterion compares the root domain name of two websites."""
        super().__init__("website", weight)

    def _normalize(self, field) -> str:
        normalized = super()._normalize(field)
        protocol_index = normalized.find("//")
        if protocol_index > -1:
            normalized = normalized[protocol_index + 2:]
        domain = normalized.split('/')[0]
        root_domain = '.'.join(domain.split(".")[-2:])
        return root_domain

    @property
    def name(self) -> str:
        return self.__class__.__name__
