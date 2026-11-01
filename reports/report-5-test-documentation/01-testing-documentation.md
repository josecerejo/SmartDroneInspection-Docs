---
title: "Report 5 - Software Test Documentation"
document_type: report5-doc-section
weight: 15
source: "Report5_Test Documentation.docx"
---

# II. Testing Documentation

## 1. Scope of Testing

**Features and Requirements in Scope**

The testing scope encompasses the complete **SmartDroneInspection** Platform-Managed Infrastructure Inspection & Corrective Maintenance Service platform across Web (`SmartDroneInspection-frontend`), Mobile (`SmartDroneInspection-mobile`), Backend Modular Monolith (`SmartDroneInspection-backend`), and Self-Hosted AI Computer Vision (`ai-inference`), covering **eight core product features (`FE-01` to `FE-08`, two features per team member)**:
- **`FE-01` — Authentication, Google OAuth2 & 5-Role Access Control** *(Owner: Trần Tùng Bách)*: Customer registration with initial asset & No-Fly Zone airspace gate, Argon2id sign-in, Google OAuth2 (Web callback & Mobile `smartdrone://auth` deep link), HS256 JWT + HmacSHA256 refresh rotation, decoupled `/api/v1/users/me` profile, CSRF & IP rate-limiting (`10 req/60s`), and 5-role `ActorZone` RBAC (`ADMIN`, `MANAGER`, `CUSTOMER`, `INSPECTOR`, `MAINTENANCE_ENGINEER`).
- **`FE-02` — Partner Onboarding, Workforce, Asset & Inspector Drone Registry** *(Owner: Trần Hoàng Trung Hiếu)*: Partner Inspector application review with remote pilot license and offline contract key (`partner_contract_file_key`, no drone required at signup), Customer Maintenance Engineer workforce provisioning, infrastructure asset catalog with checkpoints, SHA-256 documents, and No-Fly Zone creation guard, and Inspector-owned Drone registration with 3 mandatory documents (`REGISTRATION`, `OWNERSHIP`, `INSPECTION`).
- **`FE-03` — Recurring Schedules, Contract Occurrences & Outbox Notifications** *(Owner: Trần Hoàng Trung Hiếu)*: Timezone-anchored recurring inspection schedules, multi-occurrence service contract generation and parent contract inheritance (Decision D2), and deduplicated in-app notification inbox (`notifications` + `event_publication` outbox).
- **`FE-04` — Service Requests, Quotations, Contracts, Dispatch & Airspace Map** *(Owner: Phùng Trung Quốc)*: One-time and recurring customer Service Requests, in-context Order Chat negotiation, versioned VND/USD Quotations, Quote Acceptance, signed paper contract scan upload (`PDF`/`DOCX`/`JPEG`/`PNG`), cross-organization conflict-checked Partner Inspector/Drone occurrence dispatch, abort re-dispatch (`Reschedule`, `Reassign`, `Cancel`), and the interactive Vietnam Airspace & No-Fly Zone Map (Decision 18/2020/QĐ-TTg & Decree 288/2025/NĐ-CP).
- **`FE-05` — Flight Permit Gate, Field Execution, Dashboard & Calendar** *(Owner: Phùng Trung Quốc)*: Aviation flight permit upload and readiness guard (`hasFlightPermit()`), Web/Flutter Mobile 2-outcome on-site field flight sessions (`Start` $\rightarrow$ `Complete` or `Abort` with automatic reversion to `SCHEDULED` and manager alert), 5-role operational analytics dashboards, Inspector Schedule Calendar, and the Customer 5-Stage Inspection Progress Tracker.
- **`FE-06` — Evidence Intake, YOLO11 Detection, Auto-Compiled Report & PayOS** *(Owner: Trần Tùng Bách)*: Multipart photo and streaming `video/mp4` evidence intake (`file_picker` on Mobile, `AuthenticatedMedia` on Web) with EXIF GPS extraction, `YOLO11` defect detection with automatic Vision LLM fallback, findings preview chips & baseline confirmation, 6-state Inspection & 5-state auto-compiled Report lifecycle (`SUBMITTED`), AI Executive Summary card, independent `MANAGER` PDF publication (`PUBLISHED`), Customer report acceptance, and **PayOS (VietQR)** payment settlement & finance settings.
- **`FE-07` — Maintenance Work Orders, RAG Scope/Norms Advisor & Repair Execution** *(Owner: Trương Thái Như)*: Forwarded defect triage into `MaintenanceWorkOrder`s, `pgvector` RAG repair scope advisor (`TCVN`/`EN`/`ISO`) with 1-click `initialTasks` provisioning, team role assignment, RAG Cost & Norms Estimator (`suggest-estimate`), independent Customer budget & Change Order approval, field repair execution with before/after proof, and 1-click Team Lead batch work-log verification (`batch-verify`).
- **`FE-08` — Completion Report, 3-Way Re-inspection Verification & Cost Closure** *(Owner: Trương Thái Như)*: Smart template auto-drafted Maintenance Completion Report (`auto-draft`), RAG Technical Acceptance Compliance Audit (`acceptance-compliance`), event-driven 3-step/3-way Re-inspection defect verification loop (`reinspection_defect_verifications`: Prior Defect vs Engineer Repair Proof vs Drone Re-capture), independent Customer acceptance, baseline-to-actual cost inheritance & reconciliation, and Work Order closure (`CLOSED`).

