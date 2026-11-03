---
title: "CAPSTONE PROJECT REGISTER"
document_type: review2-registration
version: "2.0"
date: "2026-11-03"
project_code: "GFA26SE139"
group_name: "FA26SE112"
---

# CAPSTONE PROJECT REGISTER

- **Class:** FA26SE112 | **Duration time:** from 09/2026 To 03/2027
- **(*) Profession:** Software Engineer | **Specialty:** SE
- **(*) Kinds of person make registers:** Students

---

## 1. Register information for supervisor (if have)

| No. | Full name | Phone | E-Mail | Title |
| :---: | --- | :---: | --- | :---: |
| 1 | Phạm Minh Trí | | `tripm14@fpt.edu.vn` | Giảng viên |
| 2 | Đặng Ngọc Minh Đức | | `ducdnm2@fpt.edu.vn` | Giảng viên |

---

## 2. Register information for students (if have)

| No. | Full name | Student code | Phone | E-mail | Role in Group |
| :---: | --- | :---: | :---: | --- | :---: |
| 1 | Trần Hoàng Trung Hiếu | `SE184212` | `0963832382` | `hieuthtse184212@fpt.edu.vn` | Leader |
| 2 | Phùng Trung Quốc | `SE170027` | `0896986551` | `quocptse170027@fpt.edu.vn` | Member |
| 3 | Trương Thái Như | `SE180082` | `0328416716` | `nhuttse180082@fpt.edu.vn` | Member |
| 4 | Trần Tùng Bách | `SE180220` | `0378351050` | `bachttse180220@fpt.edu.vn` | Member |

---

## 3. Register content of Capstone Project

### (*) 3.1. Capstone Project name:
- **3.1.1. English:** SmartDroneInspection: AI-powered Infrastructure Inspection Management Platform
- **3.1.2. Vietnamese:** SmartDroneInspection: Nền tảng Quản lý Kiểm tra Hạ tầng bằng Drone tích hợp AI

---

### (*) 3.2. Main proposal content (including result and product)

#### a) Context:
Infrastructure assets such as buildings, bridges, roads, transmission towers, solar farms, industrial facilities, and telecommunication stations require regular inspections to ensure operational safety and maintenance planning. Traditional inspection processes are often manual, labor-intensive, time-consuming, and potentially hazardous for inspectors.

The increasing adoption of drones enables organizations to capture high-quality aerial images and videos efficiently. However, many organizations still lack a centralized platform for managing inspection requests, schedules, reports, detected defects, maintenance tickets, and historical inspection records.

Furthermore, drone operation should be separated from business applications. Drone missions, telemetry, and flight operations should be managed by a common drone platform (SmartDroneHub), while inspection applications should focus on asset management and inspection workflows.

This project proposes SmartDroneInspection, an AI-powered Infrastructure Inspection Management Platform that manages the complete inspection lifecycle while integrating with SmartDroneHub through standardized APIs for drone mission execution.

*Note: All required hardware components (if any) will be supported and provided by AiTA Lab to facilitate development, testing, and demonstration of the system.*

#### b) Proposed Solutions:
SmartDroneInspection is designed as a business-oriented inspection management platform rather than a drone control system. The system manages infrastructure assets, inspection service requests, quotations and contracts, inspection planning, reports, defect tracking, and maintenance work orders - while consuming drone operation services from SmartDroneHub through standardized APIs.

**Human Actors**
- **Administrator (`Admin`)** - manages users, organizations, airspace/registration approvals, asset categories, and system configuration.
- **Inspection Manager (`Manager`)** - reviews service requests, issues quotations and contracts, creates inspection schedules, assigns inspectors and drones, and reviews/publishes reports.
- **Customer (`Customer`)** - manages organization assets and maintenance staff, submits inspection service requests, accepts quotations and published reports, processes online payments, and approves/accepts maintenance work orders.
- **Inspector (`Inspector`)** - reviews assigned inspections, uploads flight permits, executes field sessions with SmartDroneHub, uploads photo/video evidence, records and confirms findings, submits reports, and verifies re-inspections.
- **Maintenance Engineer (`Maintenance Engineer`)** - manages corrective maintenance work orders, updates repair tasks with photo proof, and tracks maintenance completion history.

