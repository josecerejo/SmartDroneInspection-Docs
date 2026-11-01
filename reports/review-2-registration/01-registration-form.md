---
title: "SWP490 Review 2 - Registration Form (v2.0)"
document_type: review2-registration
version: "2.0"
date: "2026-11-01"
project_code: "GFA26SE139"
group_name: "FA26SE112"
---

# I. Capstone Project Registration Form (Updated v2.0 for Review 2)

## 1. Capstone Project Name
- **English Name**: **SmartDroneInspection: AI-powered Infrastructure Inspection Management Platform**
- **Vietnamese Name**: **Nền tảng Quản lý Dịch vụ Kiểm tra và Bảo trì Hạ tầng bằng Drone ứng dụng Trí tuệ Nhân tạo**
- **Abbreviation**: **SDI**
- **Project Code**: `GFA26SE139` | **Group Name**: `FA26SE112`

## 2. Project Team & Supervisors

### 2.1 Supervisors (Mentors)

| Full Name | Title / Department | Email | Phone | Role |
| --- | --- | --- | --- | --- |
| **Phạm Minh Trí** | Lecturer, Software Engineering Dept., FPT University HCMC | `tripm14@fpt.edu.vn` | — | Primary Supervisor |
| **Đặng Ngọc Minh Đức** | Lecturer, Software Engineering Dept., FPT University HCMC | `ducdnm2@fpt.edu.vn` | — | Co-Supervisor |

### 2.2 Student Members

| No. | Full Name | Student Code | Email | Phone | Role & Owned Features (`2` Features / Member) |
| :---: | --- | :---: | --- | :---: | --- |
| 1 | **Trần Hoàng Trung Hiếu** | `SE184212` | `hieuthtse184212@fpt.edu.vn` | `0963832382` | **Team Leader** — Owns `FE-02`, `FE-03` (`WF-01`) |
| 2 | **Phùng Trung Quốc** | `SE170027` | `quocptse170027@fpt.edu.vn` | `0896986551` | **Member** — Owns `FE-04`, `FE-05` (`WF-02`) |
| 3 | **Trần Tùng Bách** | `SE180220` | `bachttse180220@fpt.edu.vn` | `0378351050` | **Member** — Owns `FE-01`, `FE-06` (`WF-03`) |
| 4 | **Trương Thái Như** | `SE180082` | `nhuttse180082@fpt.edu.vn` | `0328416716` | **Member** — Owns `FE-07`, `FE-08` (`WF-04`) |

---

## 3. Capstone Project Description

### 3.1 Business Context & Problem Statement
Civil, industrial, and energy infrastructure operators (highway bridges, commercial buildings, transmission towers, solar farms, wind turbines) require periodic structural inspections and standards-compliant corrective maintenance. In practice, commercial service requests, quotations, signed paper contracts, partner drone pilot scheduling, Vietnam aviation compliance checks (Decision No. 18/2020/QĐ-TTg & Decree No. 288/2025/NĐ-CP), field flight logs, aerial imagery/video, defect analysis, formal PDF reporting, payment settlement, and maintenance work order cost reconciliation are fragmented across spreadsheets, chat apps, and manual file shares. This fragmentation prevents cross-customer schedule conflict detection, breaks traceability between physical structural defects and geotagged aerial evidence, and leaves maintenance budgets and post-repair re-inspections unaudited.

