# Test Statistics sheet source

This table mirrors the `Test Statistics` sheet. Keep the workbook's summary
formulas and labels; update the values from the feature files after each test
round.

## Project metadata

| Field | Value |
| --- | --- |
| Project Name | SmartDroneInspection |
| Project Code | GFA26SE139 |
| Test round | Historical Round 1 inventory: 65 retained case IDs across 8 features FE-01 to FE-08 (2 features per team member, mapped 1-to-1 to Feature 1 to Feature 8). Round 1 and Round 2 figures below are historical only. Round 3 has two verified cases (WF3-006 and WF3-016); all other Round 3 cases remain Pending. Current V25-target verification is Pending; the latest recorded PostgreSQL/Testcontainers attempt was blocked before assertions because Docker was unavailable on 2026-11-01. |
| Last updated | 2026-11-03 (targeted Round 3 verification: WF3-006 and WF3-016 Passed; all other Round 3 cases remain Pending. Historical Round 1 totals remain 65 IDs: 60 Passed, 0 Failed, 5 Pending; 92.31% overall / 93.75% of the 64-case historical baseline). |

### Historical Round 1 summary (65 retained IDs)

The following status/count table preserves the historical Round 1 worksheet totals only. It includes legacy recurrence scenarios WF1-018, WF1-019, and WF1-021 (which are excluded from current V25 target coverage) and implementation-specific WF3-017. Totals and pass-rate formulas must not be read as current V25 results. Current V25 verification: **Pending**, blocked before migration assertions when Docker was unavailable on 2026-11-01.

## Module summary

| No | Module code | Passed | Failed | Pending | N/A | Number of test cases |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | Authentication, Google OAuth2 & 5-Role Access Control | 5 | 0 | 0 | 0 | 5 |
| 2 | Partner Onboarding, Workforce, Asset & Inspector Drone Registry | 10 | 0 | 1 | 0 | 11 |
| 3 | Recurring Schedules, Contract Occurrences & Outbox Notifications | 5 | 0 | 0 | 0 | 5 |
| 4 | Service Requests, Quotations, Contracts, Dispatch & Airspace Map | 5 | 0 | 0 | 0 | 5 |
| 5 | Flight Permit Gate, Field Execution, Dashboard & Calendar | 10 | 0 | 1 | 0 | 11 |
| 6 | Evidence Intake, YOLO11 Detection, Auto-Compiled Report & PayOS | 10 | 0 | 2 | 0 | 12 |
| 7 | Maintenance Work Orders, RAG Scope/Norms Advisor & Repair Execution | 10 | 0 | 1 | 0 | 11 |
| 8 | Completion Report, 3-Way Re-inspection Verification & Cost Closure | 5 | 0 | 0 | 0 | 5 |
| **Subtotal** |  | **60** | **0** | **5** | **0** | **65** |
| **Review 2 baseline** |  | **60** | **0** | **4** | **0** | **64** |
| **Implementation-specific pending** |  | **0** | **0** | **1** | **0** | **1** |
