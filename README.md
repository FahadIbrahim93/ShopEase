# ShopEase

ShopEase is now a real, testable backend service for e-commerce inventory management.

## What is implemented

- FastAPI service with inventory operations (create/update/list/adjust/sync) plus idempotent sync support.
- API key protection for mutating endpoints.
- Validation and error handling with structured HTTP responses.
- Monitoring endpoints:
  - `GET /healthz`
  - `GET /metrics` (Prometheus format)
- Automated tests (API integration tests via TestClient).
- CI pipeline (lint + tests + security scan).

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for API docs.

## Environment

Copy `.env.example` to `.env` and adjust values as needed:

- `ENVIRONMENT` (`development`, `test`, `staging`, `production`).
- `API_KEY` for write endpoints (minimum 16 chars; default key forbidden in staging/production).
- `LOW_STOCK_THRESHOLD` for reporting.

## Core endpoints

- `GET /products?limit=<n>&offset=<n>` (paginated result with `items`, `total`, `limit`, `offset`)
- `POST /products` (requires `x-api-key`)
- `POST /products/{sku}/adjust` (requires `x-api-key`)
- `POST /sync/inventory` (requires `x-api-key`, supports `x-idempotency-key`)
- `GET /reports/low-stock`

## Quality and governance docs

- Initial audit baseline: `CTO_AUDIT_REPORT.md`
- 10/10 execution strategy: `docs/RESEARCH_AND_10_10_PLAN.md`
- Project workflow OS: `docs/PROJECT_OPERATING_SYSTEM.md`
- Contribution standards: `CONTRIBUTING.md`

## Additional project docs

- Current MVP architecture: `docs/ARCHITECTURE.md`
- Backlog seed for issue creation: `docs/INITIAL_BACKLOG.md`
