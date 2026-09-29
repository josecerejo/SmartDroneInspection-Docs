# Tasks: WF1–WF4 Four-Week Delivery

**Input**: [spec.md](spec.md), [plan.md](plan.md), [data-model.md](data-model.md),
[flow-handoffs.md](flow-handoffs.md), and [quickstart.md](quickstart.md).
**Jira file**: [jira-import.csv](jira-import.csv). Task IDs here appear in each Jira description.
**Estimate**: One day = eight hours. Every implementation task includes a focused behavior test
where a meaningful automated assertion is possible; write that test before changing behavior.

## Format

`[ID] [P?] [Story] Description (owner; week; estimate; acceptance)`.
`[P]` means different files and no unfinished dependency. Paths are relative to the workspace root.
The four owners are Hiếu (WF1), Quốc (WF2), Bách (WF3), and Như (WF4).

## Phase 1: Setup

- [ ] T001 [P] Smoke-test existing auth and migrations V1–V9 in `backend/src/test/java/com/smartdroneinspection/WorkflowBaselineTest.java` (Bách; FE-01/WF1; W1; 1d; a clean test environment starts, Flyway applies V1–V9, and all five role fixtures authenticate without default credentials).
- [ ] T002 [P] Freeze event fields, request/response DTO names, and state names in `docs/content/development/plans/bach/2026-09-22-four-week-mainflow-delivery/flow-handoffs.md` (Quốc; W1; 1d; WF1–WF4 owners agree on all five handoff keys before consuming APIs).

## Phase 2: Foundational Fixtures

- [ ] T003 [P] Create an accepted-assignment fixture in `backend/src/test/java/com/smartdroneinspection/inspections/InspectionFixture.java` (Bách; W1; 1d; WF3 tests can start without a completed WF2 runtime while preserving real role and organization IDs).
- [ ] T004 [P] Create an accepted-report/finding fixture in `backend/src/test/java/com/smartdroneinspection/maintenance/MaintenanceFixture.java` (Như; W1; 1d; WF4 tests can start without a completed WF3 runtime and cannot use cross-organization findings).

**Checkpoint**: The four owners can develop against stable fixtures and the agreed handoff contract.

## Phase 3: User Story 1 — WF1 Assets and Periodic Scheduling (P1)

**Owner**: Hiếu. **Goal**: Client asset and schedule actions produce one due periodic request.
**Independent test**: Create asset/schedule, retry due processing, observe one scoped request.

- [ ] T005 [US1] Implement Admin category and checklist APIs in `backend/src/main/java/com/smartdroneinspection/assets/api/AssetCatalogController.java` and `assets/service/AssetCatalogService.java` (Hiếu; W1; 2d; only Admin can activate valid catalog versions and maintain the per-category suggested inspection frequencies; test role denial).
- [ ] T006 [US1] Implement organization-scoped asset create/list/detail/update in `backend/src/main/java/com/smartdroneinspection/assets/api/AssetController.java` and `assets/service/AssetService.java` (Hiếu; W1; 2d; create starts in `PENDING_REVIEW`; duplicate code and cross-organization access are denied by scoped queries; Service Manager reviews through a platform-scoped endpoint).
- [ ] T007 [US1] Connect Client asset list/create/detail UI to live APIs in `frontend/src/features/assets/pages/AssetsPage.tsx` and `frontend/src/features/assets/api/assetApi.ts` (Hiếu; W3; 2d; Client can create and reopen an asset; loading/error/empty states work).
- [ ] T008 [US1] Add authorized asset-document upload in `backend/src/main/java/com/smartdroneinspection/assets/api/AssetDocumentController.java` and `assets/service/AssetDocumentService.java` (Hiếu; W3; 1d; file type/size and organization are checked before storing metadata/object key).
- [ ] T009 [US1] Implement schedule create/activate/pause and asset status checks in `backend/src/main/java/com/smartdroneinspection/assets/service/InspectionScheduleService.java` (Hiếu; W2; 2d; the schedule is created only from a Client-selected `MANAGER_APPROVED` proposal; inactive asset or unavailable checklist cannot produce an active schedule).
- [ ] T010 [US1] Publish durable due-cycle events in `backend/src/main/java/com/smartdroneinspection/assets/events/InspectionScheduleDue.java` and `assets/service/InspectionScheduleDuePublisher.java` (Hiếu; W2; 2d; one event identity per asset/schedule/cycle; retry is idempotent).
- [ ] T011 [US1] Build schedule and Admin catalog web screens in `frontend/src/features/assets/pages/InspectionSchedulesPage.tsx` and `frontend/src/features/assets/pages/AssetCatalogPage.tsx` (Hiếu; W3; 2d; authorized users can create/pause a schedule and Admin can manage active catalog).
- [ ] T012 [US1] Verify WF1→WF2 periodic handoff in `backend/src/test/java/com/smartdroneinspection/assets/PeriodicRequestHandoffTest.java` (Hiếu; W2; 1d; **producer-side** per the recorded deviation — real WF2 consumer test in T021; replay publishes no second event for the same cycle).
- [ ] T013 [US1] Complete WF1 security/regression run and update `backend/src/test/java/com/smartdroneinspection/assets/AssetWorkflowIntegrationTest.java` plus `backend/flows/assets-and-scheduling.md` (Hiếu; W4; 2d; own-org paths and negative scope pass; API and scheduler behavior documented in `backend/flows/assets-and-scheduling.md`).

