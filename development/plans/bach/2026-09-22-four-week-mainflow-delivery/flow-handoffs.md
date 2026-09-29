# Proposed Flow Handoffs and API Contract Freeze

**Status**: Planning contract; owners confirm names, payloads, and error shapes in Week 1 before
client implementation. The implemented OpenAPI and tests become authoritative.

## Handoff ownership

| Producer → consumer | Public contract | Required identity/idempotency | Consumer outcome |
| --- | --- | --- | --- |
| WF1 → WF2 | `InspectionScheduleDue` in `assets::events` | `organizationId`, `assetId`, `scheduleId`, `checklistTemplateVersionId`, `dueCycle`; unique `(assetId,scheduleId,dueCycle)` | One `PERIODIC` inspection request; unavailable checklist enters manual review. Upstream flow amended 2026-09-25 — schedules originate from Manager-reviewed proposals; the event contract is unchanged. |
| WF2 → WF3 | `InspectionAssignmentAccepted` in `inspectionrequests::events` | `assignmentId`, `orderId`, `requestId`, `assetId`, `inspectorUserId`; one inspection per accepted assignment | Inspection becomes `READY_FOR_INSPECTION`. |
| WF3 → WF4 | Public `inspections` read operation for accepted report and verified findings | `reportVersionId`, `organizationId`, `assetId`, finding IDs | Client can create a ticket only from findings in their accepted report. |
| WF4 → WF2 | `ReinspectionRequested` in `maintenance::events` | `ticketId`, `organizationId`, `assetId`, `reportVersionId`; one linked request per decision | One linked `AD_HOC` request enters WF2. |
| WF3/WF4 → billing | Report acceptance / maintenance-result acceptance events | Accepted report version or maintenance order ID; one invoice per source | Separate invoice/payment-status record for each service. |

Spring Modulith event publication registry is already present. Consumers must be idempotent and
retry-safe; a published event is not permission to import another module's internal entity.
Synchronous public query operations are used when a command needs an immediate scope or state
decision. Business modules do not import each other's controllers, HTTP DTOs, or repositories.

## Minimum browser API groups

All routes are below `/api/v1`, require the existing auth profile unless explicitly public, use
typed request/response DTOs, and return the project's RFC 7807 error shape. The server derives
Client organization from the authenticated principal rather than accepting a trusted body value.

| Flow | Route group | Main operations | Role/scope |
| --- | --- | --- | --- |
| WF1 | `/assets`, `/asset-categories`, `/checklist-templates`, `/inspection-schedules` | Admin catalog; Client asset/document and schedule create/list/detail/update/pause. | Admin catalog; Client own organization. |
| WF2 | `/inspection-requests`, `/inspection-quotations`, `/inspection-orders`, `/inspection-assignments` | Client request and quote decision; Manager review/quote/confirm/assign; Inspector assignment response. | Organization or assigned user; Manager service authority. |
| WF3 | `/inspections`, `/inspection-evidence`, `/findings`, `/reports`, `/peer-reviews` | Assigned session/checklist/evidence/finding; draft/submit/review/release/Client decision. | Assigned Inspector, distinct reviewer, Manager release, Client released view. |
| WF4 | `/maintenance-tickets`, `/maintenance-assessments`, `/maintenance-orders`, `/maintenance-work`, `/maintenance-change-requests` | Ticket, assessment, quote/order, execution, change decision, release, resolution. | Client own organization; assigned Engineer; Manager service authority. |
| Billing | `/invoices` | List own service invoices and record authorized manual payment status. | Client read own organization; authorized staff status update. |

Do not implement a generic endpoint for arbitrary state transitions. Each transition should be a
named action with validated actor, current state, version, and idempotency boundary. OpenAPI must
record transport details before web/mobile integration.

## Focused mobile API and screens

Mobile uses the existing `/api/v1/mobile/auth/**` authentication contract and secure token store.
The inspection and maintenance resources may share bearer-only API operations with web when the
transport is identical. Mobile screen coverage is:

- Inspector: assigned inbox; accept/reject; view asset/checklist; start/update inspection;
  focused checklist and optional photo upload.
- Maintenance Engineer: assigned assessment/execution inbox; accept/reject; submit technical
  assessment; progress/work-log entry and before/after photo capture.

Quotation approval, report release, peer-review authoring, and Client resolution decisions remain
web-first in this four-week scope. Mobile UI visibility never replaces backend scope checks.

## Contract acceptance tests

1. An event replay does not duplicate a periodic request, inspection, re-inspection request, or
   invoice.
2. A cross-organization Client cannot read or mutate another organization's records.
3. An unassigned Inspector/Engineer cannot mutate a task by knowing its ID.
4. Report author and peer reviewer are different users.
5. Internal report drafts and comments are absent from Client responses.
6. A rejected change request cannot alter an approved maintenance order.
