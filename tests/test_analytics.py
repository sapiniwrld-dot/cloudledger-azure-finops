from datetime import date
from decimal import Decimal

from cloudledger.analytics import budget_variance, costs_by_service, total_cost
from cloudledger.models import CostRecord


def record(service: str, cost: str) -> CostRecord:
    return CostRecord(
        usage_date=date(2026, 8, 1),
        resource_group="rg-cloudledger-dev",
        service_name=service,
        region="eastus2",
        cost=Decimal(cost),
        currency="USD",
    )


def test_cost_summary() -> None:
    records = [record("Storage", "4.25"), record("Compute", "12.50"), record("Storage", "1.75")]

    assert total_cost(records) == Decimal("18.50")
    assert costs_by_service(records) == {
        "Compute": Decimal("12.50"),
        "Storage": Decimal("6.00"),
    }
    assert budget_variance(records, Decimal("25")) == Decimal("6.50")

