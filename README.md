# CloudLedger — Azure FinOps Data Platform

CloudLedger is a portfolio project for validating, analyzing, and reporting Azure cost and usage data without committing private billing exports. The first release uses synthetic data and produces service-level totals, monthly spend, and budget variance from a repeatable command-line workflow.

## Current capabilities

- Validates required cost-export fields and numeric costs
- Aggregates spend by Azure service
- Calculates total spend and budget variance
- Uses synthetic data safe for a public repository
- Includes automated tests

## Run locally

    python -m pip install -e '.[dev]'
    cloudledger analyze data/sample_costs.csv --budget 100
    pytest -q

Real Azure exports will be stored under `exports/private/`, which Git ignores.

