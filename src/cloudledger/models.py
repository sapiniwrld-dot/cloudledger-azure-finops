from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class CostRecord:
    usage_date: date
    resource_group: str
    service_name: str
    region: str
    cost: Decimal
    currency: str

