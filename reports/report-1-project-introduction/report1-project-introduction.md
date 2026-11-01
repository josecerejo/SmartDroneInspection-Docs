---
title: "Report 1 Project Introduction"
document_type: capstone-report
report_number: 1
source_docx: report1-project-introduction.docx
---

– Ho Chi Minh City, October 2026 –

# I. Record of Changes

| Date | A* M, D | In charge | Change Description |
| --- | --- | --- | --- |
| 11 Sep 2026 | A | Team | Version 1.0: Complete project-specific introduction, background, existing systems, and team information. |
| 21 Sep 2026 | M | Team | Version 1.2: Aligned customer organization self-registration and scope exclusions. |
| 27 Oct 2026 | M | Team | Version 2.0: Synchronized with the 5-role governance model, Airspace & No-Fly Zone Map, and pgvector RAG Maintenance Scope Advisor. |
| 01 Nov 2026 | M | Team | Version 3.0: Synchronized with the 5-Role Platform Inspection Service model (ADMIN, MANAGER, CUSTOMER, INSPECTOR, MAINTENANCE_ENGINEER), narrowed scope to 8 product features (FE-01 to FE-08, 2 features per member), and integrated Partner Onboarding, Service Requests/Quotes/Signed Contracts, PayOS VietQR settlement, 6-state Inspections, 5-state Auto-Compiled Reports with AI Executive Summaries, and 3-Way Re-inspection Defect Verification. |

*A - Added M - Modified D - Deleted

# II. Project Introduction

## 1. Overview

### 1.1 Project Information

- Project name: SmartDroneInspection: AI-powered Infrastructure Inspection Management Platform
- Project code: GFA26SE139
- Group name: FA26SE112
- Software type: Platform-Managed Infrastructure Inspection & Corrective Maintenance Service Platform (Responsive React 19 Web Portals, Flutter Field Mobile Application, Spring Boot 4.1 Modular Monolith REST API, and Self-Hosted FastAPI YOLO11 / pgvector RAG AI Services)

### 1.2 Project Team

| Full Name | Role | Email | Mobile |
| --- | --- | --- | --- |
| Phạm Minh Trí | Lecturer | tripm14@fpt.edu.vn |  |
| Đặng Ngọc Minh Đức | Lecturer | ducdnm2@fpt.edu.vn |  |
| Trần Hoàng Trung Hiếu | Leader | hieuthtse184212@fpt.edu.vn | 0963832382 |
| Phùng Trung Quốc | Member | quocptse170027@fpt.edu.vn | 0896986551 |
| Trương Thái Như | Member | nhuttse180082@fpt.edu.vn | 0328416716 |
| Trần Tùng Bách | Member | bachttse180220@fpt.edu.vn | 0378351050 |

## 2. Product Background

Organizations that own or manage critical civil and energy infrastructure assets — such as highway bridges, commercial buildings, transmission towers, solar farms, wind turbines, and industrial facilities — must perform periodic structural inspections to identify defects, assess asset health, comply with aviation and safety regulations, and verify maintenance repairs. In practice, commercial service requests, quotations, offline service contracts, partner drone pilot scheduling, flight permits, field inspection logs, aerial imagery and video, defect findings, inspection reports, and maintenance work orders are frequently handled across disconnected spreadsheets, messaging apps, and manual folders. This fragmentation makes it difficult to enforce Vietnam aviation compliance, prevent cross-customer scheduling conflicts, trace every defect back to geotagged photographic or video evidence, or audit repair budgets and post-repair re-inspections from initial estimation to final cost closure.

SmartDroneInspection is engineered to unify this lifecycle into a platform-managed Infrastructure Inspection and Corrective Maintenance Service platform. It connects customer airspace-gated asset onboarding and vetted third-party partner Inspector/Drone registration (`MF1`) directly to service request negotiation, VND/USD quotations, offline signed contracts, and cross-organization mission dispatch (`MF2`), aviation flight permit verification, field survey execution, human-verified AI defect detection, auto-compiled PDF reporting with AI executive summaries, and PayOS VietQR payment settlement (`MF3`), and standards-grounded `pgvector` RAG maintenance remediation with 3-way re-inspection defect verification (`MF4`).

