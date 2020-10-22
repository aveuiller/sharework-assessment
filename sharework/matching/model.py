from dataclasses import dataclass
from typing import List


@dataclass
class Company:
    source_id: int
    source_name: str
    name: str
    website: str
    email: str
    phone: str
    address: str
    postal_code: str
    city: str
    country: str


@dataclass
class CompanyMatch:
    company_a: Company
    company_b: Company
    score: float
    success_criteria: List[str]
