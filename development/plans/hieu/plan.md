# WF1 Plan — Hiếu

**Owner**: Hiếu
**Flow**: WF1 — Assets and Periodic Scheduling
**Jira Epic**: `SCRUM-54`
**Capacity**: 17 planned days + 3 reserve days

## Outcome

Client asset and schedule actions produce one organization-scoped periodic request. The flow
must pass the G2 handoff and its negative authorization cases.

## Owner tasks

- `T005`–`T006` — Admin catalog (categories, checklist templates, per-category suggested
  frequencies) and organization-scoped asset APIs; asset creation starts in `PENDING_REVIEW`
  and the Service Manager reviews it through a platform-scoped queue.
- `T007`–`T008` — Client asset screens and authorized document upload.
- `T009`–`T010` — schedule lifecycle and durable due-cycle event. The schedule is created only
  when the Client selects a `MANAGER_APPROVED` proposal; the remaining proposals are superseded.
- `T011` — proposal comparison/selection, schedule, asset review queue, and Admin catalog web
  screens.
- `T012`–`T013` — WF1→WF2 handoff, security regression, and flow documentation.

The full task descriptions, estimates, acceptance criteria, and Jira mapping remain in
[tasks.md](../bach/2026-09-22-four-week-mainflow-delivery/tasks.md).

## Delivery windows

| Jira sprint | Dates | Focus |
| --- | --- | --- |
| W3 — Foundation & DB | Sep 28–Oct 2 | Catalog and asset API |
| W4 — WF1 & WF2 Core | Oct 5–9 | Schedule lifecycle, due event, handoff test |
| W5 — WF3 & WF4 Core | Oct 12–16 | Asset/document and catalog/schedule web UI |
| W6 — Integration & Demo | Oct 19–23 | Regression, documentation, integration support |

## Handoff and acceptance

- Publish one idempotent due-cycle event per asset, schedule, and cycle.
- Consumer WF2 creates at most one `PERIODIC` request for a replayed event.
- Reject inactive assets, unavailable checklists, duplicate codes, and cross-organization access.
- G2 is green before the integrated five-role demo.

## Deviations

- **T012 executed producer-side.** `PeriodicRequestHandoffTest` asserts event identity, payload,
  and per-cycle idempotency with an in-process listener standing in for the WF2 consumer. The real
  consumer integration (one `PERIODIC` request per replayed event) belongs to T021.

## References

- [WF1 schedule-proposal spec](2026-09-25-wf1-schedule-proposal-flow/spec.md)
- [WF1 schedule-proposal implementation plan](2026-09-25-wf1-schedule-proposal-flow/plan.md)
- [WF1 implementation README](2026-09-25-wf1-schedule-proposal-flow/README.md)
- [Shared four-week plan](../bach/2026-09-22-four-week-mainflow-delivery/plan.md)
- [Shared handoff contract](../bach/2026-09-22-four-week-mainflow-delivery/flow-handoffs.md)
- [Jira import guide](../bach/2026-09-22-four-week-mainflow-delivery/jira-import-guide.md)