**Five Core Subsystems**
1. **Asset & Fleet Management**
   Manage infrastructure assets, airspace zones, categories, specifications, locations, technical documents, registered inspector drones, lifecycle status, and inspection history.
2. **Inspection Planning, Request & Contract Management**
   Support one-time and recurring inspection service requests, quotation negotiation, signed contract records, inspection scheduling, frequency configuration, priority assignment, and conflict-checked inspector/drone allocation.
3. **Drone Mission Integration**
   Integrate with SmartDroneHub via REST API to create inspection missions, retrieve live telemetry, flight traces, drone images, flight videos (`video/mp4`), and flight reports. SmartDroneInspection acts as a consumer, not a drone controller.
4. **Inspection Report, Defect & Maintenance Management**
   Manage inspection reports, findings, photo and video evidence, online fee settlement (`PayOS`), defect classification, severity tracking, repair recommendations, and corrective maintenance work order & re-inspection lifecycle.
5. **AI-assisted Services**
   Three focused AI features integrated within the 15-week project scope:
   - **Inspection Image & Video Analysis** - detect potential defects from drone imagery and flight videos using `DroneVisionAI` (`YOLO11` & Vision LLM fallback).
   - **Inspection Report Summarization** - generate concise executive summaries from inspection reports using an LLM.
   - **Historical Case & Engineering Recommendation** - suggest repair scopes, cost norms, and compliance guidelines using `DroneKnowledgeAI` (`pgvector` RAG).

#### c) Functional Requirements:

**User Management**
- Authentication, Google OAuth2 login, authorization, 5-role access control (`Admin`, `Manager`, `Customer`, `Inspector`, `Maintenance Engineer`)
- User profiles, partner inspector & customer workforce onboarding, audit logs

**Asset Management**
- Create/update assets, manage asset categories, inspection checkpoints, and documents
- Airspace zone validation (No-Fly / Restricted Zones), Inspector-owned drone registration (3-document verification), asset history, and lifecycle tracking

**Inspection Planning**
- Create inspection plans, schedule one-time and recurring inspections, assign conflict-checked inspectors and drones
- Manage inspection calendars, flight permit pre-flight gate, and inspection notifications

**Inspection Request Management**
- Create, approve, track, and cancel inspection service requests
- Order chat negotiation, versioned quotations, signed contract upload, online payment settlement (`PayOS`), and request history

**Drone Mission Integration**
- Create and control inspection missions (`Start`, `Abort`, `Complete`) via SmartDroneHub Mission API
- Retrieve mission status, live telemetry, GPS flight traces, inspection images, flight videos (`video/mp4`), and flight reports

**Inspection Report Management**
- Upload photo and MP4 video evidence (with interactive video frame capture/cropping), record and confirm findings, auto-compile reports
- Manager review, publish reports, and Customer report acceptance

**Defect Management**
- Record and classify defects, assign severity
- Track defect lifecycle, attach photo evidence and bounding-box annotations

**Maintenance Work Order Management**
- Create and assign maintenance work orders from confirmed report defects, approve repair budgets and change orders
- Update repair progress with before/after photo proof, conduct 3-way re-inspection defect verification, reconcile costs, close work orders, and maintain history

**AI Services Integration**
- Inspection image and video defect analysis (`DroneVisionAI` — `YOLO11` & Vision LLM fallback)
- Inspection report summarization and maintenance completion report auto-drafting (LLM)
- Engineering repair scope, cost norms, and compliance recommendation (`DroneKnowledgeAI` — `pgvector` RAG)

**Dashboard & Analytics**
- Role-based inspection statistics, defect analytics, maintenance KPIs
- Asset utilization, inspection KPIs, operational reports

#### d) Non-Functional Requirements:
- Responsive Web Application
- Cross-platform Mobile Application (Flutter)
- Modular Monolith & RESTful API Architecture
- JWT Authentication & Google OAuth2
- Role-Based Access Control (RBAC) with Multi-tenant Zone Isolation
- Integration with SmartDroneHub via standardized REST APIs
- PostgreSQL Database with `pgvector` extension
- MinIO Object Storage for photo/MP4 video evidence and inspection documents
- Docker Containerization, Cloud-ready Deployment
- Real-time telemetry polling and asynchronous Transactional Outbox notifications
- Online Payment Gateway integration (`PayOS` VietQR with HMAC-SHA256 webhook verification)
- Audit Logging, Secure File Storage, Scalable and High Availability Architecture

