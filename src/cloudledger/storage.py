import hashlib
import json
import sqlite3
from collections.abc import Iterable
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from cloudledger.insights import DailyServiceCost
from cloudledger.models import CostRecord


MICROS_PER_UNIT = Decimal("1000000")


def connect_database(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS cost_records (
            id INTEGER PRIMARY KEY,
            usage_date TEXT NOT NULL,
            resource_group TEXT NOT NULL,
            service_name TEXT NOT NULL,
            region TEXT NOT NULL,
            cost_micros INTEGER NOT NULL CHECK (cost_micros >= 0),
            currency TEXT NOT NULL,
            record_hash TEXT NOT NULL UNIQUE
        );

        CREATE INDEX IF NOT EXISTS idx_cost_records_usage_date
        ON cost_records (usage_date);

        CREATE INDEX IF NOT EXISTS idx_cost_records_service_name
        ON cost_records (service_name);
        """
    )


def record_hash(record: CostRecord) -> str:
    payload = {
        "usage_date": record.usage_date.isoformat(),
        "resource_group": record.resource_group,
        "service_name": record.service_name,
        "region": record.region,
        "cost": str(record.cost),
        "currency": record.currency,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def cost_to_micros(cost: Decimal) -> int:
    micros = (cost * MICROS_PER_UNIT).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(micros)


def import_records(
    connection: sqlite3.Connection, records: Iterable[CostRecord]
) -> int:
    before = connection.total_changes
    connection.executemany(
        """
        INSERT OR IGNORE INTO cost_records (
            usage_date,
            resource_group,
            service_name,
            region,
            cost_micros,
            currency,
            record_hash
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                record.usage_date.isoformat(),
                record.resource_group,
                record.service_name,
                record.region,
                cost_to_micros(record.cost),
                record.currency,
                record_hash(record),
            )
            for record in records
        ],
    )
    connection.commit()
    return connection.total_changes - before


def record_count(connection: sqlite3.Connection) -> int:
    row = connection.execute("SELECT COUNT(*) FROM cost_records").fetchone()
    return int(row[0])


def costs_by_service(connection: sqlite3.Connection) -> dict[str, Decimal]:
    rows = connection.execute(
        """
        SELECT service_name, SUM(cost_micros) AS total_micros
        FROM cost_records
        GROUP BY service_name
        ORDER BY total_micros DESC, service_name ASC
        """
    )
    return {
        service_name: Decimal(total_micros) / MICROS_PER_UNIT
        for service_name, total_micros in rows
    }


def database_currencies(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute(
        "SELECT DISTINCT currency FROM cost_records ORDER BY currency"
    )
    return {currency for (currency,) in rows}


def daily_service_costs(connection: sqlite3.Connection) -> list[DailyServiceCost]:
    rows = connection.execute(
        """
        SELECT usage_date, service_name, SUM(cost_micros), currency
        FROM cost_records
        GROUP BY usage_date, service_name, currency
        ORDER BY usage_date, service_name
        """
    )
    return [
        DailyServiceCost(
            usage_date=date.fromisoformat(usage_date),
            service_name=service_name,
            cost=Decimal(total_micros) / MICROS_PER_UNIT,
            currency=currency,
        )
        for usage_date, service_name, total_micros, currency in rows
    ]
