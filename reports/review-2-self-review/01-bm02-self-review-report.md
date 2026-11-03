---
title: "SWP490 Review 2 - BM02 SRS/SDD Self-Review Report"
document_type: review2-bm02
version: "2.0"
date: "2026-11-01"
project_code: "GFA26SE139"
group_name: "FA26SE112"
---

# I. BM02 – SRS / SDD Self-Review & Cross-Check Report

## 1. Review Metadata & Peer Review Matrix

| Field | Value |
| --- | --- |
| **Project Code / Group** | `GFA26SE139` / `FA26SE112` — **SmartDroneInspection (SDI)** |
| **Review Date & Baseline** | `2026-11-01` — Synchronized 5-Role Platform Inspection Service Baseline (`V1`–`V17`, 8 Features `FE-01`–`FE-08`) |
| **Documents Cross-Checked** | 1. `SWP490_GFA26SE139_R2_Registration.docx` (Registration v2.0 + `BM03`)<br>2. `Report3_Software Requirement Specification.docx` (`FE-01`–`FE-08`, `16` functions, `UC-01`–`UC-30`, `BR-01`–`BR-49`)<br>3. `Report4_Software Design Document.docx` (System Design, `36`-table DB Design `V1`–`V17`, `11` State Machines, Detailed Design `3.1`–`3.8`)<br>4. `Report5_Test Report.xlsx` (`65` Test Cases across `Feature 1`–`Feature 8`) & `Report3_Project Tracking.xlsx`<br>5. Live Code Repositories: `SmartDroneInspection-backend`, `SmartDroneInspection-frontend`, `SmartDroneInspection-mobile` |

**Peer Review Assignment Matrix (Non-Author Cross-Check)**:

| Member (Author of Owned Scope) | Owned Features & Workflows (2 Features / Member) | Primary Peer Reviewer (SRS / SDD / Code / Report 5) | Secondary Reviewer |
| --- | --- | --- | --- |
| **Trần Hoàng Trung Hiếu** (`SE184212`) | `FE-02`, `FE-03` (`WF-01`) | **Trần Tùng Bách** (`SE180220`) | **Phùng Trung Quốc** (`SE170027`) |
| **Phùng Trung Quốc** (`SE170027`) | `FE-04`, `FE-05` (`WF-02`) | **Trương Thái Như** (`SE180082`) | **Trần Hoàng Trung Hiếu** (`SE184212`) |
| **Trần Tùng Bách** (`SE180220`) | `FE-01`, `FE-06` (`WF-03`) | **Trần Hoàng Trung Hiếu** (`SE184212`) | **Trương Thái Như** (`SE180082`) |
| **Trương Thái Như** (`SE180082`) | `FE-07`, `FE-08` (`WF-04`) | **Phùng Trung Quốc** (`SE170027`) | **Trần Tùng Bách** (`SE180220`) |

---

## 2. Summary of Cross-Check Findings & Resolution Status

| Severity | Found | Fixed Before Submission | Planned with Owner & Deadline | Open / Unassigned |
| :---: | :---: | :---: | :---: | :---: |
| **Critical** | `2` | `2` (`100%`) | `0` | `0` |
| **High** | `5` | `5` (`100%`) | `0` | `0` |
| **Medium** | `3` | `3` (`100%`) | `0` | `0` |
| **Total** | **`10`** | **`10` (`100%`)** | **`0`** | **`0`** |

---

## 3. Detailed Self-Review Findings Log (BM02)