**Checkpoint**: WF1 runs independently and G2 is green.

## Phase 4: User Story 2 — WF2 Request, Order, and Assignment (P1)

**Owner**: Quốc. **Goal**: A request becomes a confirmed order and accepted Inspector assignment.
**Independent test**: Seed an authorized asset or consume a periodic request, then complete one
approval and one reject/reassign cycle.

- [ ] T014 [US2] Implement ad hoc request creation and idempotent periodic-event consumption in `backend/src/main/java/com/smartdroneinspection/inspectionrequests/service/InspectionRequestService.java` (Quốc; W1; 2d; Client organization is derived from principal; due-cycle replay creates no duplicate).
- [ ] T015 [US2] Build Client request list/create/detail in `frontend/src/features/inspectionrequests/pages/InspectionRequestsPage.tsx` (Quốc; W3; 2d; Client submits scope, deadline, access and contact data for own asset with field errors shown).
- [ ] T016 [US2] Implement manager review and immutable quotation revisions in `backend/src/main/java/com/smartdroneinspection/inspectionrequests/service/InspectionQuotationService.java` (Quốc; W1; 2d; only current version receives a Client decision and earlier versions remain readable).
- [ ] T017 [US2] Implement Client approval and confirmed order transition in `backend/src/main/java/com/smartdroneinspection/inspectionrequests/service/InspectionOrderService.java` (Quốc; W2; 2d; approval records post-service terms; no payment gate; unapproved order cannot be assigned).
- [ ] T018 [US2] Implement Inspector assignment, rejection reason, and reassignment in `backend/src/main/java/com/smartdroneinspection/inspectionrequests/service/InspectionAssignmentService.java` (Quốc; W2; 2d; only assigned active Inspector can respond; acceptance emits G3 handoff).
- [ ] T019 [US2] Build Service Manager review/quote/assignment and Client approval pages in `frontend/src/features/inspectionrequests/pages/InspectionOrderPage.tsx` (Quốc; W3; 2d; current version, revision history, decision and assignment state are visible).
- [ ] T020 [US2] Add Inspector mobile assignment inbox and accept/reject response in `mobile/lib/features/inspections/presentation/assignments_page.dart` (Quốc; W4; 1d; only assigned items appear; rejection requires a reason; API errors are visible).
- [ ] T021 [US2] Test WF1 due request and WF2→WF3 accepted-assignment handoffs in `backend/src/test/java/com/smartdroneinspection/inspectionrequests/InspectionRequestHandoffTest.java` (Quốc; W3; 1d; real events preserve organization, asset, order and assignee IDs).
- [ ] T022 [US2] Complete revision/rejection/security regression and update `backend/src/test/java/com/smartdroneinspection/inspectionrequests/InspectionRequestWorkflowTest.java` plus `docs/content/backend/flows/inspection-requests.md` (Quốc; W4; 2d; cross-org, inactive user, unconfirmed order, and stale quotation decisions are denied).

**Checkpoint**: WF2 runs independently and G3 is green.

## Phase 5: User Story 3 — WF3 Inspection and Report (P1)

**Owner**: Bách. **Goal**: Accepted assignment produces an accepted, immutable report with
Inspector-verified findings. **Independent test**: Seed an accepted WF2 assignment and run the
inspection/report path with two distinct Inspector users.

