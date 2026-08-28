from datetime import date
from decimal import Decimal
from pathlib import Path

from cloudledger.ingest import load_cost_records
from cloudledger.insights import (
    DailyServiceCost,
    detect_cost_anomalies,
    forecast_latest_month,
)


def load_synthetic_daily_costs() -> list[DailyServiceCost]:
    return [
        DailyServiceCost(
            usage_date=record.usage_date,
            service_name=record.service_name,
            cost=record.cost,
            currency=record.currency,
        )
        for record in load_cost_records(Path("data/synthetic_costs_90d.csv"))
    ]


def test_forecasts_latest_month() -> None:
    forecast = forecast_latest_month(
        load_synthetic_daily_costs(), budget=Decimal("250")
    )

    assert forecast.month == "2026-08"
    assert forecast.through_date == date(2026, 8, 28)
    assert forecast.projected_cost > forecast.actual_cost
    assert forecast.projected_utilization > Decimal("100")


def test_detects_known_cost_spikes() -> None:
    anomalies = detect_cost_anomalies(load_synthetic_daily_costs())

    assert [(item.usage_date, item.service_name) for item in anomalies] == [
        (date(2026, 7, 17), "Azure SQL"),
        (date(2026, 8, 15), "Container Apps"),
    ]
