---
title: "Report 3 - Record of Changes"
document_type: report3-srs-section
weight: 5
source: "report3-software-requirement-specification.docx"
---

# I. Record of Changes

| Date | A* M, D | In charge | Change Description |
| --- | --- | --- | --- |
| 21 Sep 2026 | A | Project Team | Initial SmartDroneInspection SRS baseline aligned with the approved WF1-WF4 business flow and the five current roles. |
| 21 Sep 2026 | M | Project Team | Added Client organization self-registration and separate inspection and maintenance post-service billing milestones. |
| 24 Sep 2026 | M | Project Team | Standardized successful JSON API bodies on `ApiResponse<T>` while preserving HTTP statuses, bodyless `204` responses, binary streams, and RFC 9457 error responses. |
| 24 Sep 2026 | M | Project Team | Clarified the assigned-inspector checklist read API and Web/Mobile evidence source contract; documented optional YOLO fallback and persisted Client report-decision audit with the separate billing handoff. |
| 25 Sep 2026 | M | Project Team | Specified on-demand AI narrative drafting with human review and inspection lifecycle completion to COMPLETED on Client acceptance. |
| 26 Sep 2026 | M | Project Team | Documented last-write-wins between AI draft regeneration and narrative edits, and recorded the matching Report 5 note. |
| 26 Sep 2026 | M | Project Team | Recorded AI draft model provenance on the version snapshot and moved the narrative length limit to the `REPORT_NARRATIVE_MAX_CHARS` configuration key in SRS 3.7.1. |
| 28 Sep 2026 | M | Hiếu | Revised FE-02: Client asset registration now enters `PENDING_REVIEW`, the Service Manager approves the asset and reviews platform-generated schedule proposals, and the Client selects one proposal to create the active schedule. Added per-category suggested inspection frequencies, asset document upload rules, and the revised periodic-request generation wording. |
| 29 Sep 2026 | M | Quốc | Revised WF2 and FE-03 to periodic-only flow: Client declares inspection defaults (scope, priority, site-access constraints, contact) during asset registration; system automatically generates periodic requests on due cycle with inherited defaults and notifies Client; Client auto-accepts by default or may submit a cancellation request; removed manual Client request completion step. |

*A - Added M - Modified D - Deleted