**SmartDroneInspection (SDI)** solves this by providing an end-to-end **Platform-Managed Infrastructure Inspection & Corrective Maintenance Service Platform** that unifies four core operational stages (`MF1` to `MF4` / `WF-01` to `WF-04`):
1. **MF1 — Partner Inspector Onboarding, Customer Airspace Registration, Asset & Owned-Drone Registry**: Customer self-registration with initial asset evaluation against Vietnam No-Fly Zones (`NO_FLY_ZONE` rejected, `RESTRICTED_ZONE` routed to `PROSPECT_CUSTOMER` review, `CLEAR_ZONE` activated), Partner Inspector onboarding with remote pilot license and offline partner contract verification (no drone required at signup), Inspector-owned drone registration with 3 mandatory documents (`REGISTRATION`, `OWNERSHIP`, `INSPECTION`), customer asset catalog with standardized checkpoints, and Customer Maintenance Engineer provisioning.
2. **MF2 — Service Requests, VND/USD Quotations, Order Chat, Signed Contracts & Partner Dispatch**: One-time and recurring customer Service Requests (`OPEN`), in-context Order Chat negotiation, versioned VND/USD Quotations bound to a partner Inspector and their owned drone (`QUOTED`), Quote Acceptance (`ACCEPTED`), offline Signed Paper Contract scan upload (`CONTRACT_SIGNED`, inherited across recurring occurrences per Decision D2), and cross-organization conflict-checked partner occurrence dispatch (`ASSIGNED` -> `Inspection: SCHEDULED`).
3. **MF3 — Flight Permit Gate, Field Execution, Photo/MP4 Evidence, YOLO11 Detection, Auto-Compiled Report & PayOS Settlement**: Aviation flight permit upload and pilot license readiness guard (`hasFlightPermit()`), Web/Flutter Mobile 2-outcome field flight sessions (`IN_PROGRESS` -> `FIELD_COMPLETED` or `ABORTED` with automatic reversion to `SCHEDULED` and manager reschedule/reassign/cancel dispatch), photo and streaming `video/mp4` evidence intake into MinIO, `YOLO11` + Vision LLM fallback defect detection, findings preview chips & baseline confirmation, 6-state Inspection & 5-state auto-compiled Report submission (`SUBMITTED`, mission `UNDER_REVIEW`), AI Executive Summary card, independent `MANAGER` review and immutable SHA-256 PDF publication (`PUBLISHED`, mission `COMPLETED`), Customer report acceptance (`PAYMENT_DUE`), and **PayOS (VietQR)** payment settlement (`PAID`, unlocking PDF download and partner payout eligibility).
4. **MF4 — Maintenance Work Orders, RAG Scope/Norms Advisor, Field Repair, 3-Way Re-inspection & Cost Closure**: Forwarded defect triage into `MaintenanceWorkOrder`s, `pgvector` RAG repair scope advisor (`TCVN`/`EN`/`ISO`) with 1-click `initialTasks` provisioning, team role allocation, RAG Cost & Norms Estimator (`suggest-estimate`), independent Customer budget & Change Order approval, field repair execution with 1-click Team Lead batch work-log verification (`batch-verify`), smart auto-drafted Maintenance Completion Report (`auto-draft`), RAG Technical Acceptance Compliance Audit (`acceptance-compliance`), automated 3-step/3-way Re-inspection defect verification loop (`RESOLVED`, `UNRESOLVED`, `INCONCLUSIVE`), independent Customer acceptance, baseline-to-actual cost reconciliation, and Work Order closure (`CLOSED`).

### 3.2 Primary Actors & Five-Role Governance Model
The platform enforces strict role-based and zone-scoped access control across **5 human login roles** in **3 operational zones** (`PLATFORM`, `INSPECTOR_PARTNER`, `CUSTOMER_ORGANIZATION`):
- **Platform Admin (`ADMIN` — `ActorZone.PLATFORM`)**: Governs internal platform accounts (`MANAGER`, `ADMIN`), global asset categories, restricted-airspace prospective customer approvals, partner inspector & 3-document drone approvals, finance settings (`commission_rate`, `vat_rate`, `tncn_rate`), and system-wide security audit logs.
- **Platform Manager (`MANAGER` — `ActorZone.PLATFORM`)**: Governs partner Inspector and owned-drone registries, customer Service Requests, Order Chat negotiation, VND/USD Quotations, signed paper contract uploads, cross-organization partner dispatch, abort re-dispatch (`Reschedule`, `Reassign`, `Cancel`), independent inspection report review/publication (`PUBLISHED`), and partner payouts.
- **Partner Inspector (`INSPECTOR` — `ActorZone.INSPECTOR_PARTNER`)**: Independent licensed drone pilot (`organization_id = NULL`) who applies with a remote pilot license (drone optional at signup), registers owned drones with 3 documents (`REGISTRATION`, `OWNERSHIP`, `INSPECTION`), uploads mission flight permits, executes field sessions (`Start`, `Complete`, `Abort`) on Web and Flutter Mobile, uploads photo/MP4 evidence, confirms `YOLO11`/manual findings, submits auto-compiled reports, and performs 3-way defect verification on re-inspection missions.
- **Customer (`CUSTOMER` — `ActorZone.CUSTOMER_ORGANIZATION`)**: Customer organization owner/manager who registers with an airspace-checked initial asset, provisions `MAINTENANCE_ENGINEER` accounts, manages organization assets, submits one-time/recurring Service Requests, accepts quotes, tracks 5-stage inspection progress, accepts published reports, settles fees via **PayOS (VietQR)**, creates maintenance work orders, approves repair budgets/Change Orders, triggers re-inspection missions, and acts as independent maintenance acceptance reviewer.
- **Maintenance Engineer (`MAINTENANCE_ENGINEER` — `ActorZone.CUSTOMER_ORGANIZATION`)**: Customer engineering specialist (`Team Lead`, `Report Author`, `Team Member`) who invokes the `pgvector` RAG Scope Advisor and Cost Norms Estimator, executes field repair tasks, batch-verifies team work logs, submits auto-drafted completion reports, and reconciles actual costs.
- **Automated System & AI Actors**: **Self-Hosted YOLO11 Service (`MBDD2025`) + Vision Fallback**; **LLM & `pgvector` RAG Advisor (`TCVN 9343:2012`, `EN 1504-9`, `ISO 12944-5`)**; **PayOS VietQR Gateway**; **Spring Modulith Outbox Scheduler**.

### 3.3 Core Functional Scope (8 Mandatory Features — 2 Features per Member)

