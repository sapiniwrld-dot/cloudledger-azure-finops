import argparse
import csv
import random
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


SERVICES = {
    "Azure SQL": ("rg-data-dev", Decimal("4.20")),
    "Container Apps": ("rg-app-dev", Decimal("2.10")),
    "Storage": ("rg-data-dev", Decimal("0.65")),
    "Application Insights": ("rg-app-dev", Decimal("0.80")),
}


def generate_rows() -> list[dict[str, str]]:
    generator = random.Random(42)
    start = date(2026, 5, 31)
    rows = []

    for day_number in range(90):
        usage_date = start + timedelta(days=day_number)
        weekend_factor = Decimal("0.72") if usage_date.weekday() >= 5 else Decimal("1")
        growth_factor = Decimal("1") + Decimal(day_number) * Decimal("0.0015")

        for service_name, (resource_group, base_cost) in SERVICES.items():
            noise = Decimal(str(generator.uniform(0.95, 1.05)))
            cost = base_cost * weekend_factor * growth_factor * noise

            if day_number == 47 and service_name == "Azure SQL":
                cost += Decimal("18.00")
            if day_number == 76 and service_name == "Container Apps":
                cost += Decimal("12.00")

            rows.append(
                {
                    "usage_date": usage_date.isoformat(),
                    "resource_group": resource_group,
                    "service_name": service_name,
                    "region": "eastus2",
                    "cost": str(cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                    "currency": "USD",
                }
            )

    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic Azure cost data.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/synthetic_costs_90d.csv"),
    )
    args = parser.parse_args()

    rows = generate_rows()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} synthetic records at {args.output}")


if __name__ == "__main__":
    main()
