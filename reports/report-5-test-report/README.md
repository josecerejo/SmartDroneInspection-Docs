# Report 5 — Test Report working folder

This folder separates the contents of the supplied `Report5_Test Report.xlsx`
template so the team can update test cases without repeatedly rebuilding the
whole workbook.

**Scope (updated 2026-11-01):** The synchronized test suite tracks **65 cases** across
**8 product features (`FE-01` to `FE-08`, 2 features per team member)** mapped 1-to-1 to
8 feature sheets (`Feature 1` to `Feature 8`): Round 1 historical totals remain **60 `Passed`**, **0 `Failed`**, and **5 `Pending`**
(`92.31%` overall / `93.75%` baseline pass rate). All cases are aligned with the
5-Role Platform Inspection Service model (`ADMIN`, `MANAGER`, `CUSTOMER`,
`INSPECTOR`, `MAINTENANCE_ENGINEER`). For the V25 cleanup, focused unit/frontend checks ran, while Testcontainers/PostgreSQL V25 migration verification remains pending until Docker is available; the full frontend suite currently has 14 failing tests (`WorkforcePage.test.tsx` and `RegisterPage.test.tsx`).

The original workbook template remains unchanged; generated copies contain eight
feature sheets (`Feature 1`–`Feature 8`).

## Naming layers and mapping

The supplied template has two feature sheets (`Feature 1`, `Feature 2`). Generated
workbooks extend it to eight feature sheets (`Feature 1`–`Feature 8`), one per
Report 3 feature (`FE-01`–`FE-08`). Sheet `Feature N` contains SRS feature `FE-0N`.

| Layer | Meaning | Example |
| --- | --- | --- |
| Workbook sheet | Generated Report 5 grouping; one sheet per FE | `Feature 6` |
| SRS feature | Product capability from Report 3 | `FE-06 — Evidence Intake, YOLO11 Detection, Auto-Compiled Report & PayOS` |
| WF test ID | Business-flow traceability ID | `WF3-005` |

## Source of truth and template rule

- `template/Report5_Test Report.xlsx` is an unchanged copy of the supplied
  workbook. Do not edit this copy to add new sections or rename sheets.
- Exactly eight FE-specific Markdown files in `03-features/` are the editable
  feature sources (`fe-01` through `fe-08`). Keep test case IDs stable when a
  case is reworded or re-tested.
- When the report is ready for submission, use the exporter to produce a copy
  of the official template with eight generated feature sheets. Read
  [template-layout.md](template-layout.md) first: it carries the exact cell
  addresses, the per-sheet summary block, and the template defects that will
  otherwise corrupt an export.

## Folder map

| Folder/file | Workbook area | Purpose |
| --- | --- | --- |
| `00-cover/` | `Cover` | Project metadata and record of changes. |
| `01-test-cases/` | `Test Cases` | The index of all 65 cases and their preconditions. |
| `02-test-statistics/` | `Test Statistics` | Module totals, coverage, and execution summary across `Feature 1`–`Feature 8`. |
| `03-features/fe-01-authentication-access-control.md` | `Feature 1` sheet | `FE-01` (`WF1-001`–`WF1-005`: 5 cases, Owner: Trần Tùng Bách). |
| `03-features/fe-02-workforce-subscription-management.md` | `Feature 2` sheet | `FE-02` (`WF1-006`–`WF1-016`: 11 cases, Owner: Trần Hoàng Trung Hiếu). |
| `03-features/fe-03-asset-drone-fleet-management.md` | `Feature 3` sheet | `FE-03` (`WF1-017`–`WF1-021`: 5 cases, Owner: Trần Hoàng Trung Hiếu). |
| `03-features/fe-04-recurring-schedule-notifications.md` | `Feature 4` sheet | `FE-04` (`WF2-001`–`WF2-005`: 5 cases, Owner: Phùng Trung Quốc). |
| `03-features/fe-05-mission-dispatch-airspace-advisory.md` | `Feature 5` sheet | `FE-05` (`WF2-008`–`009`, `011`–`012`, `015`–`020`, `WF3-009`: 11 cases, Owner: Phùng Trung Quốc). |
| `03-features/fe-06-flight-readiness-field-execution.md` | `Feature 6` sheet | `FE-06` (`WF3-001`–`008`, `WF3-010`, `012`, `016`, `017`: 12 cases, Owner: Trần Tùng Bách). |
| `03-features/fe-07-operational-dashboard-schedule-calendar.md` | `Feature 7` sheet | `FE-07` (`WF4-001`–`WF4-011`: 11 cases, Owner: Trương Thái Như). |
| `03-features/fe-08-evidence-ai-defect-detection.md` | `Feature 8` sheet | `FE-08` (`WF4-012`–`WF4-016`: 5 cases, Owner: Trương Thái Như). |
| `template-layout.md` | All sheets | Exact sheet, column, and section reference. |
| `template/Report5_Test Report.xlsx` | All sheets | Original-format workbook copy. |

The `FE-01`–`FE-08` codes and their Report 3 sections are:

| FE | Report 3 § | Report 3 feature title | Owner |
| --- | --- | --- | --- |
| `FE-01` | `3.2` | Authentication, Google OAuth2 & 5-Role Access Control | Trần Tùng Bách (`SE180220`) |
| `FE-02` | `3.3` | Partner Onboarding, Workforce, Asset & Inspector Drone Registry | Trần Hoàng Trung Hiếu (`SE184212`) |
| `FE-03` | `3.4` | Recurring Schedules, Contract Occurrences & Outbox Notifications | Trần Hoàng Trung Hiếu (`SE184212`) |
| `FE-04` | `3.5` | Service Requests, Quotations & Commercial Order Chat | Phùng Trung Quốc (`SE170027`) |
| `FE-05` | `3.5` | Signed Contract Evidence & Partner Occurrence Dispatch | Phùng Trung Quốc (`SE170027`) |
| `FE-06` | `3.7` | Evidence Intake, YOLO11 Detection, Auto-Compiled Report & PayOS | Trần Tùng Bách (`SE180220`) |
| `FE-07` | `3.8` | Maintenance Work Orders, RAG Scope/Norms Advisor & Repair Execution | Trương Thái Như (`SE180082`) |
| `FE-08` | `3.9` | Completion Report, 3-Way Re-inspection Verification & Cost Closure | Trương Thái Như (`SE180082`) |

Each FE file's H1 carries the Report 3 title. The filenames keep their
original wording and are left alone so existing links remain stable.

## Editing workflow

1. Add or update the case in its owning FE-specific file first (`fe-01`–`fe-08`).
2. Keep the existing ID format (`WF1-001`–`WF4-016`) stable.
3. Mirror every case in `01-test-cases/test-case-list.md`.
4. Record execution only in the matching Round 1, Round 2, or Round 3 cell.
   Use only `Passed`, `Failed`, `Pending`, or `N/A`.
5. Update the corresponding module row and totals in
   `02-test-statistics/test-statistics.md`. `Module code` must match the
   feature sheet's `Feature` name (`B2`).
6. Before exporting, check that the number of cases, IDs, statuses, dates, and
   testers agree across all Markdown files and the workbook.

## Generate and verify a workbook copy

Run from the docs repository root:

```powershell
python -I tools/export_report5.py
python -I -m unittest discover -s tools/tests -p "test_*.py" -v
```
