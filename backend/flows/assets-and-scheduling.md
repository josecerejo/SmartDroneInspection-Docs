---
title: "WF1 Asset and Scheduling Runtime Flow"
weight: 30
---

# WF1 Asset and Scheduling Runtime Flow

WF1 is implemented inside the `assets` Spring Modulith module. The API is
versioned under `/api/v1`. Authorization uses the authenticated backend
principal and scoped resource lookups — never a client-supplied user,
organization, or owner id — to decide access.

## Module layout

| Package | Responsibility |
| --- | --- |
| `assets/api` | Thin controllers and Java-record request/response DTOs for assets, documents, catalog, proposals, and schedules. |
| `assets/domain` | Feature-owned JPA entities (`Asset`, `AssetDocument`, `AssetCategory`, `ChecklistTemplate`, `ChecklistItem`, `CategoryFrequencySuggestion`, `ScheduleProposal`, `InspectionSchedule`) and their state transitions. |
| `assets/repository` | Scoped Spring Data repositories, including pessimistic-lock lookups for review and selection. |
| `assets/service` | Transaction boundaries and use-case orchestration (`AssetService`, `AssetReviewService`, `AssetCatalogService`, `AssetDocumentService`, `ScheduleProposalService`, `InspectionScheduleService`, `InspectionScheduleDuePublisher`). |
| `assets/events` | The frozen WF1 → WF2 handoff contract, exported as the named interface `events`. |

`assets` may depend on `shared`, `shared::api`, `shared::exception`,
`shared::storage`, and `users`. Object storage is reached through the
`shared.storage.EvidenceObjectStore` port, so `assets` does not depend on the
`inspections` module.

## Asset lifecycle (FE-02)

An asset moves `PENDING_REVIEW` → `ACTIVE` (approved) or `PENDING_REVIEW` →
`REJECTED`. `INACTIVE` and `RETIRED` are also valid stored states. Only a
`PENDING_REVIEW` asset can be reviewed, and only a `PENDING_REVIEW` or
`INACTIVE` asset can be edited.

| Operation | Endpoint | Role | Scope |
| --- | --- | --- | --- |
| Create asset | `POST /api/v1/assets` | `CLIENT` | Authenticated actor's organization; starts `PENDING_REVIEW`. |
| List assets | `GET /api/v1/assets` | `CLIENT`, `ADMIN` | Organization-scoped. |
| Read asset | `GET /api/v1/assets/{assetId}` | `CLIENT`, `ADMIN` | Organization-scoped. |
| Update asset | `PUT /api/v1/assets/{assetId}` | `CLIENT` | Organization-scoped; pending/inactive only. |
| Review asset | `POST /api/v1/assets/{assetId}/review` | `SERVICE_MANAGER` | **Platform-scoped** (Service Manager has no organization). |
| Review queue | `GET /api/v1/assets/pending-review` | `SERVICE_MANAGER` | **Platform-scoped**; lists every `PENDING_REVIEW` asset. |
| Upload document | `POST /api/v1/assets/{assetId}/documents` | `CLIENT`, `ADMIN` | Organization-scoped; active/inactive assets only. |
| List documents | `GET /api/v1/assets/{assetId}/documents` | `CLIENT`, `ADMIN`, `SERVICE_MANAGER` | Organization-scoped. |
| Stream document | `GET /api/v1/assets/{assetId}/documents/{documentId}/content` | `CLIENT`, `ADMIN`, `SERVICE_MANAGER` | Rechecks asset scope before streaming. |

Document upload accepts `image/png`, `image/jpeg`, `image/webp`, and
`application/pdf` up to 10 MB; anything else is rejected before storage. The
backend computes a SHA-256 checksum and stores the object under
`assets/{assetId}/documents/{uuid}`. MinIO storage is optional: the
`EvidenceObjectStore` bean exists only when object storage is configured, and
document endpoints report that storage is unavailable otherwise.

The review queue is deliberately separate from `GET /api/v1/assets`. The
general list is organization-scoped and closed to `SERVICE_MANAGER`, whose
accounts carry no organization.

## Categories and suggested frequencies (FE-02)

Admin maintains the catalog that drives proposal generation.

