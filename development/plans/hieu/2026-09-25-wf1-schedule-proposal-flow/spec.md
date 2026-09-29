# Spec: WF1 Schedule Proposal Flow

**Owner**: Hiếu (WF1) | **Date**: 2026-09-25 | **Epic**: `SCRUM-54`
**Status**: Approved in design review (brainstorming session 2026-09-25)

## Motivation

The original WF1 design had the Client create inspection schedules directly.
The revised business decision replaces that with a platform-proposed schedule
flow: the platform proposes schedule options, a Service Manager reviews them,
and the Client picks one. This spec is the source of truth for the revised
flow; Report 3, `business-flows.md`, `database-design.md`, and the four-week
plan documents must be updated in the same change as the code.

## Decisions (from design review)

1. **T012 handoff test is producer-side** (Approach A): assert idempotent
   event publication and the frozen `InspectionScheduleDue` payload with a
   mock consumer. The real WF2 consumer integration test moves to Quốc's
   T014/T021. Deviation recorded in Report 5.
2. **Flow**: Client creates asset → `PENDING_REVIEW` → Service Manager
   approves/rejects the asset → on approval the system auto-generates **N
   schedule proposals** from the category's suggested frequencies → Manager
   edits/approves each proposal → Client compares and **selects exactly one**
   → an `inspection_schedules` row is created `ACTIVE`; the remaining
   proposals become `SUPERSEDED`.
3. **Client cannot create schedules directly** — only by selecting an
   approved proposal.
4. **Proposal generation**: system-generated per category policy (Approach C:
   auto-generate, Manager reviews/adjusts before the Client sees them).
5. **Policy configuration**: Admin configures suggested frequencies per
   category in the catalog API/UI (part of T005), stored in a new table.
6. **Modeling**: separate `schedule_proposals` entity (Approach 1);
   `InspectionScheduleStatus` enum is unchanged, so T009/T010 schedule
   lifecycle and due-cycle publication are unaffected.

## Domain and migration

### Enum changes

```java
public enum AssetStatus {
  PENDING_REVIEW,  // new — Client created, awaiting Manager review
  REJECTED,        // new — Manager rejected (RETIRED is NOT reused)
  ACTIVE, INACTIVE, RETIRED
}
```

`InspectionScheduleStatus` stays `ACTIVE / PAUSED / DISABLED`.

### Migration `V11__schedule_proposals_and_category_policy.sql`

Forward-only; no applied migration is rewritten.

1. **`category_frequency_suggestions`** — Admin policy per category:
   `id UUID PK`, `asset_category_id FK → asset_categories`,
   `frequency_unit VARCHAR` (DAY/WEEK/MONTH/YEAR check), `frequency_interval INT > 0`,
   `sort_order INT`.
2. **`schedule_proposals`**:
   `id UUID PK`, `asset_id FK`, `checklist_template_id FK` (the active
   `checklist_templates` row of the asset's category at generation time;
   Manager review may not change it),
   `frequency_unit`, `frequency_interval`,
   `status VARCHAR` (`GENERATED`, `MANAGER_APPROVED`, `MANAGER_REJECTED`,
   `CLIENT_SELECTED`, `SUPERSEDED`),
   `manager_note VARCHAR(500) NULL`,
   `reviewed_by_user_id UUID NULL`, `selected_by_user_id UUID NULL`,
   `created_at`, `updated_at`, `row_version`.

### Lifecycle

```text
Client creates asset            → PENDING_REVIEW
Manager approves asset          → ACTIVE + N proposals (1 per suggested frequency)
Manager edits/approves proposal → MANAGER_APPROVED (or MANAGER_REJECTED)
                                  Client sees only MANAGER_APPROVED, own org
Client selects one proposal     → proposal CLIENT_SELECTED
                                → inspection_schedules row created ACTIVE
                                → other proposals → SUPERSEDED
Manager rejects asset           → REJECTED, no proposals
```

## Backend structure (module `assets`)

```text
assets/
├── api/
│   ├── AssetCatalogController.java        # T005 — categories + suggested frequencies + checklists
│   ├── AssetController.java               # T006 — Client CRUD + Manager review action
│   ├── AssetDocumentController.java       # T008
│   ├── ScheduleProposalController.java    # new — Manager review + Client list/select
│   ├── InspectionScheduleController.java  # T009/T011 — list/pause/activate
│   └── dto/{request,response}/…
├── service/
│   ├── AssetCatalogService.java
│   ├── AssetService.java                  # create → PENDING_REVIEW; scoped queries
│   ├── AssetReviewService.java            # approve → generate N proposals / reject
│   ├── ScheduleProposalService.java       # manager edit/approve; client select
│   ├── AssetDocumentService.java
│   ├── InspectionScheduleService.java     # input comes only from a selected proposal
│   └── InspectionScheduleDuePublisher.java
├── events/InspectionScheduleDue.java
└── repository/ + ScheduleProposalRepository + CategoryFrequencySuggestionRepository
```

## API contract (`/api/v1`, `ApiResponse.success` envelope)