#### e) Theory & Practical:

**Applied Theory**
- Software Engineering: SDLC, Object-Oriented Analysis and Design, Modular Monolith Software Architecture
- Business Process Modeling, Workflow Management, Relational & Vector Database Design
- RESTful API Design, External System Integration (`SmartDroneHub`, `PayOS`, `OAuth2`)
- Mobile Computing, Asynchronous Event-Driven Notification & Telemetry Integration
- AI Integration: Computer Vision (`YOLO11`), LLM-based summarization, and Retrieval-Augmented Generation (`RAG`)
- Software Testing, Automated Verification, Cloud Deployment

**Technologies**
- **Backend:** Java 21, Spring Boot, Spring Modulith, Spring Security, Spring Data JPA / Hibernate, Flyway
- **Frontend:** ReactJS (React 19, TypeScript), Material UI
- **Mobile:** Flutter (Dart, Riverpod, GoRouter, Dio)
- **Database:** PostgreSQL 17 (with `pgvector`)
- **Storage:** MinIO Object Storage
- **AI:** `DroneVisionAI` (Python FastAPI, `YOLO11` & Vision LLM fallback), `DroneKnowledgeAI` (`pgvector` RAG), LLM-based summarization
- **Payment & Auth:** PayOS (VietQR), Google OAuth2
- **Deployment:** Docker, Docker Compose, GitHub Actions CI/CD, Cloud Deployment

#### f) Products (Expected Deliverables):
- SmartDroneInspection Web Portal (ReactJS + Material UI)
- Flutter Mobile Application (Inspector + Maintenance Engineer)
- Asset & Drone Fleet Management Module
- Inspection Planning & Airspace Gate Module
- Inspection Service Request, Quotation, Contract & PayOS Payment Module
- Drone Mission Integration Module (`SmartDroneHub` API)
- Inspection Report & Evidence Module
- Defect Management Module
- Corrective Maintenance Work Order & 3-Way Re-inspection Module
- AI Services: Image & Video Analysis (`YOLO11`), Report Summarization (`LLM`), Engineering & Case Recommendation (`pgvector` RAG)
- Dashboard & Analytics
- RESTful APIs
- Docker Deployment Package
- Software Documentation (Reports 1–5)

#### g) Proposed Tasks:

**Work Package 1 - Requirement Analysis & System Design**
- Requirement analysis, business workflow analysis (`MF1`–`MF4`, `FE-01`–`FE-08`)
- Software architecture design (Spring Modulith), PostgreSQL & `pgvector` database design
- REST API specification, UI/UX design

**Work Package 2 - Asset, Fleet & Inspection Planning**
- User management, 5-role RBAC, partner/customer onboarding, and airspace zone validation
- Asset management and Inspector-owned drone registry module
- Service request, quotation, contract management, inspection scheduling, and notification services

**Work Package 3 - Mission Integration, Report & Maintenance Management**
- Flight permit pre-flight gate and `SmartDroneHub` Mission API integration (telemetry, flight trace, MP4 video & flight report)
- Inspection report management, defect management, and `PayOS` online payment settlement
- Corrective maintenance work order management, 3-way re-inspection verification, and dashboard

**Work Package 4 - Mobile Application & AI Integration**
- Flutter mobile application (Inspector + Maintenance Engineer)
- Photo and MP4 video evidence management (with interactive frame capture/cropping)
- AI services: image & video defect analysis (`YOLO11`), report summarization (`LLM`), engineering & case recommendation (`pgvector` RAG)

**Work Package 5 - Testing & Deployment**
- Unit testing, system integration testing, performance testing, security testing
- Docker containerization and cloud staging deployment
- Software documentation (Reports 1–5), deployment guide

---

## 4. Other comments (propose all relative things if have):
............................................................................................................................................................
............................................................................................................................................................

---

| Supervisor (If have)<br>*(Sign and full name)* | HCM, date 19/08/2026<br>On behalf of Registers<br>*(Sign and full name)* |
| :---: | :---: |
| <br><br><br>**Phạm Minh Trí & Đặng Ngọc Minh Đức** | <br><br><br>**Trần Hoàng Trung Hiếu** |
