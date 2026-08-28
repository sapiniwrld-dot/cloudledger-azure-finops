from decimal import Decimal
from pathlib import Path

from cloudledger.ingest import load_cost_records
from cloudledger.storage import (
    connect_database,
    costs_by_service,
    import_records,
    initialize_database,
    record_count,
)


def test_import_is_idempotent_and_queryable(tmp_path: Path) -> None:
    records = load_cost_records(Path("data/sample_costs.csv"))
    connection = connect_database(tmp_path / "costs.db")
    initialize_database(connection)

    assert import_records(connection, records) == 8
    assert import_records(connection, records) == 0
    assert record_count(connection) == 8
    assert costs_by_service(connection) == {
        "Azure SQL": Decimal("25.03"),
        "Container Apps": Decimal("9.93"),
        "Storage": Decimal("2.97"),
        "Application Insights": Decimal("2.18"),
        "Key Vault": Decimal("0.74"),
    }

    connection.close()

