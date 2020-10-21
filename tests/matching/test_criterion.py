import unittest

from sharework.matching.criterion import (
    AddressCriterion, DomainNameCriterion, FieldCriterion,
    NameContainedCriterion,
    PhoneCriterion
)
from sharework.matching.persistence import Company


class CriterionTestCase(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.company1 = Company(
            source_id=1,
            source_name="source",
            name="name",
            website="None",
            email="a@b.com",
            phone="+33123456789",
            address="",
            postal_code="",
            city="",
            country=""
        )
        self.company2 = Company(
            source_id=1,
            source_name="source",
            name="name",
            website="None",
            email="a@b.com",
            phone="0123456789",
            address="any",
            postal_code="",
            city="",
            country=""
        )


class FieldCriterionTestCase(CriterionTestCase):
    def test_attribute_not_existing(self):
        criterion = FieldCriterion("any", 1)
        self.assertIsNone(criterion.match(self.company1, self.company2))

    def test_both_attribute_empty(self):
        criterion = FieldCriterion("city", 1)
        self.assertIsNone(criterion.match(self.company1, self.company2))

    def test_one_attribute_empty(self):
        criterion = FieldCriterion("address", 1)
        self.assertIsNone(criterion.match(self.company1, self.company2))

    def test_attribute_equal(self):
        criterion = FieldCriterion("name", 1)
        self.assertTrue(criterion.match(self.company1, self.company2))


class NameContainedCriterionTestCase(CriterionTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.criterion = NameContainedCriterion()

    def test_name_contained(self):
        self.company1.name = "MyCompany Inc."
        self.company2.name = "mycompany"
        self.assertTrue(self.criterion.match(self.company1, self.company2))

    def test_same_names(self):
        self.assertTrue(self.criterion.match(self.company1, self.company2))

    def test_different_names(self):
        self.company1.name = "Any"

        match = self.criterion.match(self.company1, self.company2)
        self.assertIsNotNone(match)
        self.assertFalse(match)


class PhoneCriterionTestCase(CriterionTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.criterion = PhoneCriterion()

    def test_phone_matches(self):
        self.company1.phone = "+33 4 56 78 90 12"
        self.company1.country = "France"
        self.company2.phone = "0456789012"
        self.company2.country = "France"

        self.assertTrue(self.criterion.match(self.company1, self.company2))

    def test_different_phone_countries(self):
        self.company1.phone = "+33 4 56 78 90 12"
        self.company2.phone = "+342456789012"

        match = self.criterion.match(self.company1, self.company2)
        self.assertIsNotNone(match)
        self.assertFalse(match)

    def test_different_phones(self):
        self.company1.phone = "+33 4 56 78 90 12"
        self.company2.country = "France"

        match = self.criterion.match(self.company1, self.company2)
        self.assertIsNotNone(match)
        self.assertFalse(match)


class AddressCriterionTestCase(CriterionTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.criterion = AddressCriterion()

    def test_address_field_missing(self):
        self.company1.address = "1"
        self.company1.postal_code = "12345"
        self.company1.city = "Paris"
        self.company1.country = "france"

        self.company2.address = "1"
        self.company2.postal_code = "12345"
        self.company2.city = "Paris"

        self.company2.country = ""
        self.assertIsNone(self.criterion.match(self.company1, self.company2))

        self.company2.city = ""
        self.company2.country = "France"
        self.assertIsNone(self.criterion.match(self.company1, self.company2))

        self.company2.postal_code = ""
        self.company2.city = "paris"
        self.assertIsNone(self.criterion.match(self.company1, self.company2))

        self.company2.address = ""
        self.company2.postal_code = "12345"
        self.assertIsNone(self.criterion.match(self.company1, self.company2))

    def test_address_matches(self):
        self.company1.address = "1"
        self.company1.postal_code = "12345"
        self.company1.city = "Paris"
        self.company1.country = "france"

        self.company2.address = "1"
        self.company2.postal_code = "12345.0"
        self.company2.city = "Paris"
        self.company2.country = "france"

        self.assertTrue(self.criterion.match(self.company1, self.company2))

    def test_address_not_matching(self):
        self.company1.address = "2"
        self.company1.postal_code = "12345"
        self.company1.city = "Paris"
        self.company1.country = "france"

        self.company2.address = "1"
        self.company2.postal_code = "12345.0"
        self.company2.city = "Paris"
        self.company2.country = "france"

        match = self.criterion.match(self.company1, self.company2)
        self.assertIsNotNone(match)
        self.assertFalse(match)


class DomainNameCriterionTestCase(CriterionTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.criterion = DomainNameCriterion()

    def test_missing_field(self):
        self.company1.website = ""
        self.company2.website = "https://toto.com"

        self.assertIsNone(self.criterion.match(self.company1, self.company2))

    def test_different_domain(self):
        self.company1.website = "tata.com"
        self.company2.website = "https://toto.com"

        match = self.criterion.match(self.company1, self.company2)
        self.assertIsNotNone(match)
        self.assertFalse(match)

    def test_same_root_domain(self):
        self.company1.website = "web.toto.com/any/particular/url?view=json"
        self.company2.website = "https://toto.com"

        self.assertTrue( self.criterion.match(self.company1, self.company2))