| ID | Category (SRS / SDD / Code / Test) | Severity | Description of Mismatch / Issue Found During Self-Review | Resolution & Evidence (Fixed vs. Planned) | Owner |
| :---: | --- | :---: | --- | --- | --- |
| **`SR-01`** | **Code vs. Docs (5-Role Platform Service Cutover)** | **Critical** | Earlier reports described self-service Enterprise Subscriptions (PayPal) and Platform Drone Pool Leasing, whereas live code (`V7`–`V14`) transitioned to the **5-Role Platform Inspection Service model** (`ADMIN`, `MANAGER`, `CUSTOMER`, `INSPECTOR`, `MAINTENANCE_ENGINEER`) with Inspector onboarding, Inspector-owned Drone 3-doc registration, Service Requests/Quotes/Signed Contracts, and **PayOS (VietQR)** payment. | **FIXED (`2026-11-01`)**: Synchronized Reports 1, 2, 3, 4, 5, Project Tracking, and Review 2 pack with the 5-Role Platform Inspection Service model and retired Subscription/Drone Leasing from the 8 core features. | **Trần Hoàng Trung Hiếu** |
| **`SR-02`** | **Scope Consolidation (12 Features -> 8 Features)** | **Critical** | The initial 12-feature breakdown spread 3 features per member across 12 sheets in Report 5, whereas team governance standardized on **8 cohesive features (`FE-01` to `FE-08`, 2 features per member)** mapped 1-to-1 to `Feature 1`–`Feature 8`. | **FIXED (`2026-11-01`)**: Consolidated SRS (`§3.2`–`§3.9`), SDD (`§3.1`–`§3.8`), Report 1 (`§6.1`), Report 2 WBS & RACI (`16` functions), and Report 5 (`Feature 1`–`Feature 8`) into the 8-feature structure. | **Trần Hoàng Trung Hiếu** |
| **`SR-03`** | **Code vs. SDD (6-State Inspection & Abort Re-Dispatch)** | **High** | Migration `V15` and PR `#118` streamlined `InspectionStatus` to 6 states (`SCHEDULED`, `IN_PROGRESS`, `FIELD_COMPLETED`, `UNDER_REVIEW`, `COMPLETED`, `CANCELLED`), removed `READY_FOR_FLIGHT` and `REPORT_DRAFT`, and replaced session `postpone` with `Abort` + Manager re-dispatch (`PUT /schedule`, `PUT /assignment`, `POST /cancellation`). | **FIXED (`2026-11-01`)**: Updated SRS `FE-06`, SDD `§2.1.1` & `§3.5`, and Mermaid state/sequence diagrams to reflect the 6-state lifecycle and abort re-dispatch flow. | **Trần Tùng Bách** |
| **`SR-04`** | **Code vs. SDD (5-State Auto-Compiled Report & AI Summary)** | **High** | Migrations `V16` and `V17` dropped manual `content_snapshot` notes and removed `DRAFT`/`AUTHOR_VERIFIED` from `ReportStatus`, auto-compiling reports to `SUBMITTED` on tab visit alongside `GET /ai-summary` (`ReportAiSummaryCard`). | **FIXED (`2026-11-01`)**: Updated SRS `FE-06 (§3.7.2)`, SDD `§2` & `§3.6`, and Mermaid diagram `34` to reflect the 5-state auto-compiled report lifecycle (`SUBMITTED`, `RETURNED`, `APPROVED`, `PUBLISHED`, `SUPERSEDED`). | **Trần Tùng Bách** |
| **`SR-05`** | **Code vs. Docs (Photo & Streaming MP4 Video Evidence)** | **High** | Backend (`PR #107`), Web (`AuthenticatedMedia` HTML5 video + findings preview chips), and Mobile (`PR #21` `file_picker` streaming upload) added `video/mp4` evidence support alongside photos, plus automatic Vision LLM fallback when `YOLO11` returns empty detections (`ac50d56`). | **FIXED (`2026-11-01`)**: Updated SRS `FE-06 (§3.7.1)`, SDD `§3.6`, and Report 5 (`Feature 6`, including `WF3-017`) to document photo/MP4 evidence intake and Vision LLM fallback. | **Trần Tùng Bách** |
| **`SR-06`** | **Code vs. Docs (PayOS VietQR Payment & Finance Settings)** | **High** | Migrations `V12` and `V13` (`PR #113`, `#119`) added `inspection_finance_settings` (`commission_rate`, `vat_rate`, `tncn_rate`), Customer report acceptance (`PAYMENT_DUE`), PayOS VietQR payment link creation, and HMAC-SHA256 webhook settlement (`PAID`, gating PDF downloads with `402 Payment Required`). | **FIXED (`2026-11-01`)**: Documented PayOS VietQR settlement and finance settings across SRS `FE-06`, SDD `§2` & `§3.4`/`§3.6`, and Report 5 (`Feature 6`). | **Trần Tùng Bách** |
| **`SR-07`** | **Code vs. Docs (MF4 RAG Norms, Compliance Audit & 3-Way Re-inspection)** | **High** | Migrations `V10` and `V14` (`PR #107`, `#112`, `#117`) added 1-click RAG `initialTasks`, RAG cost norms (`POST /suggest-estimate`), 1-click batch work-log verification (`POST /work-logs/batch-verify`), smart `GET /reports/auto-draft`, RAG `GET /acceptance-compliance`, and the 3-step/3-way Re-inspection defect verification loop (`reinspection_defect_verifications`). | **FIXED (`2026-11-01`)**: Updated SRS `FE-07` & `FE-08 (§3.8–§3.9)`, SDD `§2` & `§3.7–§3.8`, and Report 5 (`Feature 7` & `Feature 8`) with full API and schema traceability. | **Trương Thái Như** |
| **`SR-08`** | **Code vs. Docs (Google OAuth2 & Decoupled `/users/me` Profile)** | **Medium** | Backend (`7cc2534`, `e23d23f`) and Mobile (`PR #22`) added Google OAuth2 (`/api/v1/auth/oauth2/authorize/google`, Web callback & `smartdrone://auth` deep link) and moved profile/pilot-license endpoints to `UserProfileController` (`/api/v1/users/me`). | **FIXED (`2026-11-01`)**: Updated SRS `FE-01 (§3.2)` and SDD `§3.1` to reflect Google OAuth2 and `/api/v1/users/me`. | **Trần Tùng Bách** |
| **`SR-09`** | **Code vs. Docs (Recurring Contract Inheritance D2 & Occurrence Dispatch)** | **Medium** | Backend (`ContractWorkflowService`) inherits the parent signed contract across all recurring occurrences (`Decision D2`), simplifying commercial flow without re-uploading contracts per occurrence. | **FIXED (`2026-11-01`)**: Documented Decision D2 in `FE-04` and `FE-05` (MF2 contract request-to-assignment lifecycle). | **Phùng Trung Quốc** |
| **`SR-10`** | **Report 5 Workbook Layout (12 Sheets -> 8 Sheets)** | **Medium** | `Report5_Test Report.xlsx` exporter and test suite needed to be updated from 12 feature sheets (`Feature 1`–`Feature 12`) to 8 feature sheets (`Feature 1`–`Feature 8`) matching `FE-01`–`FE-08` and including all 65 test cases. | **FIXED (`2026-11-01`)**: Consolidated `03-features/` into `fe-01`–`fe-08.md`, updated `test-case-list.md` & `test-statistics.md`, and updated `export_report5.py` and `test_feature_sheets.py` / `test_report5.py`. | **Trần Hoàng Trung Hiếu** |