## 3. Existing Systems

The following commercial systems provide reference benchmarks for drone inspection data management, visual review, and reporting.

### 3.1 DroneDeploy

Description: DroneDeploy is a cloud-based drone data platform for flight planning, image processing, visual inspection, analysis, and reporting.

Actors: Organization Owner/Admin, Coordinator, Member, External User, Pilot, Analyst, and Viewer.

Main features: Automated flight planning, drone media upload and orthomosaic/3D processing, measurements, visual issue tagging, inspection reports, and workspace permission management.

Pros: Mature visual inspection interface, strong 2D/3D spatial visualization, and flexible workspace collaboration.

Cons: Focuses primarily on aerial mapping and visual issue tagging rather than platform-managed inspection service contracts, Vietnam Decision No. 18/2020/QĐ-TTg and Decree No. 288/2025/NĐ-CP airspace and flight-permit readiness gates, independent two-tier report publication with VietQR payment settlement, or civil-engineering maintenance work orders with `pgvector` RAG cost norms and 3-way re-inspection verification.

Reference: DroneDeploy, https://www.dronedeploy.com/

### 3.2 Flyability Inspector

Description: Flyability Inspector is companion desktop and cloud software designed for organizing, reviewing, and reporting indoor/confined-space inspection data captured by Elios drones.

Actors: Inspection Teams, Structural Engineers, and Asset Owners.

Main features: Asset-based organization, visual review with points of interest (POI), spatial localization, historical comparison, and structured inspection report generation.

Pros: Strong visual context for reviewing localized structural defects and comparing inspection history over time.

Cons: Coupled to proprietary Elios hardware data rather than hardware-agnostic uploaded aerial photos and MP4 videos, and does not provide commercial service request/quote/contract workflows, partner pilot dispatch, or end-to-end maintenance work order cost reconciliation.

Reference: Flyability, "Inspector", https://www.flyability.com/inspector

## 4. Business Opportunity

Infrastructure-owning enterprises in Vietnam and Southeast Asia increasingly rely on specialized unmanned aerial vehicle (UAV) inspection services for bridge, building, power-grid, and renewable-energy assessments rather than maintaining expensive internal aviation departments. However, coordinating external partner drone pilots, verifying 3-document aircraft airworthiness, checking prohibited military/aviation no-fly zones, negotiating one-off and recurring service contracts, verifying AI-detected defects, settling inspection fees, and closing the loop on structural repairs require an integrated governance platform.

SmartDroneInspection addresses this gap by combining a **Platform-Coordinated Partner Inspector & Commercial Service Contract model** with an **end-to-end Inspection-to-Maintenance Engineering workflow**. Customers register their infrastructure assets through an automated Vietnam No-Fly Zone gate, request one-off or recurring inspection services, negotiate VND/USD quotes via order chat, sign offline paper contracts, track 5-stage mission progress, accept published PDF reports, pay online via **PayOS (VietQR)**, and execute corrective maintenance guided by a `pgvector` RAG civil engineering advisor (`TCVN 9343:2012`, `EN 1504-9`, `ISO 12944-5`) and a 3-step/3-way drone re-inspection verification loop.

## 5. Software Product Vision

For infrastructure-owning customer organizations that require auditable, standards-compliant structural inspections and maintenance remediation, **SmartDroneInspection** is a multi-portal Web and Flutter Mobile platform that connects commercial inspection service contracts and vetted partner drone pilots to field survey execution, human-verified AI defect findings, independently published PDF reports, PayOS VietQR settlement, and budget-controlled engineering work orders.

Unlike generic cloud storage or standalone mapping tools, SmartDroneInspection enforces strict 5-role separation of duties across three operational zones (`PLATFORM`, `CUSTOMER_ORGANIZATION`, `INSPECTOR_PARTNER`), immutable published PDF report integrity (`SHA-256`), and human accountability at every AI decision boundary — ensuring that AI computer vision (`YOLO11` with Vision LLM fallback) and generative language models (AI Executive Summaries & `pgvector` RAG scope, cost norm, and compliance advisors) accelerate engineering productivity without replacing professional engineering judgment.