- [ ] T023 [US3] Implement assignment-scoped inspection start and checklist responses in `backend/src/main/java/com/smartdroneinspection/inspections/service/InspectionService.java` (Bách; W1; 2d; only accepted assignee can start/update, and required checklist answers are enforced).
- [ ] T024 [US3] Connect mobile assigned inspection list/start in `mobile/lib/features/inspections/presentation/inspections_page.dart` (Bách; W1; 1d; Inspector sees only assigned inspections and an authorized start action).
- [ ] T025 [US3] Implement evidence validation, checksum, retry-safe metadata, and MinIO storage in `backend/src/main/java/com/smartdroneinspection/inspections/service/EvidenceService.java` (Bách; W2; 2d; corrupt/unsupported files fail; retry cannot duplicate an inspection evidence record).
- [ ] T026 [US3] Add configured AI candidate ingestion with safe failure behavior in `backend/src/main/java/com/smartdroneinspection/inspections/service/FindingCandidateService.java` and `backend/src/main/java/com/smartdroneinspection/infrastructure/ai/` (Bách; W2; 1d; candidate retains model/confidence/box; AI outage leaves evidence usable).
- [ ] T027 [US3] Implement confirm/modify/reject/manual finding commands in `backend/src/main/java/com/smartdroneinspection/inspections/service/VerifiedFindingService.java` (Bách; W2; 1d; rejected/unreviewed candidates never enter official findings).
- [ ] T028 [US3] Build report draft and immutable version snapshots in `backend/src/main/java/com/smartdroneinspection/inspections/service/InspectionReportService.java` (Bách; W3; 2d; revision creates a new version; accepted version cannot be overwritten).
- [ ] T029 [US3] Enforce distinct author and peer reviewer in `backend/src/main/java/com/smartdroneinspection/inspections/service/ReportReviewService.java` (Bách; W3; 1d; self-review denied and change request/technical approval recorded).
- [ ] T030 [US3] Implement manager release and Client acceptance/revision actions in `backend/src/main/java/com/smartdroneinspection/inspections/service/ReportReleaseService.java` (Bách; W3; 1d; Client sees only released version and acceptance emits billing/WF4 read handoff).
- [ ] T031 [US3] Connect web inspection and report screens in `frontend/src/features/inspections/pages/InspectionsPage.tsx` and `frontend/src/features/reports/pages/ReportsPage.tsx` (Bách; W4; 2d; authorized Inspector, reviewer, Manager and Client each see valid actions and states).
- [ ] T032 [US3] Add focused mobile checklist and photo capture in `mobile/lib/features/inspections/presentation/inspection_detail_page.dart` (Bách; W4; 1d; assigned Inspector can submit a checklist response and photo with failure/retry feedback).
- [ ] T033 [US3] Run report/authorization regression and update `backend/src/test/java/com/smartdroneinspection/inspections/InspectionWorkflowTest.java` plus `docs/content/backend/flows/inspections-and-reports.md` (Bách; W4; 2d; G3/G4 real handoff, self-review denial, hidden drafts, manual fallback and immutable acceptance pass).

**Checkpoint**: WF3 runs independently and G4 is green.

## Phase 6: User Story 4 — WF4 Maintenance and Billing (P1)

**Owner**: Như. **Goal**: Accepted findings become assessed, approved, executed, and resolved
maintenance with separate post-service invoice status. **Independent test**: Seed an accepted
report/finding and run ticket closure plus one change or re-inspection branch.

