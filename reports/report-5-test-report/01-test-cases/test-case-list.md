# Test Cases sheet source

This table mirrors the `Test Cases` sheet. The workbook columns and order are
fixed: `No`, `Function Name`, `Sheet Name`, `Description`, `Pre-Condition`.

## Project and environment notes

| Field | Value |
| --- | --- |
| Project Name | SmartDroneInspection |
| Project Code | SEP490 — *confirm with project owner* |
| Test environment | Local/integration environment with PostgreSQL, Redis, backend API, web client, and mobile client; MinIO is used for runtime/storage verification, while S3Mock 5.2.3 is used by CI S3 API integration tests. |
| Baseline | Current WF1–WF4 main-flow scope; no autonomous drone flight control. |

The FE-01 supporting verification is intentionally outside the workbook case
index and functional-case statistics; its auth-flow and role-policy evidence is
recorded in `03-features/fe-01-identity-access-governance.md`.

## Case index

The `Sheet Name` column refers to the fixed workbook sheet, not to an SRS
feature code. `FE-xx` identifies the product feature and `WFx-yyy` identifies
the business-flow test case. For example, `WF4-001` is correctly placed on
the `Feature 2` sheet because the template groups WF3 and WF4 there; it maps
to FE-07, not FE-02.

The FE-01 role-aware portal/navigation policy check, browser authentication
flow checks, and cross-cutting API response-envelope contract checks are
recorded separately in `03-features/fe-01-identity-access-governance.md`. These supporting checks
verify SRS access and API contracts; they are not additional WFx functional
cases or workbook rows.

FE-08 Dashboard, Analytics and Notifications has no assigned WFx case in this
baseline. Treat it as an uncovered feature, not an implicitly passed or
pending workbook test.

`WF1-011`-`WF1-019` record the 2026-09-28 schedule-proposal revision of WF1.
The `WF1-005`-`WF1-010` range is unallocated; case IDs are stable and are
therefore not reused to close the gap.