## 6. Project Scope & Limitations

The software product is architected as a Platform-Managed Infrastructure Inspection & Corrective Maintenance Service platform organized around four connected Main Flows (`MF1` to `MF4` / `WF-01` to `WF-04`):
- **Stage 1 (`MF1` / `WF-01` — Partner Inspector Onboarding, Customer Airspace Registration, Asset & Drone Registry)**: Customer self-registration with initial infrastructure asset evaluation against Vietnam No-Fly Zones (Decision 18/2020/QĐ-TTg & Decree 288/2025/NĐ-CP), partner Inspector onboarding with remote pilot license and offline partner contract verification (no drone required at signup), inspector-owned drone registration with 3 mandatory documents (`REGISTRATION`, `OWNERSHIP`, `INSPECTION`), customer asset catalog with standardized checkpoints, and Customer Maintenance Engineer workforce provisioning.
- **Stage 2 (`MF2` / `WF-02` — Service Requests, VND/USD Quotations, Order Chat, Signed Contracts & Partner Dispatch)**: One-time and recurring customer service requests (`OPEN`), in-context order chat negotiation (`service_request_messages`), versioned VND/USD quotations bound to a partner Inspector and their owned drone (`QUOTED`), quote acceptance (`ACCEPTED`), executed offline paper contract scan upload with SHA-256 verification and recurring occurrence inheritance (`CONTRACT_SIGNED`), and cross-organization conflict-checked partner occurrence assignment (`ASSIGNED` -> `Inspection: SCHEDULED`).
- **Stage 3 (`MF3` / `WF-03` — Flight Permit Gate, Field Execution, Photo/MP4 Evidence, YOLO11 Detection, Auto-Compiled Report & PayOS Settlement)**: Aviation flight permit upload and pilot license readiness guard (`hasFlightPermit()`), Web/Flutter Mobile on-site field flight sessions (`IN_PROGRESS` -> `FIELD_COMPLETED` or `ABORTED` with automatic reversion to `SCHEDULED` and manager reschedule/reassign/cancel dispatch), photo and streaming `video/mp4` evidence intake into MinIO, `YOLO11` + Vision LLM fallback defect detection, findings baseline confirmation, tab-visit auto-compiled report submission (`SUBMITTED`, mission `UNDER_REVIEW`), AI Executive Summary generation, independent `MANAGER` review and immutable A4 PDF publication (`PUBLISHED`, mission `COMPLETED`), Customer report acceptance (`PAYMENT_DUE`), and **PayOS (VietQR)** online payment settlement (`PAID`, unlocking PDF download and partner payout eligibility).
- **Stage 4 (`MF4` / `WF-04` — Maintenance Work Orders, RAG Scope/Norms Advisor, Field Repair, 3-Way Re-inspection & Cost Closure)**: Corrective defect handoff into `MaintenanceWorkOrder`s, `pgvector` RAG repair scope advisory with 1-click initial task provisioning, engineering team role allocation (`Team Lead`, `Report Author`, `Team Member`, independent `CUSTOMER` reviewer), RAG-assisted Vietnamese construction cost norm estimation (`suggest-estimate`), Customer budget and Change Order approval, field repair execution with before/after proof and 1-click Team Lead batch work-log verification (`batch-verify`), smart auto-drafted Maintenance Completion Report (`auto-draft`), RAG technical acceptance compliance audit (`acceptance-compliance`), automated 3-step/3-way Re-inspection defect verification loop (`RESOLVED`, `UNRESOLVED`, `INCONCLUSIVE`), independent Customer acceptance, baseline-to-actual cost reconciliation, and Work Order closure (`CLOSED`).

**Five-Role Governance Model**

