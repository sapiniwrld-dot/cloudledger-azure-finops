# CloudLedger — Azure FinOps Data Platform

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
- Uses synthetic data safe for a public repository
- Includes automated tests

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
