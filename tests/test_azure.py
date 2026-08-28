from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from cloudledger.azure import load_azure_query_records


def test_loads_azure_query_columns_by_name() -> None:
    records = load_azure_query_records(
        Path("tests/fixtures/azure_cost_query.json")
    )

    assert len(records) == 2
    assert records[0].usage_date == date(2026, 8, 1)
    assert records[0].service_name == "Storage"
    assert records[0].cost == Decimal("3.25")
    assert records[1].region == "eastus2"


def test_rejects_invalid_azure_response(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid Azure"):
        load_azure_query_records(invalid)
