---
title: "Report 4 - Record of Changes"
document_type: report4-sdd-section
weight: 5
source: "report4-software-design-document.docx"
---

# I. Record of Changes

| Date | A* M, D | In charge | Change Description |
| --- | --- | --- | --- |
| 27 Oct 2026 | A | Project Team | Version 1.0: Initial release of the Software Design Document (SDD) for SmartDroneInspection. |
| 31 Oct 2026 | M | Project Team | Version 1.1: Streamlined Inspection lifecycle to 6 canonical states (V15), removed field session postponement in favor of abort-and-dispatch (PR #118), and streamlined InspectionReport lifecycle to 5 states with auto-compilation (V16, V17). |
| 01 Nov 2026 | M | Project Team | Version 2.0: Synchronized SDD with the 5-role Platform Inspection Service architecture (ADMIN, MANAGER, CUSTOMER, INSPECTOR, MAINTENANCE_ENGINEER), narrowed Detailed Design to 8 features (FE-01 to FE-08), added migrations V7–V14 (Customer airspace onboarding, Partner Inspector/Drone 3-doc review, Service Requests/Quotes/Chat/Signed Contracts, PayOS VietQR payment, Finance Settings, and 3-way Re-inspection defect verifications), and documented MF4 RAG cost norms and acceptance compliance auditing. |
| 01 Nov 2026 | M | Project Team | Version 2.1: Updated Database Design ERD and table descriptions to the V25 target schema: removed retired subscription/PayPal, drone-lease, internal recurring-schedule and Inspector partner-application entities; added `inspector_profiles`, `otp_challenges`, and `inspector_flight_logs`; reflected retained/dropped column decisions and the VND-only quote schema. |
| 02 Nov 2026 | M | Project Team | Version 2.2: Synchronized System and Detailed Design with current implementation: documented InspectorProfile and consolidated OTP flows, platform-provisioned Inspectors, recurring ServiceRequest occurrence materialization, VND persistence with legacy USD-compatible API input mapping and VND-only PayOS, parent-request signed contracts, manual and automatic report authoring actions separated from persisted states, absence of a current PDF 402 guard, automatic PAID payout for assigned Inspectors, accurate maintenance compliance checks, and reinspection completion-report reinstatement. Corrected Database Design ERD fields, distinct work-order user FKs, payout behavior, and qualified selected composite tenant-FK coverage. Canonical standalone Mermaid ERD source remains stale pending regeneration; generated PNGs and manifest were not regenerated. |
| 03 Nov 2026 | M | Project Team | Version 2.3: Aligned the inspection-report lifecycle and reviewer flow with direct publication from SUBMITTED, removing the intermediate APPROVED state. |
|  |  |  |  |

*A - Added M - Modified D - Deleted
