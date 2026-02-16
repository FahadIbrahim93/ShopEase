# Contributing to ShopEase

## Purpose
This project is set up for parallel execution by humans and AI coders. Quality and traceability are mandatory.

## Ground Rules
- Every code change must map to an issue.
- No direct commits to main branch.
- Keep pull requests small and reviewable.
- Include objective evidence (tests/checks) in PR description.

## Workflow
1. Open or select an issue from templates in `.github/ISSUE_TEMPLATE`.
2. Move issue to `Ready` only after acceptance criteria are complete.
3. Create branch using naming convention:
   - `feat/<issue-id>-short-name`
   - `fix/<issue-id>-short-name`
   - `chore/<issue-id>-short-name`
4. Commit using Conventional Commits.
5. Open PR using `.github/PULL_REQUEST_TEMPLATE.md`.
6. Merge only after review + checks pass.

## Definition of Ready
- Problem statement exists.
- Scope and non-goals are explicit.
- Acceptance criteria are testable.
- Dependencies are identified.

## Definition of Done
- Acceptance criteria met.
- Relevant tests pass.
- Security impact addressed.
- Documentation updated.
- Rollback approach documented in PR.

## Recommended Review SLA
- First response: < 1 business day
- Follow-up cycles: < 1 business day each

## Documentation Structure
- `docs/RESEARCH_AND_10_10_PLAN.md`: strategic execution plan.
- `docs/PROJECT_OPERATING_SYSTEM.md`: issue/PR governance model.
- `CTO_AUDIT_REPORT.md`: initial baseline audit snapshot.