- [ ] T034 [US4] Implement ticket creation from accepted-report findings in `backend/src/main/java/com/smartdroneinspection/maintenance/service/MaintenanceTicketService.java` (Như; W1; 2d; at least one own-org verified finding is required; duplicate active ticket links are denied).
- [ ] T035 [US4] Build Client ticket create/detail in `frontend/src/features/maintenance/pages/MaintenancePage.tsx` (Như; W1; 1d; Client selects accepted findings, sees source report and receives clear validation errors).
- [ ] T036 [US4] Implement assessment assignment and Engineer estimate in `backend/src/main/java/com/smartdroneinspection/maintenance/service/MaintenanceAssessmentService.java` (Như; W2; 2d; accepted assessment assignment is required; cost range and technical scope are validated).
- [ ] T037 [US4] Add Engineer mobile assessment inbox/submit in `mobile/lib/features/tasks/presentation/assessment_page.dart` (Như; W2; 1d; assigned Engineer records scope, materials, labor, risk and estimate).
- [ ] T038 [US4] Implement versioned maintenance quote, Client approval, order, and execution assignment in `backend/src/main/java/com/smartdroneinspection/maintenance/service/MaintenanceOrderService.java` (Như; W2; 2d; approved order is required before execution; previous quote/order versions persist).
- [ ] T039 [US4] Implement assigned work logs and required before/after evidence in `backend/src/main/java/com/smartdroneinspection/maintenance/service/MaintenanceWorkService.java` (Như; W3; 2d; unrelated Engineer denied; work cannot complete without both evidence kinds).
- [ ] T040 [US4] Implement material change request and approved new order version in `backend/src/main/java/com/smartdroneinspection/maintenance/service/MaintenanceChangeService.java` (Như; W3; 2d; extra work waits for Client approval and rejected changes leave current order intact).
- [ ] T041 [US4] Implement manager release and Client accept/rework/re-inspection in `backend/src/main/java/com/smartdroneinspection/maintenance/service/MaintenanceResolutionService.java` (Như; W3; 1d; only released result is decidable; re-inspection emits one linked WF2 request).
- [ ] T042 [US4] Connect Manager/Client maintenance quote, approval and resolution views in `frontend/src/features/maintenance/pages/MaintenanceOrderPage.tsx` (Như; W4; 1d; user sees approved scope, changed versions, evidence and available decision).
- [ ] T043 [US4] Build Engineer mobile execution/progress/photo UI against the agreed DTO and an assigned-task fixture in `mobile/lib/features/tasks/presentation/task_detail_page.dart` (Như; W1; 1d; progress and before/after inputs render for the assigned Engineer; T045 connects and verifies live API authorization).
- [ ] T044 [US4] Add both post-service invoice sources with a forward migration in `backend/src/main/resources/db/migration/V10__cross_flow_invoices.sql` and `backend/src/main/java/com/smartdroneinspection/billing/` (Như; W4; 2d; one invoice per accepted inspection report or maintenance order; manual payment status; old rows preserved).
- [ ] T045 [US4] Connect the live mobile execution API, run ticket/billing/authorization regression, and update `mobile/lib/features/tasks/presentation/task_detail_page.dart`, `backend/src/test/java/com/smartdroneinspection/maintenance/MaintenanceWorkflowTest.java`, and `docs/content/backend/flows/maintenance-and-billing.md` (Như; W4; 2d; G4/G5 real handoff, mobile assignment denial, change approval, evidence, closure, invoice and cross-org denial pass).

**Checkpoint**: WF4 runs independently and the whole five-role journey in `quickstart.md` passes.

## Dependencies and Execution Order

| Dependency | Tasks | Gate |
| --- | --- | --- |
| Contract freeze before consumers | T002 → T010/T014/T018/T030/T041/T044 | W1 |
| WF1 periodic event → WF2 consumer | T010 + T014 → T012/T021 | G2 |
| WF2 accepted assignment → WF3 inspection | T018 + T023 → T021/T033 | G3 |
| WF3 accepted report → WF4 ticket | T030 + T034 → T033/T045 | G4 |
| WF4 re-inspection → WF2 ad hoc request | T041 + T014 → T045 | G5 |
| Report and maintenance acceptance → billing | T030/T041 → T044 → T045 | W4 |

WF3 may use T003 fixture before T018; WF4 may use T004 fixture before T030. Replace fixture-only
proof with real handoff tests at G3/G4. Event consumers must be idempotent so this does not create
a Modulith dependency cycle.

## Parallel Opportunities

- In W1, T001–T004 touch separate test/contract files and can run in parallel.
- WF1 T005–T006, WF2 T014/T016, WF3 T023–T024, and WF4 T034–T035/T043 can proceed concurrently
  after each relevant contract/fixture is understood.
- In W2, each owner works inside their flow's module; cross-flow changes are reviewed at G2/G3.
- In W3–W4, web and mobile work may overlap backend work within an owner's flow only after DTO shapes
  are stable; avoid competing edits to the same file.

## Implementation Strategy

Build a narrow working path in each flow first, then add the named revision and failure branches.
The first integrated milestone is WF1→WF2→WF3 through accepted assignment at the end of W2.
The second is accepted report→maintenance ticket at the end of W3. Week 4 is for billing,
re-inspection, full regression and the five-role demo. If a gate slips, preserve role/resource
scope and version history; defer only optional polish listed in [plan.md](plan.md).
