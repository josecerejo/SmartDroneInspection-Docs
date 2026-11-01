---
title: "Report 3 - Record of Changes"
document_type: report3-srs-section
weight: 5
source: "report3-software-requirement-specification.docx"
---

# I. Record of Changes

| Date | A* M, D | In charge | Change Description |
| --- | --- | --- | --- |
| 27 Oct 2026 | A | Project Team | Version 1.0: Initial release of the Software Requirement Specification (SRS) for SmartDroneInspection. |
| 27 Oct 2026 | M | Project Team | Clarified AI defect detection fallback: when YOLO11 returns no detections, use the configured vision-capable LLM before reporting zero candidates. |
| 01 Nov 2026 | M | Project Team | Version 2.0: Synchronized with the 5-role Platform Inspection Service model (ADMIN, MANAGER, CUSTOMER, INSPECTOR, MAINTENANCE_ENGINEER), narrowed scope to 8 product features (FE-01 to FE-08), replaced subscription/leasing with MF1 partner/airspace onboarding and MF2 service requests, VND quotes, offline contracts, and PayOS VietQR checkout, streamlined MF3 to 6 inspection states and 5 auto-compiled report states with AI executive summaries, and added MF4 3-way re-inspection defect verification and RAG norms/compliance auditing. |
| 01 Nov 2026 | M | Project Team | Version 2.1: Aligned functional requirements with V25 implementation: Platform-provisioned Inspectors with separate `inspector_profiles` replace persisted Inspector applications; `otp_challenges` consolidates OTP purposes; recurring requests use `service_request_occurrences` while the separate internal recurring-schedule engine is retired; service-request quotes use VND persistence. Preserved historical requirements separately from verified implementation evidence. |
|  |  |  |  |
|  |  |  |  |

*A - Added M - Modified D - Deleted
