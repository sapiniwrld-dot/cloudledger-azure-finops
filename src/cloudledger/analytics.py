from collections import defaultdict
from decimal import Decimal

from cloudledger.models import CostRecord


def total_cost(records: list[CostRecord]) -> Decimal:
    return sum((record.cost for record in records), start=Decimal("0"))


def costs_by_service(records: list[CostRecord]) -> dict[str, Decimal]:
    totals: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for record in records:
        totals[record.service_name] += record.cost
    return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))


def budget_variance(records: list[CostRecord], budget: Decimal) -> Decimal:
    return budget - total_cost(records)

