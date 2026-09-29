# WF1 — Asset Registration and Periodic Inspection Scheduling

**Owner:** Hiếu · **Epic:** `SCRUM-54` · **Repo:** `SmartDroneInspection-Backend` · **Branch:** `feat/wf1-schedule-proposal`

## What changed

The original WF1 let the **Client create the inspection schedule directly**. The revised flow makes the
platform propose schedule options, the **Service Manager** review them, and the **Client pick one**:

```text
Client creates asset            -> PENDING_REVIEW
Service Manager approves asset  -> ACTIVE
System generates N proposals    (one per category suggested frequency)
Service Manager reviews         -> MANAGER_APPROVED / MANAGER_REJECTED
Client selects exactly one      -> CLIENT_SELECTED, schedule created ACTIVE,
                                   remaining proposals SUPERSEDED
Due-cycle publisher             -> one InspectionScheduleDue event per asset+schedule+cycle
```

The Client can no longer create a schedule directly.

## Commits (backend, on top of `e219466`)

| Commit | What |
| --- | --- |
| `3758592` | Migration V11 + schedule-proposal domain and category frequency policy |
| `70cec60` | Baseline migration count -> 11; asset review lifecycle tests |
| `da2ab59` | Admin catalog API with suggested frequencies (T005) |
| `5995917` | Category name limit aligned with DB column (160) |
| `139dd7f` | Organization-scoped asset API (T006) |
| `1fdd3b8` | Organization-scoped asset search |
| `6b47560` | Asset access aligned with task contract (CLIENT+ADMIN) |
| `e875ca8` | Schedule proposal review and selection API |
| `c1db0d3` | Lock asset during selection; validate frequency pair |
| `d83a435` | Manager asset review with proposal generation |
| `53a126c` | Authorized asset document upload (T008) + storage port moved to `shared.storage` |

## API added

| Route | Methods | Role / scope |
| --- | --- | --- |
| `/api/v1/asset-categories` | GET · POST · PUT | read: authenticated · write: **ADMIN** |
| `/api/v1/asset-categories/{id}/suggested-frequencies` | GET · POST · DELETE | **ADMIN** write |
| `/api/v1/assets` | POST · GET | create: **CLIENT** (org from principal) · list: **CLIENT**, **ADMIN** |
| `/api/v1/assets/{assetId}` | GET · PUT | own organization only |
| `/api/v1/assets/{assetId}/review` | POST | **SERVICE_MANAGER** — `APPROVE` / `REJECT` |
| `/api/v1/assets/{assetId}/documents` | GET · POST | own organization (write CLIENT/ADMIN, read also MANAGER) |
| `/api/v1/assets/{assetId}/documents/{documentId}/content` | GET | own organization |
| `/api/v1/schedule-proposals` | GET | CLIENT sees own-org `MANAGER_APPROVED`; MANAGER/ADMIN see all |
| `/api/v1/schedule-proposals/{proposalId}/review` | POST | **SERVICE_MANAGER** |
| `/api/v1/schedule-proposals/{proposalId}/select` | POST | **CLIENT** own organization |

Successful responses use the shared `ApiResponse` envelope; errors are RFC 7807 `ProblemDetail`.

## Data model (migration `V11`)

- **`category_frequency_suggestions`** — Admin policy per category: `frequency_unit`, `frequency_interval`, `sort_order`.
- **`schedule_proposals`** — `asset_id`, `checklist_template_id`, frequency, `status`
  (`GENERATED` -> `MANAGER_APPROVED` / `MANAGER_REJECTED` -> `CLIENT_SELECTED` / `SUPERSEDED`),
  `manager_note`, `reviewed_by_user_id`, `selected_by_user_id`.
- **`assets.status`** CHECK widened for `PENDING_REVIEW` and `REJECTED`.
- `inspection_schedules` is written **only** from a `CLIENT_SELECTED` proposal.

## Authorization rules

- Organization is always derived from the authenticated principal — never from a request body.
- Cross-organization asset or proposal access returns `404 NOT_FOUND` (same convention as `GET /assets/{id}`).
- Asset documents can only be uploaded while the asset is `ACTIVE` or `INACTIVE`; `PENDING_REVIEW` is rejected with `409`.
- Upload validation: `image/png`, `image/jpeg`, `image/webp`, `application/pdf` (else `415`); maximum 10 MB (else `413`).
- Only `SERVICE_MANAGER` may review an asset or a proposal; only `CLIENT` may select one.

## Verified

Backend `mvnw.cmd verify` — **BUILD SUCCESS**, 159 tests, 0 failures; JaCoCo coverage gate and the
Spring Modulith boundary test pass.

| Test class | Covers |
| --- | --- |
| `ScheduleProposalModelTest` | Proposal lifecycle state machine |
| `AssetCatalogApiIntegrationTest` | Admin category and suggested-frequency management |
| `AssetApiIntegrationTest` | Client asset CRUD, org scope, duplicate code, category validation |
| `AssetReviewApiIntegrationTest` | Manager approve/reject, N proposals generated, idempotent re-approve |
| `ScheduleProposalApiIntegrationTest` | Manager review, Client select, siblings superseded, cross-org denial |
| `AssetDocumentApiIntegrationTest` | Upload type/size rules, active-only, organization scoping |
| `ModulithArchitectureTest` | Module boundaries (no `assets <-> inspections` cycle) |

## Cross-module note

`EvidenceObjectStore` moved from `inspections.spi` to **`shared.storage`** so the `assets` module can
store documents without creating a module cycle (`inspections` already depends on `assets`).
Only package and imports changed — the interface and its behavior are unchanged.

## Documentation impact

| Document | Status |
| --- | --- |
| `project-reference/business-flows.md` | **Updated** — WF1 rewritten (high-level) with Manager review steps, N-proposal comparison, Client selection |
| `project-reference/database-design.md` | **Updated** — V11 tables (`category_frequency_suggestions`, `schedule_proposals`), `assets.status` values, schedule-from-proposal note, table count 35 → 37 |
| Report 3 `03-functional-requirements.md` | **Updated** — FE-02 §3.3 flow, screen list, authorization matrix, periodic-request generation |
| Report 3 `00-record-of-changes.md` | **Updated** — 28 Sep 2026 FE-02 revision row |
| Report 5 test report | Pending — WF1 cases and execution evidence |
| `development/plans/.../tasks.md`, `hieu/plan.md` | Pending |

## Still open

- Task 7 — inspection schedule lifecycle API (list / pause / activate).
- Task 8 — durable due-cycle publisher (`InspectionScheduleDue`) + producer-side handoff test (T012).
- Tasks 9a/9b — frontend screens (asset list/create, proposal compare/select, manager review queue, Admin catalog).
- Task 10 — T013 full-flow integration and negative-scope sweep.
- Task 11 — documentation sync (Report 3, database design, Report 5) and final merge with `origin/main`.
