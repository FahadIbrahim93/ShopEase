# ShopEase Project Operating System (Issue + PR Workflow)

This document defines a platform-agnostic process that works across GitHub, GitLab, Jira, Linear, and AI coding assistants.

## 1. Workflow States

Use these states consistently in any platform:
1. **Backlog**: captured but unrefined.
2. **Ready**: scoped with acceptance criteria and owner.
3. **In Progress**: active work.
4. **In Review**: PR open and awaiting feedback.
5. **Done**: merged and validated.
6. **Blocked**: external dependency unresolved.

## 2. Issue Taxonomy

Required issue types:
- **Epic**: strategic objective spanning multiple features.
- **Feature**: user-visible capability.
- **Task**: technical unit of execution.
- **Bug**: defect against expected behavior.
- **Security**: vulnerability/remediation action.

Priority scale:
- `P0` critical now
- `P1` high
- `P2` normal
- `P3` low

## 3. Label System

Apply structured labels:

- Type: `type:epic`, `type:feature`, `type:task`, `type:bug`, `type:security`
- Priority: `priority:p0` ... `priority:p3`
- Area: `area:backend`, `area:frontend`, `area:platform`, `area:security`, `area:data`
- Status: `status:blocked` (only when blocked)
- AI execution: `ai:ready`, `ai:needs-context`, `ai:human-only`

## 4. Branch and Commit Convention

Branch naming:
- `feat/<issue-id>-short-name`
- `fix/<issue-id>-short-name`
- `chore/<issue-id>-short-name`

Commit naming (Conventional Commits):
- `feat(scope): add inventory normalization pipeline`
- `fix(api): handle invalid marketplace payload`
- `docs(process): add issue and PR templates`

## 5. PR Requirements (Definition of Done Gate)

A PR can merge only when all are true:
- Linked issue exists.
- Acceptance criteria are satisfied.
- Tests added/updated and passing.
- Security checks pass.
- Docs updated where behavior changed.
- Rollback impact noted.

## 6. AI-Coder Handoff Packet (Required in every issue)

To support work from multiple platforms and AI coders, each issue must include:
- Problem statement and business impact.
- Exact scope and non-goals.
- Interfaces/contracts touched.
- Constraints (performance, security, compatibility).
- Test plan and expected evidence.
- Completion checklist.

## 7. Recommended Board Setup (Any Platform)

Columns:
- Backlog
- Ready
- In Progress
- In Review
- Blocked
- Done

Swimlanes:
- Product
- Engineering
- Security
- Reliability

## 8. Cadence

- Weekly planning: prioritize top `P0/P1` only.
- Daily async updates: blockers + next action.
- Weekly architecture/security review.
- Release retro: defect escapes, MTTR, and process improvements.