| Feature ID | Feature Name | Sub-Functions (SRS §3.2–§3.9) | Primary Owner |
| :---: | --- | --- | --- |
| **`FE-01`** | **Authentication, Google OAuth2 & 5-Role Access Control** | `3.2.1` Customer Airspace Registration, Argon2id Sign-In & Google OAuth2 (`Web` & `Mobile` deep-link)<br>`3.2.2` HS256 JWT, Refresh Rotation, `/users/me` Profile & 5-Role `ActorZone` RBAC | **Trần Tùng Bách** (`SE180220`) |
| **`FE-02`** | **Partner Onboarding, Workforce, Asset & Inspector Drone Registry** | `3.3.1` Partner Inspector Onboarding, Pilot License Review & Customer Maintenance Workforce<br>`3.3.2` Infrastructure Asset Catalog, No-Fly Zone Guard & Inspector-Owned Drone 3-Doc Review | **Trần Hoàng Trung Hiếu** (`SE184212`) |
| **`FE-03`** | **Recurring Schedules, Contract Occurrences & Outbox Notifications** | `3.4.1` Timezone-Anchored Recurring Schedules & Multi-Occurrence Contract Inheritance (Decision D2)<br>`3.4.2` Spring Modulith Transactional Outbox & Deduplicated In-App Notification Inbox | **Trần Hoàng Trung Hiếu** (`SE184212`) |
| **`FE-04`** | **Service Requests, Quotations, Contracts, Dispatch & Airspace Map** | `3.5.1` Service Requests, VND/USD Quotations, Order Chat & Signed Paper Contract Upload<br>`3.5.2` Cross-Org Partner Inspector/Drone Dispatch, Abort Re-Dispatch & Vietnam Airspace Map | **Phùng Trung Quốc** (`SE170027`) |
| **`FE-05`** | **Flight Permit Gate, Field Execution, Dashboard & Calendar** | `3.6.1` Aviation Flight Permit Upload Gate & Web/Mobile Field Flight Sessions (`Start`/`Complete`/`Abort`)<br>`3.6.2` 5-Role Operational Analytics Dashboard, Schedule Calendar & Customer 5-Stage Progress Tracker | **Phùng Trung Quốc** (`SE170027`) |
| **`FE-06`** | **Evidence Intake, YOLO11 Detection, Auto-Compiled Report & PayOS** | `3.7.1` Photo & Streaming MP4 Video Intake, YOLO11 + Vision Fallback & Findings Confirmation<br>`3.7.2` Auto-Compiled Report (`SUBMITTED`), AI Executive Summary, Manager PDF Publish & PayOS VietQR | **Trần Tùng Bách** (`SE180220`) |
| **`FE-07`** | **Maintenance Work Orders, RAG Scope/Norms Advisor & Repair Execution** | `3.8.1` Work Order Creation, `pgvector` RAG Scope Advisor & 1-Click Initial Task Provisioning<br>`3.8.2` RAG Cost Norms Estimator (`suggest-estimate`), Budget Approval & 1-Click Batch Log Verify | **Trương Thái Như** (`SE180082`) |
| **`FE-08`** | **Completion Report, 3-Way Re-inspection Verification & Cost Closure** | `3.9.1` Smart Auto-Drafted Maintenance Completion Report (`auto-draft`) & RAG Acceptance Compliance Audit<br>`3.9.2` 3-Step / 3-Way Re-inspection Defect Verification Loop, Independent Acceptance & Cost Closure | **Trương Thái Như** (`SE180082`) |

### 3.4 Technology Stack & Deployment Architecture
- **Backend API**: **Java 21**, **Spring Boot 4.1.0**, **Spring Modulith 2.1.1** (7 bounded modules: `users`, `assets`, `contracts`, `inspections`, `maintenance`, `notifications`, `infrastructure`), Spring Security OAuth2 Resource Server (HS256 JWT + Google OAuth2 + CSRF + Argon2id), Hibernate/JPA, **Flyway (`V1`–`V17`)**, **OpenHTMLtoPDF 1.0.10**.
- **AI & Vector Services**: **Python 3.11 + FastAPI 0.115.6 + Ultralytics 8.3.55 (`YOLO11 mbdd2025-v1`)** container; multimodal Vision LLM fallback; LLM Executive Summary generator; **`pgvector` (`vector(768)`)** RAG Scope, Cost Norms & Acceptance Compliance Advisor.
- **Database, Storage & Payments**: **PostgreSQL 17 (`pgvector/pgvector:pg17`)**, **MinIO S3-compatible Object Storage**, **PayOS (VietQR)** online payment links & HMAC-SHA256 webhook verification.
- **Web & Mobile Clients**: **React 19.2.8**, **TypeScript 6.0.2**, **Vite 8.2.2**, **Material UI (MUI) 9.4.0**, **TanStack Query v5**, **Leaflet 1.9.4**; **Flutter 3.13.2 (Dart)**, **Riverpod 3.4.2**, **GoRouter 17.2.1**, **Dio 5.11.0**, **file_picker 12.1.3** (streaming MP4 & PDF uploads).
- **CI/CD & Cloud Staging**: GitHub Actions (`JUnit 5 + Testcontainers`, `JaCoCo >= 80%`, `Vitest`, `Flutter analyze/test`, `Python OOXML verification`) with automated deployment to **`https://smartdroneinspection.duckdns.org`**.