The platform enforces strict role-based and zone-scoped access control across five canonical login roles in three operational zones:
- **Platform Zone (`ActorZone.PLATFORM`)**: `Platform Admin` (`ADMIN`) governs internal platform accounts, standard asset categories, customer restricted-airspace reviews, partner inspector/drone approvals, finance settings (commission, VAT, TNCN rates), and system audit logs; `Platform Manager` (`MANAGER`) governs partner Inspector/Drone registries, service request chat and VND/USD quotations, signed contract uploads, cross-organization partner dispatch, abort re-dispatch, independent inspection report review/publication, and partner payouts.
- **Partner Inspector Zone (`ActorZone.INSPECTOR_PARTNER`)**: `Inspector` (`INSPECTOR`) is an independent licensed partner pilot who applies with a pilot license (drone optional at signup), registers owned drones with 3 documents, uploads mission flight permits, executes field sessions (`Start`, `Complete`, `Abort`), uploads photo/MP4 evidence, confirms `YOLO11`/manual findings, submits auto-compiled reports, and performs 3-way defect verification on re-inspection missions.
- **Customer Organization Zone (`ActorZone.CUSTOMER_ORGANIZATION`)**: `Customer` (`CUSTOMER`) governs organization assets, Maintenance Engineer accounts, service requests, quote acceptance, 5-stage progress tracking, published report acceptance, PayOS VietQR settlement, maintenance work orders, repair budgets/Change Orders, re-inspection requests, and independent maintenance acceptance/closure; `Maintenance Engineer` (`MAINTENANCE_ENGINEER`) plans RAG-assisted tasks and cost estimates, executes field repairs, batch-verifies team work logs, and submits auto-drafted completion reports.

### 6.1 Major Features

Eight core product features (`FE-01` to `FE-08`, 2 functions per feature = 16 functions total, 2 features per team member) form the unified scope baseline across Reports 1–5:

- **FE-01: Authentication, Google OAuth2 & 5-Role Access Control** *(Owner: Trần Tùng Bách)* — Customer registration with initial asset & No-Fly Zone airspace gate, Argon2id sign-in, Google OAuth2 (Web callback & Mobile `smartdrone://auth` deep link), HS256 JWT + HmacSHA256 refresh rotation, decoupled `/api/v1/users/me` profile, and 5-role `ActorZone` RBAC across `/admin`, `/client`, and `/operations`.
- **FE-02: Partner Onboarding, Workforce, Asset & Inspector Drone Registry** *(Owner: Trần Hoàng Trung Hiếu)* — Partner Inspector application & pilot license/offline contract review (no drone required at signup), Customer Maintenance Engineer workforce provisioning, infrastructure asset catalog with checkpoints, SHA-256 documents, and No-Fly Zone creation guard, and Inspector-owned Drone registration with 3 mandatory documents (`REGISTRATION`, `OWNERSHIP`, `INSPECTION`).
- **FE-03: Recurring Schedules, Contract Occurrences & Outbox Notifications** *(Owner: Trần Hoàng Trung Hiếu)* — Timezone-anchored recurring inspection schedules, multi-occurrence service contract generation and parent contract inheritance (Decision D2), and deduplicated event-driven in-app notifications (`notifications` + `event_publication` outbox).
- **FE-04: Service Requests, Quotations, Contracts, Dispatch & Airspace Map** *(Owner: Phùng Trung Quốc)* — One-time and recurring Service Requests, in-context Order Chat negotiation, versioned VND/USD Quotations, Quote Acceptance, offline Signed Paper Contract scan upload (`PDF`/`DOCX`/`JPEG`/`PNG`), cross-organization conflict-checked Partner Inspector/Drone occurrence dispatch, abort re-dispatch (`Reschedule`, `Reassign`, `Cancel`), and the interactive Vietnam Airspace & No-Fly Zone Map (Nominatim & Vietnam landmarks).
- **FE-05: Flight Permit Gate, Field Execution, Dashboard & Calendar** *(Owner: Phùng Trung Quốc)* — Aviation flight permit upload and readiness guard (`hasFlightPermit()`), Web/Flutter Mobile on-site field flight session logging (`Start`, `Complete`, `Abort` with manager alert), role-scoped operational analytics dashboards, Inspector Schedule Calendar, and the Customer 5-Stage Inspection Progress Tracker.
- **FE-06: Evidence Intake, YOLO11 Detection, Auto-Compiled Report & PayOS** *(Owner: Trần Tùng Bách)* — Multipart photo and streaming `video/mp4` evidence intake (`file_picker` on Mobile, `AuthenticatedMedia` on Web) with EXIF GPS extraction, `YOLO11` defect detection with automatic Vision LLM fallback, findings preview chips & baseline confirmation, 6-state Inspection & 5-state auto-compiled Report lifecycle (`SUBMITTED`), AI Executive Summary card, independent `MANAGER` PDF publication (`PUBLISHED`), Customer report acceptance, and **PayOS (VietQR)** payment settlement & finance settings.
- **FE-07: Maintenance Work Orders, RAG Scope/Norms Advisor & Repair Execution** *(Owner: Trương Thái Như)* — Forwarded defect triage into `MaintenanceWorkOrder`s, `pgvector` RAG repair scope advisor (`TCVN`/`EN`/`ISO`) with 1-click `initialTasks` provisioning, team role assignment, RAG Cost & Norms Estimator (`suggest-estimate`), independent Customer budget & Change Order approval, field repair execution with before/after proof, and 1-click Team Lead batch work-log verification (`batch-verify`).
- **FE-08: Completion Report, 3-Way Re-inspection Verification & Cost Closure** *(Owner: Trương Thái Như)* — Smart template auto-drafted Maintenance Completion Report (`auto-draft`), RAG Technical Acceptance Compliance Audit (`acceptance-compliance`), event-driven 3-step/3-way Re-inspection defect verification loop (`reinspection_defect_verifications`: Prior Defect vs Engineer Repair Proof vs Drone Re-capture), independent Customer acceptance, baseline-to-actual cost inheritance & reconciliation, and Work Order closure (`CLOSED`).