| No | Function Name | Sheet Name | Description | Pre-Condition |
| ---: | --- | --- | --- | --- |
| 1 | `[WF1-001]` FE-02 — WF1 asset catalog and scheduling | Feature 1 | Admin maintains an inspection category/checklist and the system exposes it for planning. | Admin is authenticated; the category/checklist is valid and active. |
| 2 | `[WF1-002]` FE-02 — WF1 asset catalog and scheduling | Feature 1 | Client creates an asset for the client organization and can view its own asset. | Client is active and belongs to an organization. |
| 3 | `[WF1-003]` FE-02 — WF1 asset catalog and scheduling | Feature 1 | A client cannot read or modify an asset owned by another organization. | Two organizations exist; the client is authenticated in organization A. |
| 4 | `[WF1-004]` FE-02 — WF1 asset catalog and scheduling | Feature 1 | An active periodic schedule creates one due request for the correct asset and cycle. | Active asset and schedule exist; the due cycle is reached. |
| 5 | `[WF2-001]` FE-03 — WF2 request and quotation | Feature 1 | Client creates an ad-hoc inspection request with scope, location, and preferred timing. | Client owns the organization and required asset exists. |
| 6 | `[WF2-002]` FE-03 — WF2 request and quotation | Feature 1 | Service Manager prepares a versioned quotation and sends it to the client. | A valid request is visible to the Service Manager; pricing data is complete. |
| 7 | `[WF2-003]` FE-03 — WF2 order and assignment | Feature 1 | Client approves the quotation and the system records the confirmed order and billing milestone. | Quotation is in an approvable state; client has organization scope. |
| 8 | `[WF2-004]` FE-03 — WF2 order and assignment | Feature 1 | Service Manager assigns an Inspector; an unassigned or conflicting Inspector cannot access the task. | Confirmed order exists; candidate Inspector is active. |
| 9 | `[WF3-001]` FE-04 — WF3 inspection execution | Feature 2 | Assigned Inspector starts an accepted inspection, loads and saves its checklist, and cannot access another Inspector's checklist. | Active Inspector owns an accepted assignment; its inspection is in progress and checklist is published. |
| 10 | `[WF3-002]` FE-04 — WF3 evidence and traceability | Feature 2 | Inspector uploads supported evidence through the MinIO SDK adapter with server checksum/source metadata, retry-safe persistence, and scoped read access. | Assigned inspection is in progress; valid image, PostgreSQL, and an S3-compatible test endpoint are available (S3Mock in CI; MinIO in runtime verification). |
| 11 | `[WF3-003]` FE-05 — WF3 AI candidate review | Feature 2 | Inspector reviews AI candidates or adds a manual finding; pending/rejected detections remain non-official and AI failure preserves manual entry. | Eligible evidence exists; deterministic inference stub or manual fallback is available. |
| 12 | `[WF3-004]` FE-06 — WF3 report review and release | Feature 2 | Report progresses through independent review, Manager release, and Client accept/revision; accepted version and handoff are protected. | Checklist, evidence, and verified findings exist; author, reviewer, Manager, and owning Client scopes are configured. |
| 13 | `[WF4-001]` FE-07 — WF4 maintenance ticket | Feature 2 | Client creates a maintenance ticket from an accepted finding and sees only its organization data. | A released report contains an accepted finding. |
| 14 | `[WF4-002]` FE-07 — WF4 assessment and execution | Feature 2 | Maintenance Engineer views and updates only assigned assessment/execution work. | Ticket is assigned to the engineer; required service scope exists. |
| 15 | `[WF4-003]` FE-07 — WF4 rework and billing | Feature 2 | Client approval, rework/reinspection, and post-service invoice/payment status follow the configured milestone. | Maintenance work is complete or requires rework; invoice status is available. |
| 16 | `[WF1-011]` FE-02 — WF1 schedule proposals and due cycle | Feature 1 | Client registers an asset and it starts in `PENDING_REVIEW`. | Client is active with organization scope; an active category exists. |
| 17 | `[WF1-012]` FE-02 — WF1 schedule proposals and due cycle | Feature 1 | Service Manager approves a pending asset and the platform generates one proposal per suggested frequency. | Asset is `PENDING_REVIEW`; its category has suggested frequencies and an active checklist template. |
| 18 | `[WF1-013]` FE-02 — WF1 schedule proposals and due cycle | Feature 1 | Service Manager rejects a pending asset and no proposals are generated. | Asset is `PENDING_REVIEW`. |
| 19 | `[WF1-014]` FE-02 — WF1 schedule proposals and due cycle | Feature 1 | Service Manager approves, rejects, or adjusts the frequency of a generated proposal. | Asset is `ACTIVE` and its proposals are `GENERATED`. |
| 20 | `[WF1-015]` FE-02 — WF1 schedule proposals and due cycle | Feature 1 | Client selects one approved proposal, creating the active schedule and superseding its siblings. | At least one `MANAGER_APPROVED` proposal exists for an owned asset with no active schedule. |
| 21 | `[WF1-016]` FE-02 — WF1 schedule proposals and due cycle | Feature 1 | Repeating a selection and selecting another organization's proposal are both denied. | An active schedule already exists, and a foreign-organization proposal exists. |
| 22 | `[WF1-017]` FE-03 — WF1 schedule proposals and due cycle | Feature 1 | The due-cycle publisher emits one event per cycle and a replay stays silent. | An `ACTIVE` schedule has `next_due_at` in the past. |
| 23 | `[WF1-018]` FE-03 — WF1 schedule proposals and due cycle | Feature 1 | Asset document upload enforces file type, size, asset state, and organization scope. | Active asset exists; png/jpeg/webp/pdf and oversize fixtures are available. |
| 24 | `[WF1-019]` FE-03 — WF1 schedule proposals and due cycle | Feature 1 | Negative scope sweep across every WF1 endpoint. | Two organizations and the five role fixtures exist. |
