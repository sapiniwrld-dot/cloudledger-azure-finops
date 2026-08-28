import sys
from pathlib import Path

from cloudledger.cli import main


def test_import_and_database_summary(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    database = tmp_path / "cloudledger.db"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "cloudledger",
            "import",
            "data/sample_costs.csv",
            "--database",
            str(database),
        ],
    )
    main()
    first_import = capsys.readouterr().out
    assert "Imported: 8" in first_import
    assert "Skipped duplicates: 0" in first_import

    main()
    second_import = capsys.readouterr().out
    assert "Imported: 0" in second_import
    assert "Skipped duplicates: 8" in second_import

    monkeypatch.setattr(
        sys,
        "argv",
        ["cloudledger", "database-summary", "--database", str(database)],
    )
    main()
    summary = capsys.readouterr().out
    assert "Records: 8" in summary
    assert "Currencies: USD" in summary
    assert "Azure SQL: 25.03" in summary
