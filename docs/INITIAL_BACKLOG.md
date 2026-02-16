# Initial Backlog Seed (Create These as Issues)

Use the templates under `.github/ISSUE_TEMPLATE/` to create these immediately.

## Epics
1. [EPIC] Core Inventory Platform MVP
2. [EPIC] Security and Compliance Baseline
3. [EPIC] Observability and Operations Excellence
4. [EPIC] Delivery Automation and Release Governance

## P0 Features/Tasks
- [FEATURE] API authentication and key rotation policy
- [FEATURE] Inventory sync idempotency and conflict handling
- [TASK] Persist inventory storage (replace in-memory with database)
- [TASK] Add migration framework and schema versioning
- [SECURITY] Add secret scanning and dependency vulnerability gate in CI
- [TASK] Add OpenAPI contract versioning and changelog policy

## P1 Features/Tasks
- [FEATURE] Inventory reservation and release workflow
- [FEATURE] Multi-channel catalog mapping rules
- [TASK] Add structured request logging and correlation IDs across services
- [TASK] Add SLO dashboard and alert thresholds

## Bugs to Watch
- [BUG] Concurrent writes produce stale updates (when persistence is added)
- [BUG] Invalid marketplace payload edge cases in sync endpoint
