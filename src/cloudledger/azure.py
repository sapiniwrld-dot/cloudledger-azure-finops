import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from cloudledger.models import CostRecord


REQUIRED_AZURE_COLUMNS = {
    "PreTaxCost",
    "UsageDate",
    "ResourceGroup",
    "Currency",
}


def load_azure_query_records(path: Path) -> list[CostRecord]:
    try:
        payload: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        properties = payload["properties"]
        column_names = [column["name"] for column in properties["columns"]]
        rows = properties["rows"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise ValueError("Invalid Azure Cost Management query response") from error

    missing = REQUIRED_AZURE_COLUMNS.difference(column_names)
    if missing:
        names = ", ".join(sorted(missing))
        raise ValueError(f"Missing Azure cost columns: {names}")

    records = []
    for row_number, values in enumerate(rows, start=1):
        if len(values) != len(column_names):
            raise ValueError(f"Azure row {row_number} does not match its columns")
        row = dict(zip(column_names, values, strict=True))
        try:
            usage_date = datetime.strptime(str(row["UsageDate"]), "%Y%m%d").date()
            cost = Decimal(str(row["PreTaxCost"]))
        except (InvalidOperation, ValueError) as error:
            raise ValueError(f"Invalid Azure cost row {row_number}: {error}") from error

        records.append(
            CostRecord(
                usage_date=usage_date,
                resource_group=str(row["ResourceGroup"] or "unassigned").strip(),
                service_name=str(row.get("ServiceName") or "All Services").strip(),
                region=str(row.get("ResourceLocation") or "global").strip(),
                cost=cost,
                currency=str(row["Currency"]).strip().upper(),
            )
        )

    return records