| Route | Method | Role / scope |
| --- | --- | --- |
| `/asset-categories` | GET | authenticated read; POST/PUT **ADMIN** |
| `/asset-categories/{id}/suggested-frequencies` | GET/POST/DELETE | **ADMIN** |
| `/checklist-templates` | GET/POST/PUT | read: ADMIN+MANAGER; write: **ADMIN** |
| `/assets` | POST | **CLIENT**, org from principal → `PENDING_REVIEW` |
| `/assets` | GET | org-scoped list/detail (CLIENT/ADMIN/…) |
| `/assets/{id}` | PUT | **CLIENT** own org, only `PENDING_REVIEW`/`INACTIVE` |
| `/assets/{id}/review` | POST | **SERVICE_MANAGER** — `APPROVE` / `REJECTED` |
| `/assets/{id}/documents` | GET/POST | **CLIENT** own org + ADMIN; type/size/org checked before MinIO write |
| `/schedule-proposals` | GET | **CLIENT** own org, only `MANAGER_APPROVED` |
| `/schedule-proposals/{id}/review` | POST | **SERVICE_MANAGER** — `APPROVE`/`REJECT`, may edit unit/interval |
| `/schedule-proposals/{id}/select` | POST | **CLIENT** own org → creates ACTIVE schedule, supersedes siblings |
| `/inspection-schedules` | GET, `/pause`, `/activate` | **CLIENT** own org / ADMIN (T009) |

The server derives organization from the authenticated principal; a trusted
`organizationId` in the request body is never accepted.

## Due-cycle event (T010)

```java
public record InspectionScheduleDue(
    UUID organizationId, UUID assetId, UUID scheduleId,
    UUID checklistTemplateVersionId, LocalDate dueCycle) {}
```

- Publishes `InspectionScheduleDue` for rows where
  `status = ACTIVE AND next_due_at <= now`.
- Sets `lastGeneratedDueCycle` **before** publishing so the unique
  `(assetId, scheduleId, dueCycle)` identity makes replay idempotent; the
  Modulith event publication registry (migration V2) provides durable delivery.
- Payload and identity match the frozen contract in
  `development/plans/bach/2026-09-22-four-week-mainflow-delivery/flow-handoffs.md`.

## Frontend (feature `features/assets`)

```text
api/   assetApi.ts (modify), catalogApi.ts, proposalApi.ts, documentApi.ts  (new)
hooks/ useAssets.ts (modify), useCatalog.ts, useProposals.ts, useAssetDocuments.ts (new)
pages/ AssetsPage.tsx (modify — status badges, create form, detail + upload)
       ScheduleProposalsPage.tsx  (new — Client compares N options, selects one)
       InspectionSchedulesPage.tsx (new, T011)
       AssetReviewPage.tsx        (new — Manager: asset queue + proposal review)
       AssetCatalogPage.tsx       (new, T011 — Admin: categories + suggested frequencies)
```

- `accessPolicy.ts`: `SECTION_ROLE_ACCESS.operations.assets` →
  `['SERVICE_MANAGER']` (Inspector and Maintenance Engineer stay excluded).
- `router.tsx`: add the four new routes as lazy imports, following the
  existing portal-section pattern.
- TanStack Query owns server state; toast via existing `useToastStore`.

## Test plan

| Task | Test | Key assertions |
| --- | --- | --- |
| T005 | `AssetCatalogApiIntegrationTest` | Admin CRUD OK; role denial for CLIENT/MANAGER; duplicate code 409; interval ≤ 0 → 400 |
| T006 | `AssetApiIntegrationTest` | create → `PENDING_REVIEW`; cross-org list/detail/update denied; duplicate code in org 409; `REJECTED` not updatable |
| review | `AssetReviewApiIntegrationTest` | only SERVICE_MANAGER; approve → ACTIVE + N proposals; reject → no proposals; re-approve idempotent |
| proposal | `ScheduleProposalApiIntegrationTest` | CLIENT sees only own-org `MANAGER_APPROVED`; select → ACTIVE schedule + siblings `SUPERSEDED`; double select / cross-org select denied; edit selected proposal → 409 |
| T008 | `AssetDocumentApiIntegrationTest` | wrong type 415; oversize 413; `PENDING_REVIEW`/cross-org asset denied; list own org |
| T009 | `InspectionScheduleServiceTest` | inactive asset / inactive checklist cannot create schedule; pause/activate transitions |
| T012 | `PeriodicRequestHandoffTest` | one publish per `(assetId, scheduleId, dueCycle)`; replay publishes nothing; payload = 5 contract fields; mock consumer receives exactly once; consumer-real deviation noted |
| T013 | `AssetWorkflowIntegrationTest` | full path create→review→proposal→select→due event; negative scope at every endpoint; `.\mvnw.cmd verify` green |

Frontend: Vitest/RTL for API unwrap + error paths and the four new pages;
`npm run lint` and `npm run build`.

## Documentation impact (same change as code)

| File | Update |
| --- | --- |
| Report 3 `03-functional-requirements.md` WF1 sections | revised flow: `PENDING_REVIEW` → Manager review → N proposals → Client selects |
| Report 3 `00-record-of-changes.md` | new change row |
| `project-reference/business-flows.md` | WF1 swimlane: Manager actor, asset-review and proposal-review/selection branches |
| `project-reference/database-design.md` | V11 tables + `AssetStatus` values |
| `development/plans/bach/2026-09-22-four-week-mainflow-delivery/{tasks,spec}.md`, `hieu/plan.md` | T006/T009 descriptions + T012 producer-side deviation |
| `flow-handoffs.md` | contract unchanged (5 fields); note upstream proposal flow |
| Report 5 `01`/`03`/`02`/`00` | new WF1 cases, statistics, cover change history |

## Verification

```powershell
cd SmartDroneInspection-Backend; .\mvnw.cmd spotless:apply; .\mvnw.cmd verify
cd ..\SmartDroneInspection-Frontend; npm run lint; npm run test; npm run build
cd ..\SmartDroneInspection-Docs; git diff --check
```

## Out of scope

- WF2 consumer implementation (Quốc's T014/T021) — T012 stays producer-side.
- Editing suggested frequencies by Managers (Admin-only policy).
- Notification/email when proposals appear (in-app list only).