**Out-of-Scope Items**

- Physical unmanned aircraft radio-control (RC) actuation, autopilot telemetry streaming, and hardware flight controller firmware testing (`BR-16`).
- Native OS push notifications (APNs/FCM) and external SMTP delivery (notifications are delivered via the deduplicated in-app notification inbox).

**Stages and Levels of Testing**

- **Unit Testing**: Owned by individual feature developers (`Hiếu`, `Quốc`, `Bách`, `Như`); executed on every commit via JUnit 5, Vitest, and Flutter Test (`>= 80%` backend JaCoCo coverage gate).
- **Integration Testing**: Executed in CI against real containerized **PostgreSQL 17 (`pgvector:pg17`)** and **MinIO** instances via Testcontainers, verifying Flyway migrations `V1`–`V17`, Spring Modulith boundaries (`ModulithArchitectureTest`), REST controllers, security filters, PayOS webhook verification, and OpenHTMLtoPDF rendering.
- **System & End-to-End Workflow Testing**: Executed against the full-stack Docker environment (`ConnectedMainFlowE2eIntegrationTest`) and the cloud Staging server (`https://smartdroneinspection.duckdns.org`).
- **Acceptance Testing**: Conducted against the functional test cases across `Feature 1`–`Feature 8` in `Report5_Test Report.xlsx`.

---

## 2. Test Strategy

### 2.1 Testing Types
- **Functional & Business Rule Testing**:
  - *Objective*: Verify that every mandatory feature (`FE-01`–`FE-08`) and business rule (`BR-01`–`BR-49`) behaves according to the SRS specifications.
  - *Technique*: Equivalence partitioning, boundary-value analysis (`10 MB` file limits, `[-90..90]`/`[-180..180]` coordinates, `0..100%` finance rates), and positive/negative API/UI scenarios.
  - *Completion Criteria*: Complete functional test coverage across `Feature 1`–`Feature 8` with 100% of happy-path test cases passing.
- **State Machine Transition Testing**:
  - *Objective*: Ensure every lifecycle entity transitions only along valid, authorized edges and rejects illegal or out-of-order state mutations (`400 Bad Request` / `409 Conflict`).
  - *Technique*: State-transition path coverage across `ServiceRequest`, `ServiceRequestOccurrence`, `Asset`, `Drone`, `RecurringInspectionSchedule`, `Inspection` (6 states), `FieldSession`, `Finding`, `InspectionReport` (5 states), `ReinspectionDefectVerification` (3-way), and `MaintenanceWorkOrder` (12 states).
  - *Completion Criteria*: 100% of main entity state machines covered by positive and negative transition tests.
