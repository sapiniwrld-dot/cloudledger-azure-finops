import argparse
from decimal import Decimal
from pathlib import Path

from cloudledger.analytics import budget_variance, costs_by_service, total_cost
from cloudledger.ingest import load_cost_records
from cloudledger.storage import (
    connect_database,
    costs_by_service as database_costs_by_service,
    database_currencies,
    import_records,
    initialize_database,
    record_count,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze Azure cost export data.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze = subparsers.add_parser("analyze", help="Summarize a cost CSV file.")
    analyze.add_argument("csv_file", type=Path)
    analyze.add_argument("--budget", type=Decimal, required=True)

    import_command = subparsers.add_parser(
        "import", help="Import a cost CSV file into SQLite."
    )
    import_command.add_argument("csv_file", type=Path)
    import_command.add_argument("--database", type=Path, required=True)

    summary = subparsers.add_parser(
        "database-summary", help="Summarize costs stored in SQLite."
    )
    summary.add_argument("--database", type=Path, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "analyze":
        records = load_cost_records(args.csv_file)
        currency = records[0].currency if records else "USD"

        print("CloudLedger cost summary")
        print(f"Total: {total_cost(records):.2f} {currency}")
        print(
            f"Budget remaining: "
            f"{budget_variance(records, args.budget):.2f} {currency}"
        )
        print("By service:")
        for service, cost in costs_by_service(records).items():
            print(f"  {service}: {cost:.2f} {currency}")

    elif args.command == "import":
        records = load_cost_records(args.csv_file)
        connection = connect_database(args.database)
        try:
            initialize_database(connection)
            imported = import_records(connection, records)
            print(f"Imported: {imported}")
            print(f"Skipped duplicates: {len(records) - imported}")
            print(f"Database records: {record_count(connection)}")
        finally:
            connection.close()

    elif args.command == "database-summary":
        connection = connect_database(args.database)
        try:
            initialize_database(connection)
            currencies = ", ".join(sorted(database_currencies(connection))) or "N/A"
            print("CloudLedger database summary")
            print(f"Records: {record_count(connection)}")
            print(f"Currencies: {currencies}")
            print("By service:")
            for service, cost in database_costs_by_service(connection).items():
                print(f"  {service}: {cost:.2f}")
        finally:
            connection.close()


if __name__ == "__main__":
    main()