---

## 4. SWP490 Review 2 Compliance Checklist (Self-Audit Verification)

| Check # | Review 2 Mandatory Requirement | Verification Evidence in Package | Status |
| :---: | --- | --- | :---: |
| **C-01** | Registration Form updated to v2.0/v3.0 with `BM03` Record of Changes | `01-registration-form.md` & `02-bm03-record-of-changes.md` (`8` change rows traced to SRS/SDD). | **PASS** |
| **C-02** | SRS has `8` cohesive Mandatory Features (`FE-01`–`FE-08`), `2` per member, with Normal + Exception flows, Validation, Business Rules & UI-to-API mapping | Report 3 SRS `§3.2`–`§3.9` (`16` sub-functions, `30` Use Cases, `49` Business Rules). | **PASS** |
| **C-03** |SRS has `6` locked Non-Functional Requirements (`NFR-01`–`NFR-06`) with numerical thresholds and verification links | Report 3 SRS `§4.2.1` (`NFR-01` API `<=500ms`, `NFR-02` YOLO11 `<=10s`, `NFR-03` Tenant Isolation, `NFR-04` Auth Lockout/Rate Limit, `NFR-05` SHA-256 PDF Immutability, `NFR-06` Modulith + `>=80%` JaCoCo). | **PASS** |
| **C-04** | SDD includes System Context, Component/Module Diagram, Deployment Topology, ERD (`36` tables `V1`–`V17`), `11` State Machines, and Class/Sequence/Activity diagrams for all `8` Features & `4` Main Workflows | Report 4 SDD `§1.1–§1.3`, `§2.1–§2.2`, `§3.1–§3.8`. | **PASS** |
| **C-05** | Test Report (`Report5_Test Report.xlsx`) contains all `65` test cases routed across `Feature 1`–`Feature 8` (`2` sheets per member) with `>= 90%` pass rate | `65` TCs (`60 Passed = 92.31%`, `0 Failed`, `5 Pending`). | **PASS** |
| **C-06** | `BM04` Commitment tables reconcile 100% between By-Workflow (`WF-01`–`WF-04`) and By-Member (`Hiếu`, `Quốc`, `Bách`, `Như`) | `02-appendix-a-and-bm04-commitment.md` (`§9.4` Table A = Table B = `65` TCs, `8` Demo Scenarios, `5` Action Items). | **PASS** |
| **C-07** | Zero unowned features, zero orphan tables/endpoints, and zero open Critical/High defects | Verified via automated Python OOXML test suite (`tools/tests/test_*.py`). | **PASS** |