- **Security, RBAC & Multi-Zone Isolation Testing**:
  - *Objective*: Verify zero cross-tenant data leakage, strict `ActorZone` and role separation of duties (authors/team members cannot self-approve or self-accept; Customers cannot read unpublished reports or download unpaid PDFs), CSRF enforcement, account lockout, and IP rate-limiting.
  - *Technique*: Cross-organization ID probing, 5-role matrix permutation testing, token revocation checks, and brute-force rate-limit simulation (`AuthRateLimitFilter`).
  - *Completion Criteria*: `100%` of unauthorized or cross-scope requests rejected (`NFR-03`, `NFR-04`).
- **Performance, Integrity & Non-Functional Testing**:
  - *Objective*: Validate API response latency (`NFR-01`), YOLO11 + Vision fallback inference latency (`NFR-02`), signed contract and published PDF report immutability (`NFR-05`), and modular architecture / coverage gates (`NFR-06`).
  - *Technique*: Concurrent API timing assertions, container inference benchmarks, `SHA-256` immutability assertions, and automated JaCoCo + Spring Modulith verification in GitHub Actions.
  - *Completion Criteria*: All 6 locked NFR thresholds met and verified by reproducible tests.

### 2.2 Test Levels

| Type of Tests | Unit | Integration | System | Acceptance |
| --- | :---: | :---: | :---: | :---: |
| Functional & Business Rule Testing | X | X | X | X |
| Domain State Machine Transition Testing | X | X | X | X |
| API & Database Persistence Testing (V1–V17) |  | X | X |  |
| Security, RBAC & ActorZone Isolation Testing | X | X | X | X |
| AI Vision, Executive Summary & pgvector RAG Testing | X | X | X | X |
| Performance, PayOS Webhook & PDF Immutability Testing |  | X | X | X |

### 2.3 Supporting Tools

| Purpose | Tool | Vendor/In-house | Version |
| --- | --- | --- | --- |
| Backend Unit & Integration Testing Framework | JUnit Jupiter / Spring Boot Test / MockMvc | Open Source (Eclipse / Broadcom) | `6.0.x` / `4.1.0` |
| Containerized Database & S3 Test Harness | Testcontainers (`pgvector:pg17` & `MinIO`) | AtomicJar / Docker | `1.20.x` / `PG 17` |
| Architectural Boundary & Code Coverage Gate | Spring Modulith Test / JaCoCo Maven Plugin | Broadcom / EclEmma | `2.1.1` / `0.8.13` |
| Frontend Component & Unit Testing | Vitest / React Testing Library / JSDOM | Open Source (Vite / Testing Library) | `5.0.1` / `16.3.3` |
| Mobile Widget & Repository Testing | Flutter Test / Dart Analyzer | Google | `Dart 3.13.2` |
| Full-Stack E2E & Browser Automation | Node.js E2E Runner / Playwright MCP | Open Source / Microsoft | `Node 22` / `1.50+` |
| Continuous Integration & Deployment | GitHub Actions (`ci.yml`, `deploy.yml`) | GitHub | `v4` |
| Report & Workbook OOXML Verification | Custom Python OOXML Exporter & Unittest Suite | In-house (`SmartDroneInspection-docs/tools`) | `Python 3.12+` |

---

## 3. Test Plan

### 3.1 Human Resources

