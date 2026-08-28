import calendar
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from statistics import median


@dataclass(frozen=True)
class DailyServiceCost:
    usage_date: date
    service_name: str
    cost: Decimal
    currency: str


@dataclass(frozen=True)
class MonthForecast:
    month: str
    through_date: date
    actual_cost: Decimal
    projected_cost: Decimal
    budget: Decimal
    projected_utilization: Decimal


@dataclass(frozen=True)
class CostAnomaly:
    usage_date: date
    service_name: str
    cost: Decimal
    score: Decimal


def forecast_latest_month(
    daily_costs: list[DailyServiceCost], budget: Decimal
) -> MonthForecast:
    if not daily_costs:
        raise ValueError("Cannot forecast an empty dataset")
    if budget <= 0:
        raise ValueError("Budget must be greater than zero")

    latest_date = max(item.usage_date for item in daily_costs)
    current_month = [
        item
        for item in daily_costs
        if (item.usage_date.year, item.usage_date.month)
        == (latest_date.year, latest_date.month)
    ]
    actual = sum((item.cost for item in current_month), start=Decimal("0"))
    days_in_month = calendar.monthrange(latest_date.year, latest_date.month)[1]
    projected = (actual / Decimal(latest_date.day) * Decimal(days_in_month)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    utilization = (projected / budget * Decimal("100")).quantize(
        Decimal("0.1"), rounding=ROUND_HALF_UP
    )
    return MonthForecast(
        month=latest_date.strftime("%Y-%m"),
        through_date=latest_date,
        actual_cost=actual,
        projected_cost=projected,
        budget=budget,
        projected_utilization=utilization,
    )


def detect_cost_anomalies(
    daily_costs: list[DailyServiceCost], threshold: Decimal = Decimal("6")
) -> list[CostAnomaly]:
    by_service: defaultdict[str, list[DailyServiceCost]] = defaultdict(list)
    for item in daily_costs:
        by_service[item.service_name].append(item)

    anomalies = []
    for service_name, items in by_service.items():
        middle = median(item.cost for item in items)
        absolute_deviations = [abs(item.cost - middle) for item in items]
        median_deviation = median(absolute_deviations)
        if median_deviation == 0:
            continue

        for item in items:
            score = Decimal("0.6745") * abs(item.cost - middle) / median_deviation
            if item.cost > middle and score >= threshold:
                anomalies.append(
                    CostAnomaly(
                        usage_date=item.usage_date,
                        service_name=service_name,
                        cost=item.cost,
                        score=score.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP),
                    )
                )

    return sorted(anomalies, key=lambda item: (item.usage_date, item.service_name))

