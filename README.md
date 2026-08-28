# CloudLedger — Azure FinOps Data Platform

[![CI](https://github.com/sapiniwrld-dot/cloudledger-azure-finops/actions/workflows/ci.yml/badge.svg)](https://github.com/sapiniwrld-dot/cloudledger-azure-finops/actions/workflows/ci.yml)

CloudLedger is a portfolio project for validating, analyzing, and reporting Azure cost and usage data without committing private billing exports. The first release uses synthetic data and produces service-level totals, monthly spend, and budget variance from a repeatable command-line workflow.

## Current capabilities

- Validates required cost-export fields and numeric costs
- Aggregates spend by Azure service
- Calculates total spend and budget variance
- Stores validated records in an indexed SQLite database
- Prevents duplicate imports with deterministic record fingerprints
- Forecasts month-end spending and budget utilization
- Detects service-level cost anomalies using median absolute deviation
- Generates a deterministic 90-day dataset with known cost spikes
- Imports read-only Azure Cost Management Query API responses
- Uses synthetic data safe for a public repository
- Includes automated tests

## Architecture

    Azure Cost Management Query API        Synthetic CSV data
                    |                              |
                    v                              v
           Private JSON adapter  --->  Validation and normalization
                                              |
                                              v
                                  Duplicate-safe SQLite storage
                                              |
                           +------------------+------------------+
                           |                                     |
                           v                                     v
                  Budget forecasting                    Anomaly detection
                           |                                     |
                           +------------------+------------------+
                                              |
                                              v
                                      CLI FinOps reports

GitHub Actions installs the project and runs the complete test suite on every push and pull request.

## Run locally

    python -m pip install -e '.[dev]'
    cloudledger analyze data/sample_costs.csv --budget 100
    cloudledger import data/sample_costs.csv --database cloudledger.db
    cloudledger database-summary --database cloudledger.db
    python scripts/generate_sample_data.py
    cloudledger import data/synthetic_costs_90d.csv --database cloudledger-90d.db
    cloudledger insights --database cloudledger-90d.db --budget 250
    pytest -q

Real Azure exports will be stored under `exports/private/`, which Git ignores.

## Import Azure Cost Management data

Save a subscription-scoped Azure Cost Management Query API response under the ignored `exports/private/` directory, then import it into a local database:

    cloudledger azure-import exports/private/azure-cost-query.json --database azure-costs.db

The importer discovers columns by name, validates Azure's response schema, converts `YYYYMMDD` usage dates, preserves decimal costs, and prevents duplicate imports. The repository includes only a synthetic API fixture for automated tests; real subscription IDs and billing values are never committed.

API reference: [Azure Cost Management Query - Usage](https://learn.microsoft.com/en-us/rest/api/cost-management/query/usage?view=rest-cost-management-2026-06-01)
