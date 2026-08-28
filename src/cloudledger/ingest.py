import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from cloudledger.models import CostRecord


REQUIRED_COLUMNS = {
    "usage_date",
    "resource_group",
    "service_name",
    "region",
    "cost",
    "currency",
}


def load_cost_records(path: Path) -> list[CostRecord]:
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames or [])
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(f"Missing required columns: {names}")

        records = []
        for line_number, row in enumerate(reader, start=2):
            try:
                cost = Decimal(row["cost"])
                if cost < 0:
                    raise ValueError("cost cannot be negative")
                records.append(
                    CostRecord(
                        usage_date=date.fromisoformat(row["usage_date"]),
                        resource_group=row["resource_group"].strip(),
                        service_name=row["service_name"].strip(),
                        region=row["region"].strip(),
                        cost=cost,
                        currency=row["currency"].strip().upper(),
                    )
                )
            except (InvalidOperation, ValueError) as error:
                raise ValueError(f"Invalid record on line {line_number}: {error}") from error

    return records

