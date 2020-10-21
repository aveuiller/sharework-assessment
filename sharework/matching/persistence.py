from dataclasses import dataclass


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