| Operation | Endpoint | Role |
| --- | --- | --- |
| List categories | `GET /api/v1/asset-categories` | Any authenticated user |
| Create category | `POST /api/v1/asset-categories` | `ADMIN` |
| Update category | `PUT /api/v1/asset-categories/{categoryId}` | `ADMIN` |
| List suggested frequencies | `GET /api/v1/asset-categories/{categoryId}/suggested-frequencies` | Any authenticated user |
| Add suggested frequency | `POST /api/v1/asset-categories/{categoryId}/suggested-frequencies` | `ADMIN` |
| Delete suggested frequency | `DELETE /api/v1/asset-categories/{categoryId}/suggested-frequencies/{frequencyId}` | `ADMIN` |

A suggested frequency is a `(frequencyUnit, frequencyInterval)` pair with a
`sortOrder`, unique per category. Valid units are `DAY`, `WEEK`, `MONTH`, and
`YEAR`; the interval must be positive.

## Schedule proposals (FE-02)

The Client no longer creates an inspection schedule directly. The platform
proposes cadences, the Service Manager reviews them, and the Client selects
one.

```text
approve asset
  -> for each category suggested frequency: GENERATED
       -> Manager APPROVE   -> MANAGER_APPROVED
       -> Manager REJECT    -> MANAGER_REJECTED
       -> Manager adjusts the interval before approving
  -> Client selects one MANAGER_APPROVED proposal
       -> that proposal  -> CLIENT_SELECTED  (active schedule created)
       -> its siblings    -> SUPERSEDED
```

| Operation | Endpoint | Role | Scope |
| --- | --- | --- | --- |
| List proposals for an asset | `GET /api/v1/schedule-proposals?assetId={assetId}` | `CLIENT`, `SERVICE_MANAGER`, `ADMIN` | Client sees only `MANAGER_APPROVED` options of owned assets; Manager sees every proposal. |
| Review proposal | `POST /api/v1/schedule-proposals/{proposalId}/review` | `SERVICE_MANAGER` | Approve or reject, optionally adjusting the frequency. |
| Select proposal | `POST /api/v1/schedule-proposals/{proposalId}/select` | `CLIENT` | Owned asset, no existing active schedule. |

Approving an asset requires the category to have at least one suggested
frequency and an active checklist template; otherwise the review fails with
`NO_SUGGESTED_FREQUENCIES` or `NO_ACTIVE_CHECKLIST` (409). A review request
that supplies only one of `frequencyUnit` and `frequencyInterval` is rejected
with `VALIDATION_FAILED` (400). Selecting a proposal locks the proposal and the
asset row, so a concurrent second selection cannot create a second active
schedule.

## Schedule lifecycle (FE-02)

| Operation | Endpoint | Role | Scope |
| --- | --- | --- | --- |
| List schedules | `GET /api/v1/inspection-schedules?assetId={assetId}` | `CLIENT`, `ADMIN` | Organization-scoped. |
| Pause schedule | `POST /api/v1/inspection-schedules/{scheduleId}/pause` | `CLIENT` | Organization-scoped; active only. |
| Activate schedule | `POST /api/v1/inspection-schedules/{scheduleId}/activate` | `CLIENT` | Organization-scoped; requires an active asset and checklist. |

## WF1 → WF2 due-cycle handoff

`InspectionScheduleDuePublisher` runs on a one-minute fixed delay. It selects
due `ACTIVE` schedules with a pessimistic write lock and, for each one,
publishes one `InspectionScheduleDue` event and then advances the schedule in
the same transaction.

```text
InspectionScheduleDue(
  organizationId, assetId, scheduleId,
  checklistTemplateVersionId, dueCycle)
```

The event identity is `(assetId, scheduleId, dueCycle)`. Because
`markGenerated` records `lastGeneratedDueCycle` and advances `nextDueAt` inside
the same transaction as the publish, a replayed run cannot publish the same
cycle twice. The consumer side — one `PERIODIC` inspection request per replayed
event — belongs to WF2.

The record is a frozen contract and is consumed through the exported
`assets::events` named interface. The publisher calls its own transactional
method through the Spring proxy, so the scheduler path is genuinely
transactional rather than relying on self-invocation.