| Worker/Doer | Role | Specific Responsibilities/Comments |
| --- | --- | --- |
| **Trần Hoàng Trung Hiếu** (`SE184212`) | Project Leader & Tester (`FE-02`, `FE-03` Owner) | Owns functional test cases on Sheets **`Feature 2` and `Feature 3`** covering `FE-02` (Partner Onboarding, Workforce, Asset & Inspector Drone Registry) and `FE-03` (Recurring Schedules, Contract Occurrences & Outbox Notifications). |
| **Phùng Trung Quốc** (`SE170027`) | Backend / Mobile Engineer & Tester (`FE-04`, `FE-05` Owner) | Owns functional test cases on Sheets **`Feature 4` and `Feature 5`** covering `FE-04` (Service Requests, Quotations, Contracts, Dispatch & Airspace Map) and `FE-05` (Flight Permit Gate, Field Execution, Dashboard & Calendar). |
| **Trần Tùng Bách** (`SE180220`) | Full-Stack / AI Engineer & Tester (`FE-01`, `FE-06` Owner) | Owns functional test cases on Sheets **`Feature 1` and `Feature 6`** covering `FE-01` (Authentication, Google OAuth2 & 5-Role Access Control) and `FE-06` (Evidence Intake, YOLO11 Detection, Auto-Compiled Report & PayOS). |
| **Trương Thái Như** (`SE180082`) | Full-Stack Engineer & Tester (`FE-07`, `FE-08` Owner) | Owns functional test cases on Sheets **`Feature 7` and `Feature 8`** covering `FE-07` (Maintenance Work Orders, RAG Scope/Norms Advisor & Repair Execution) and `FE-08` (Completion Report, 3-Way Re-inspection Verification & Cost Closure). |
| **Phạm Minh Trí & Đặng Ngọc Minh Đức** | Supervisors / Reviewers | Review test strategy, verify quality targets, and audit Defense readiness. |

### 3.2 Test Environment

| Purpose | Tool | Provider | Version |
| --- | --- | --- | --- |
| Cloud Staging Environment | Ubuntu Linux VPS (`https://smartdroneinspection.duckdns.org`, Docker Compose, Nginx, Tailscale) | Cloud VPS / DuckDNS | `Ubuntu 24.04` / `Docker 27.x` |
| Backend Runtime & API Container | Eclipse Temurin JRE Alpine + Spring Boot | Adoptium / Broadcom | `Java 21` / `4.1.0` |
| Relational & Vector Database Server | PostgreSQL with `pgvector` and `pgcrypto` | PostgreSQL Global Dev Group | `17` (`pgvector:pg17`) |
| S3-Compatible Object Storage | MinIO Server (`inspection-evidence` bucket) | MinIO Inc. | `RELEASE.2025` |
| Computer Vision Defect Inference Container | Python Slim + FastAPI + Ultralytics YOLO11 (`MBDD2025`) | Python / Ultralytics | `Python 3.11` / `8.3.55` |
| Web & Mobile Test Clients | Google Chrome / Edge + Flutter Android Client | Google / Microsoft | `Evergreen` / `API 34` |

### 3.3 Test Milestones

| Milestone Task | Start Date | End Date |
| --- | --- | --- |
| Milestone 1: Unit & Migration Foundation Gate (Schema, Auth, RBAC, Modulith Boundaries) | `2026-09-15` | `2026-10-08` |
| Milestone 2: Core Inspection, MinIO, YOLO11 & PDF Reporting Integration Testing | `2026-10-09` | `2026-10-22` |
| Milestone 3: Review 2 Baseline & RAG Maintenance Verification | `2026-10-23` | `2026-10-27` |
| Milestone 4: 5-Role Platform Service Cutover (`V7`–`V17`), Contracts, PayOS & 3-Way Re-inspection Verification | `2026-10-28` | `2026-11-01` |
| Milestone 5: Final Regression & Live Demo Rehearsal (`100%` Workflows, `>= 90%` Pass Rate across `Feature 1`–`Feature 8`) | `2026-11-02` | `2026-11-30` |

---

## 4. Test Cases

**8-Feature Functional Test Suite Structure (`FE-01` to `FE-08`)**

