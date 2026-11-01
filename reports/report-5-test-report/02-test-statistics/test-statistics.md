# Test Statistics sheet source

This table mirrors the `Test Statistics` sheet. Keep the workbook's summary
formulas and labels; update the values from the feature files after each test
round.

## Project metadata

| Field | Value |
| --- | --- |
| Project Name | SmartDroneInspection |
| Project Code | GFA26SE139 |
| Test round | 2026-11-01 Synchronized 65-Case Test Suite across 8 Features FE-01 to FE-08 (2 features per team member, mapped 1-to-1 to Feature 1 to Feature 8). Backed by automated backend JUnit/Testcontainers tests (migrations V1–V17), frontend Vitest suites, and Flutter mobile tests. |
| Last updated | 2026-11-01 (Report 5 version 2.0; 65 cases across 8 feature sheets: 60 Passed, 0 Failed, 5 Pending, 92.31% overall / 93.75% baseline coverage) |

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
