# Cover sheet source

This file mirrors the fields in the `Cover` sheet. Keep the labels unchanged
when transferring values into the workbook.

| Field | Value |
| --- | --- |
| Project Name | SmartDroneInspection |
| Project Code | SEP490 — *confirm with project owner* |
| Creator | *Enter team/member name* |
| Issue Date | 2026-09-28 |
| Document Code | *Enter document code* |
| Version | 1.7 |

## Record of change

The workbook's change table uses these columns. Add one row for each approved
revision; do not remove old entries.

| Effective Date | Version | Change Item | A / D / M | Change Description | Reference |
| --- | --- | --- | --- | --- | --- |
| 2026-09-22 | 0.1 | Initial Markdown test-report source | A | Split the supplied Report 5 template into editable sections and added the current WF1–WF4 baseline cases. | Report 5 template |
| 2026-09-22 | 0.2 | FE ownership alignment | M | Added FE-01 through FE-07 mapping, recorded the FE-01 W3 auth/migration gate, and split WF3 traceability across FE-04, FE-05, and FE-06 without changing test IDs or workbook sheets. | Jira SCRUM-56, SCRUM-58, SCRUM-106, SCRUM-107, SCRUM-108 |
| 2026-09-22 | 0.3 | Week 3 automated verification | M | Recorded the passed FE-01 foundation smoke gate and FE-04 execution/checklist acceptance evidence; recalculated Round 1 statistics without changing template case IDs or layout. | `WorkflowBaselineTest`, `InspectionWorkflowTest`, `InspectionFixtureTest`, mobile inspection test |
| 2026-09-22 | 0.4 | FE-01 scope correction | M | Removed MinIO from the FE-01 foundation scope and linked evidence storage/MinIO to FE-04/WF3 task T025; retained the separate infrastructure healthcheck evidence. | Jira SCRUM-58, SCRUM-85, SCRUM-108; Report 3 SRS 3.2 and 3.5 |
| 2026-09-22 | 0.5 | Workbook feature-sheet mapping clarification | M | Clarified that Feature 1/Feature 2 are fixed workbook sheets, while FE codes identify SRS capabilities and WF IDs identify business-flow test cases; documented the WF4-to-FE-07 mapping in Feature 2. | `README.md`, `template-layout.md`, `test-case-list.md`, feature sources, and test statistics |
| 2026-09-22 | 0.6 | FE-04/FE-05 case-boundary correction | M | Removed finding creation from the FE-04 evidence case and assigned AI candidate verification/manual findings to FE-05, preserving the existing WF3 test IDs. | Report 3 SRS 3.5–3.6; FE-04 and FE-05 sources; `test-case-list.md` |
| 2026-09-24 | 0.7 | FE-01 role-aware frontend navigation | M | Recorded automated portal, screen-access, multi-role entry, legacy redirect, and denied-route verification against the existing SRS matrix; functional workbook case IDs and statistics are unchanged. | SmartDroneInspection-Frontend: `src/app/permissions/accessPolicy.test.ts`; Report 3 SRS 3.1.3 |
| 2026-09-24 | 0.8 | FE-01 browser authentication flow | M | Recorded frontend auth-contract, validation, session-return, and role-routing tests; implemented shared light login and Client registration without changing functional workbook case IDs or statistics. | SmartDroneInspection-Frontend: `src/features/auth/`; Report 3 SRS 3.2; `npm.cmd test` |
| 2026-09-24 | 0.9 | Shared API response contract | M | Recorded automated verification for the successful JSON envelope and unchanged Problem Details, 204, and binary-stream contracts; functional workbook case IDs and totals remain unchanged. | Backend `ApiResponseTest` and API integration tests; frontend/mobile envelope tests; Report 3 sections 4.1 and 5.2 |
| 2026-09-24 | 1.0 | WF3 FE-04/FE-05/FE-06 automated verification | M | Recorded passing checklist/evidence, AI candidate/manual finding, and report lifecycle cases; updated test totals and coverage while preserving all workbook sheets and stable WFx IDs. | Jira SCRUM-85–SCRUM-93; backend `mvnw verify`; frontend and mobile regression; FE-04, FE-05, and FE-06 sources |
| 2026-09-25 | 1.1 | WF3 S3 integration-test runner update | M | Recorded the unavailable MinIO CI image and successful S3Mock S3 API integration rerun; clarified that the CI mock does not replace MinIO runtime verification. | Backend PR #44 CI runs 36090635549 and 36092639825; `EvidenceApiIntegrationTest`; `MinioEvidenceObjectStoreIntegrationTest` |
| 2026-09-25 | 1.2 | FE-specific Report 5 source structure | M | Split editable feature details into exactly eight FE-specific files, retained all 15 WFx case IDs and statuses, documented FE-08 as uncovered, and made the generated preview's per-round status formulas count the corresponding round. The original template remains unchanged. | `README.md`, `template-layout.md`, `test-case-list.md`, `test-statistics.md`, and `03-features/` |
| 2026-09-26 | 1.3 | WF3 AI draft narrative and inspection completion verification | M | Recorded executed AI-draft/narrative and COMPLETED-transition evidence on WF3-004 (Round 2 note) and noted the ai-draft HTTP live-provider happy path as not run; updated Report 3 SRS 3.7.1 and business flows WF3-11/WF3-20; workbook case IDs, sheet totals, and statistics unchanged. | `InspectionReportServiceTest`, `ReportSnapshotSerializationTest`, `ReportDraftClientTest`, extended `InspectionReportApiIntegrationTest`, `InspectionServiceTest` lock test; Report 3 SRS 3.7.1 |
| 2026-09-28 | 1.5 | FE-01 client registration persistence defect fix | M | Fixed `POST /api/v1/auth/register` returning 500 (the audit insert referenced the new user before the Hibernate flush) and recorded the passing FE-01 self-registration persistence gate; workbook case IDs, sheet totals, and statistics unchanged. | Backend `ClientRegistrationApiIntegrationTest`, `ClientRegistrationServiceTest`; `.\mvnw.cmd verify` 165/165; Report 3 SRS 3.2 |
| 2026-09-28 | 1.6 | FE-01 admin user creation persistence defect fix | M | Fixed `POST /api/v1/platform/users` returning 500 (same audit-before-flush cause) and recorded the passing FE-01 admin-creation persistence gate; workbook case IDs, sheet totals, and statistics unchanged. | Backend `AdminUserApiIntegrationTest`, `AdminUserServiceTest`; `.\mvnw.cmd verify` 167/167 |
| 2026-09-29 | 1.7 | WF1 proposal flow cases added | A | Added `WF1-011`-`WF1-019` for asset review, schedule-proposal generation/review/selection, document-upload rules, the due-cycle event, and the negative scope sweep; recounted Feature 1 to 17 cases and the total to 24. | Report 3 SRS 3.3; `project-reference/business-flows.md`; backend `mvnw verify`; `fe-02-asset-registry-inspection-schedule.md`, `fe-03-inspection-request-work-assignment.md`, `test-statistics.md` |