The functional test case inventory in `Report5_Test Report.xlsx` is organized across **8 Feature sheets (`Feature 1` through `Feature 8`, mapped 1-to-1 to `FE-01` through `FE-08`, 2 features per team member)**:
- **`Feature 1` (`FE-01` — Trần Tùng Bách)**: Customer airspace registration, Argon2id & Google OAuth2 sign-in, session rotation, `/users/me`, and 5-role `ActorZone` RBAC (`WF1-001`–`WF1-005`).
- **`Feature 2` (`FE-02` — Trần Hoàng Trung Hiếu)**: Partner Inspector onboarding, Customer Maintenance Engineer provisioning, Asset catalog with No-Fly Zone guard, and Inspector-owned Drone 3-document registration & review (`WF1-006`–`WF1-016`).
- **`Feature 3` (`FE-03` — Trần Hoàng Trung Hiếu)**: Timezone-anchored recurring schedules, multi-occurrence contract inheritance (Decision D2), and deduplicated transactional outbox notifications (`WF1-017`–`WF1-021`).
- **`Feature 4` (`FE-04` — Phùng Trung Quốc)**: Service requests, VND/USD quotes, Order Chat, signed paper contract upload, cross-org partner dispatch, abort re-dispatch, and Vietnam Airspace Map (`WF2-001`–`WF2-005` — `5` TCs).
- **`Feature 5` (`FE-05` — Phùng Trung Quốc)**: Flight permit upload gate, 2-outcome field sessions (`Start`, `Complete`, `Abort`), 5-role dashboard, schedule calendar, and 5-stage Customer Progress Tracker (`WF2-008`–`WF2-009`, `WF2-011`–`WF2-012`, `WF2-015`–`WF2-020`, `WF3-009` — `11` TCs).
- **`Feature 6` (`FE-06` — Trần Tùng Bách)**: Photo & streaming MP4 video evidence intake, `YOLO11` + Vision LLM fallback, findings preview & baseline confirmation, 5-state auto-compiled report, AI Executive Summary, Manager PDF publication, and PayOS VietQR settlement (`WF3-001`–`WF3-008`, `WF3-010`–`WF3-017`).
- **`Feature 7` (`FE-07` — Trương Thái Như)**: Work order creation with 1-click RAG initial tasks, team assignment, RAG cost norms estimator (`suggest-estimate`), Customer budget/Change Order approval, field repair execution, and 1-click batch work-log verification (`WF4-001`–`WF4-011`).
- **`Feature 8` (`FE-08` — Trương Thái Như)**: Smart auto-drafted completion report (`auto-draft`), RAG acceptance compliance audit (`acceptance-compliance`), 3-step/3-way Re-inspection defect verification loop, independent Customer acceptance, and cost reconciliation/closure (`WF4-012`–`WF4-016`).

**Test Case Artifacts**

- **Unit & Integration Test Suites**: Automated JUnit 5 & Testcontainers (`SmartDroneInspection-backend`), Vitest (`SmartDroneInspection-frontend`), and Flutter Test (`SmartDroneInspection-mobile`).
- **System & Functional Test Workbook**: `Report5_Test Report.xlsx` (`Cover`, `Test Cases`, `Test Statistics`, and `Feature 1` through `Feature 8`).

---

## 5. Test Reports

**Execution Summary Statistics (`Feature 1` through `Feature 8`)**

All 65 functional test cases in `Report5_Test Report.xlsx` are mapped across the 8 product features (`FE-01`–`FE-08`):
- **Total Test Cases**: `65` (`64` baseline cases + `1` Vision fallback case `WF3-017`)
- **Passed**: `60` (`92.31%` overall / `93.75%` baseline Test Successful Coverage — exceeds the `>= 90%` threshold)
- **Failed**: `0` (`0.00%`)
- **Pending**: `5` (`7.69%`)
- **N/A**: `0` (`0.00%`)
- **Defect Status**: `0` open Critical or High defects in `Report3_Project Tracking.xlsx`.
