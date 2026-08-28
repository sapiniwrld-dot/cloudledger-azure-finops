from pathlib import Path

import pytest

from cloudledger.ingest import load_cost_records


def test_loads_sample_costs() -> None:
    records = load_cost_records(Path("data/sample_costs.csv"))

    assert len(records) == 8
    assert {record.currency for record in records} == {"USD"}


def test_rejects_missing_columns(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.csv"
    invalid.write_text("usage_date,cost\n2026-08-01,1.00\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required columns"):
        load_cost_records(invalid)

