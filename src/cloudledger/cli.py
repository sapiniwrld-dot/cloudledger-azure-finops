import argparse
from decimal import Decimal
from pathlib import Path

from cloudledger.analytics import budget_variance, costs_by_service, total_cost
from cloudledger.ingest import load_cost_records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze Azure cost export data.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze = subparsers.add_parser("analyze", help="Summarize a cost CSV file.")
    analyze.add_argument("csv_file", type=Path)
    analyze.add_argument("--budget", type=Decimal, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    records = load_cost_records(args.csv_file)
    currency = records[0].currency if records else "USD"

    print("CloudLedger cost summary")
    print(f"Total: {total_cost(records):.2f} {currency}")
    print(f"Budget remaining: {budget_variance(records, args.budget):.2f} {currency}")
    print("By service:")
    for service, cost in costs_by_service(records).items():
        print(f"  {service}: {cost:.2f} {currency}")


if __name__ == "__main__":
    main()