![Report 1 figure](assets/image15.png)

Figure 1. Core operational workflow diagram from partner and customer airspace onboarding through service contracts, field capture, AI defect verification, auto-compiled reporting, PayOS settlement, and RAG-assisted maintenance remediation.

### 6.2 Limitations & Exclusions

- **LI-1 (No Real-Time Drone Flight Control)**: The platform does not provide autonomous drone flight control, radio-control (RC) piloting, or live autopilot telemetry streaming (`BR-16`). Drone flight operations are executed by licensed partner Inspectors using the aircraft's dedicated flight controller in compliance with Vietnam Decree No. 288/2025/NĐ-CP.
- **LI-2 (Human-in-the-Loop AI & RAG Mandate)**: All AI outputs — `YOLO11` / Vision fallback defect candidates (`PENDING`), AI Executive Summaries, and `pgvector` RAG scope, cost norm, and compliance recommendations — are strictly advisory (`BR-20`, `BR-27`). No AI output is published or approved without explicit human verification.
- **LI-3 (Controlled Onboarding & Zone Separation)**: Public self-registration creates only a Customer organization (with airspace verification on its initial asset); partner Inspector accounts and internal platform roles require administrative verification (`BR-01`, `BR-06`, `BR-29`).
- **LI-4 (Strict Multi-Zone, Tenant & Assignment Scoping)**: Customer resources are isolated by `organization_id`, and partner Inspectors can access only missions explicitly assigned to them (`BR-02`, `BR-04`).
- **LI-5 (Immutable Published Deliverables & Payment Gate)**: Published inspection reports (`PUBLISHED`) and accepted maintenance completion reports are rendered to immutable `SHA-256` PDF files in MinIO (`BR-26`, `BR-49`), and Customer PDF downloads enforce the PayOS / settlement payment gate (`BR-33`).
- **LI-6 (No 3D Photogrammetry Reconstruction)**: General-purpose 3D point-cloud photogrammetry and digital-twin mesh reconstruction are outside the capstone scope.
- **LI-7 (In-App Notification Delivery)**: Operational alerts are delivered through the deduplicated in-app notification inbox (`/api/v1/notifications`) backed by the Spring Modulith transactional outbox (`event_publication`).
