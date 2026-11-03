# PLAN & HƯỚNG DẪN CHỈNH SỬA BẢN ĐĂNG KÝ ĐỀ TÀI (`CAPSTONE PROJECT REGISTER`)

> **Mục đích tài liệu này**: Dùng làm prompt / đặc tả đầu vào cho Agent chỉnh sửa lại file **CAPSTONE PROJECT REGISTER** (bản gốc ngày `19/08/2026`).
> **Nguyên tắc bắt buộc cho Agent thực thi**:
> 1. **Cái nào giữ được là GIỮ NGUYÊN 100% từng câu chữ và bố cục gốc** (không viết lại dài dòng, không tự ý đổi cấu trúc đề mục).
> 2. **Chỉ chỉnh sửa (Replace) đúng các dòng có thay đổi thực tế** theo bảng `Bản gốc (Before)` $\rightarrow$ `Bản sửa (After)` bên dưới.
> 3. Không nhấn mạnh tính năng xuất PDF (PDF chỉ là tính năng phụ). Dùng tên ngắn gọn cho 5 roles: `Administrator (Admin)`, `Inspection Manager (Manager)`, `Customer`, `Inspector`, `Maintenance Engineer`.

---

## I. CÁC PHẦN GIỮ NGUYÊN 100% (KHÔNG ĐƯỢC SỬA)

Agent **giữ nguyên hoàn toàn** nội dung gốc của các mục sau:
1. **Header & Thông tin chung**: `Class: FA26SE112`, `Duration time: from 09/2026 To 03/2027`, `Profession: Software Engineer`, `Specialty: SE`, `Kinds of person make registers: Students`.
2. **Mục `1. Register information for supervisor`**: Giữ nguyên bảng 2 giảng viên (`Phạm Minh Trí`, `Đặng Ngọc Minh Đức`).
3. **Mục `2. Register information for students`**: Giữ nguyên bảng 4 thành viên (`Trần Hoàng Trung Hiếu`, `Phùng Trung Quốc`, `Trương Thái Như`, `Trần Tùng Bách`).
4. **Mục `3.1. Capstone Project name`**:
   - `3.1.1. English: SmartDroneInspection: AI-powered Infrastructure Inspection Management Platform`
   - `3.1.2. Vietnamese: SmartDroneInspection: Nền tảng Quản lý Kiểm tra Hạ tầng bằng Drone tích hợp AI`
5. **Mục `3.2.a) Context`**: **Giữ nguyên 100% cả 5 đoạn văn gốc** (bao gồm cả đoạn giải thích tách biệt `SmartDroneHub` quản lý bay/telemetry với `SmartDroneInspection` quản lý nghiệp vụ kiểm tra, và dòng `Note` về phần cứng của `AiTA Lab`).
6. **Mục `4. Other comments` & Chữ ký cuối trang**: Giữ nguyên.

---

## II. CHI TIẾT CÁC VỊ TRÍ CẦN CHỈNH SỬA (`BEFORE` $\rightarrow$ `AFTER`)

### 1. Mục `3.2.b) Proposed Solutions`

#### 1.1. Đoạn văn mở đầu của `b) Proposed Solutions`
- **Lý do sửa**: Bổ sung luồng thương mại (`quotations and contracts`) và đổi `maintenance tickets` thành `maintenance work orders`.
- **Bản gốc (Before)**:
  ```text
  SmartDroneInspection is designed as a business-oriented inspection management platform rather than a drone control system. The system manages infrastructure assets, inspection requests, inspection planning, reports, defect tracking, and maintenance tickets - while consuming drone operation services from SmartDroneHub through standardized APIs.
  ```
- **Bản sửa (After)**:
  ```text
  SmartDroneInspection is designed as a business-oriented inspection management platform rather than a drone control system. The system manages infrastructure assets, inspection service requests, quotations and contracts, inspection planning, reports, defect tracking, and maintenance work orders - while consuming drone operation services from SmartDroneHub through standardized APIs.
  ```

#### 1.2. Tiểu mục `Human Actors` (trong `b) Proposed Solutions`)
- **Lý do sửa**: Thay role `Viewer` (chỉ xem thụ động) bằng **`Customer`** (khách hàng sở hữu công trình: gửi yêu cầu kiểm tra, duyệt báo giá/báo cáo, thanh toán trực tuyến `PayOS`, duyệt & nghiệm thu lệnh bảo trì); cập nhật ngắn gọn nhiệm vụ của 4 role còn lại.
- **Bản gốc (Before)**:
  ```text
  Human Actors
  ● Administrator - manages users, organizations, asset categories, and system configuration.
  ● Inspection Manager - creates inspection plans, approves requests, assigns inspectors, and reviews reports.
  ● Inspector - reviews assigned inspections, records findings, uploads evidence, and generates reports.
  ● Maintenance Engineer - manages maintenance tickets, updates repair status, and tracks maintenance history.
  ● Viewer - searches inspection records, views dashboards and historical reports.
  ```
- **Bản sửa (After)**:
  ```text
  Human Actors
  ● Administrator (Admin) - manages users, organizations, airspace/registration approvals, asset categories, and system configuration.
  ● Inspection Manager (Manager) - reviews service requests, issues quotations and contracts, schedules inspections, assigns inspectors and drones, and reviews/publishes reports.
  ● Customer - manages organization assets and maintenance staff, submits inspection service requests, accepts quotations and published reports, processes online payments, and approves/accepts maintenance work orders.
  ● Inspector - reviews assigned inspections, uploads flight permits, executes field sessions with SmartDroneHub, uploads photo/video evidence, records findings, submits reports, and verifies re-inspections.
  ● Maintenance Engineer - manages corrective maintenance work orders, updates repair tasks with photo proof, and tracks maintenance history.
  ```

#### 1.3. Tiểu mục `Five Core Subsystems` (trong `b) Proposed Solutions`)
- **Lý do sửa**: Giữ nguyên đúng 5 phân hệ gốc, chỉ bổ sung các từ khóa thực tế (`airspace zones, registered drones`, `quotations & contracts`, `flight videos (video/mp4)`, `PayOS`, `YOLO11`, `pgvector RAG`).
- **Bản gốc (Before)**:
  ```text
  Five Core Subsystems
  1. Asset Management
  Manage infrastructure assets, categories, specifications, locations, technical documents, lifecycle status, and inspection history.
  2. Inspection Planning & Request Management
  Support inspection scheduling, frequency configuration, priority assignment, inspector allocation, and digital request approval workflows.
  3. Drone Mission Integration
  Integrate with SmartDroneHub via REST API to create inspection missions, retrieve telemetry, drone images, and flight logs. SmartDroneInspection acts as a consumer, not a drone controller.
  4. Inspection Report & Defect Management
  Manage inspection reports, findings, evidence, defect classification, severity tracking, repair recommendations, and maintenance ticket lifecycle.
  5. AI-assisted Services
  Three focused AI features integrated within the 15-week project scope:
  ● Inspection Image Analysis - detect potential defects from drone imagery using DroneVisionAI.
  ● Inspection Report Summarization - generate concise summaries from inspection reports using an LLM.
  ● Historical Case Recommendation - suggest similar past inspection cases and guidelines using DroneKnowledgeAI.
  ```
- **Bản sửa (After)**:
  ```text
  Five Core Subsystems
  1. Asset & Fleet Management
  Manage infrastructure assets, airspace zones, categories, specifications, locations, technical documents, registered inspector drones, lifecycle status, and inspection history.
  2. Inspection Planning, Request & Contract Management
  Support one-time and recurring inspection service requests, quotation negotiation, signed contract records, inspection scheduling, frequency configuration, and conflict-checked inspector/drone allocation.
  3. Drone Mission Integration
  Integrate with SmartDroneHub via REST API to create inspection missions, retrieve live telemetry, flight traces, drone images, flight videos (video/mp4), and flight reports. SmartDroneInspection acts as a consumer, not a drone controller.
  4. Inspection Report, Defect & Maintenance Management
  Manage inspection reports, findings, photo/video evidence, online fee settlement (PayOS), defect classification, severity tracking, repair recommendations, and corrective maintenance work order & re-inspection lifecycle.
  5. AI-assisted Services
  Three focused AI features integrated within the 15-week project scope:
  ● Inspection Image & Video Analysis - detect potential defects from drone imagery and flight videos using DroneVisionAI (YOLO11 & Vision LLM fallback).
  ● Inspection Report Summarization - generate concise executive summaries from inspection reports using an LLM.
  ● Historical Case & Engineering Recommendation - suggest repair scopes, cost norms, and compliance guidelines using DroneKnowledgeAI (pgvector RAG).
  ```

---

### 2. Mục `3.2.c) Functional Requirements`
- **Lý do sửa**: Giữ nguyên 10 nhóm chức năng gốc (`Defect Management` và `Dashboard & Analytics` **giữ nguyên 100%**); cập nhật nhẹ nội dung của 8 nhóm còn lại để khớp với tính năng đã hiện thực.
- **Chi tiết từng nhóm cần sửa trong `c) Functional Requirements`**:

1. **Nhóm `User Management`**:
   - **Before**:
     ```text
     User Management
     ● Authentication, authorization, role-based access control
     ● User profiles, audit logs
     ```
   - **After**:
     ```text
     User Management
     ● Authentication, Google OAuth2 login, authorization, 5-role access control (Admin, Manager, Customer, Inspector, Maintenance Engineer)
     ● User profiles, inspector & customer workforce onboarding, audit logs
     ```

2. **Nhóm `Asset Management`**:
   - **Before**:
     ```text
     Asset Management
     ● Create/update assets, manage asset categories and documents
     ● Asset search, asset history, lifecycle tracking
     ```
   - **After**:
     ```text
     Asset Management
     ● Create/update assets, manage asset categories, inspection checkpoints, and documents
     ● Airspace zone validation (No-Fly / Restricted Zones), Inspector-owned drone registration (3-document verification), asset history, and lifecycle tracking
     ```

3. **Nhóm `Inspection Planning`**:
   - **Before**:
     ```text
     Inspection Planning
     ● Create inspection plans, schedule inspections, assign inspectors
     ● Manage inspection calendars, inspection notifications
     ```
   - **After**:
     ```text
     Inspection Planning
     ● Create inspection plans, schedule one-time and recurring inspections, assign conflict-checked inspectors and drones
     ● Manage inspection calendars, flight permit pre-flight gate, and inspection notifications
     ```

4. **Nhóm `Inspection Request Management`**:
   - **Before**:
     ```text
     Inspection Request Management
     ● Create, approve, track, and cancel inspection requests
     ● Inspection request history
     ```
   - **After**:
     ```text
     Inspection Request Management
     ● Create, approve, track, and cancel inspection service requests
     ● Order chat negotiation, versioned quotations, signed contract upload, online payment settlement (PayOS), and request history
     ```

5. **Nhóm `Drone Mission Integration`**:
   - **Before**:
     ```text
     Drone Mission Integration
     ● Create inspection missions via SmartDroneHub Mission API
     ● Retrieve mission status, telemetry, inspection images, and flight reports
     ```
   - **After**:
     ```text
     Drone Mission Integration
     ● Create and control inspection missions (Start, Abort, Complete) via SmartDroneHub Mission API
     ● Retrieve mission status, live telemetry, GPS flight traces, inspection images, flight videos (video/mp4), and flight reports
     ```

6. **Nhóm `Inspection Report Management`**:
   - **Before**:
     ```text
     Inspection Report Management
     ● Create reports, upload evidence, record findings
     ● Approve and archive reports
     ```
   - **After**:
     ```text
     Inspection Report Management
     ● Upload photo and MP4 video evidence (with interactive video frame capture/cropping), record and confirm findings, auto-compile reports
     ● Manager review, publish reports, and Customer report acceptance
     ```

7. **Nhóm `Defect Management`**: **GIỮ NGUYÊN 100%**

8. **Nhóm `Maintenance Ticket Management` $\rightarrow$ Đổi thành `Maintenance Work Order Management`**:
   - **Before**:
     ```text
     Maintenance Ticket Management
     ● Create and assign maintenance tickets
     ● Update repair progress, close tickets, maintain history
     ```
   - **After**:
     ```text
     Maintenance Work Order Management
     ● Create and assign maintenance work orders from confirmed report defects, approve repair budgets and change orders
     ● Update repair progress with before/after photo proof, conduct 3-way re-inspection defect verification, reconcile costs, close work orders, and maintain history
     ```

9. **Nhóm `AI Services Integration`**:
   - **Before**:
     ```text
     AI Services Integration
     ● Inspection image analysis (DroneVisionAI)
     ● Inspection report summarization
     ● Historical case recommendation (DroneKnowledgeAI)
     ```
   - **After**:
     ```text
     AI Services Integration
     ● Inspection image and video defect analysis (DroneVisionAI — YOLO11 & Vision LLM fallback)
     ● Inspection report summarization and maintenance completion report auto-drafting (LLM)
     ● Engineering repair scope, cost norms, and compliance recommendation (DroneKnowledgeAI — pgvector RAG)
     ```

10. **Nhóm `Dashboard & Analytics`**: **GIỮ NGUYÊN 100%**

---

### 3. Mục `3.2.d) Non-Functional Requirements`
- **Lý do sửa**: Giữ nguyên 11/12 dòng gốc; chỉ sửa dòng `SignalR` (do chuyển sang Spring Boot) và bổ sung `pgvector` + `PayOS`.
- **Chỉ sửa các dòng sau trong `d) Non-Functional Requirements`**:
  1. `● PostgreSQL Database` $\rightarrow$ `● PostgreSQL Database with pgvector extension`
  2. `● MinIO Object Storage for evidence and inspection images` $\rightarrow$ `● MinIO Object Storage for photo/MP4 video evidence and inspection documents`
  3. `● SignalR for real-time mission status updates` $\rightarrow$ `● Real-time telemetry polling, asynchronous Transactional Outbox notifications, and PayOS online payment gateway`
  *(9 dòng còn lại trong `d)` giữ nguyên 100%)*

---

### 4. Mục `3.2.e) Theory & Practical`
- **Lý do sửa**: Chuyển công nghệ Backend từ `ASP.NET Core Web API, Entity Framework Core, SignalR` sang **`Java 21, Spring Boot, Spring Modulith, Spring Data JPA / Hibernate, Flyway`** và làm rõ mô hình AI (`YOLO11`, `pgvector RAG`).
- **Trong `Applied Theory`**:
  - Giữ nguyên 5/6 dòng, chỉ sửa dòng thứ 4:
    - **Before**: `● Mobile Computing, Real-time Communication (SignalR)`
    - **After**: `● Mobile Computing, Event-Driven Notification & Telemetry Integration`
- **Trong `Technologies`**:
  - **Before**:
    ```text
    Technologies
    ● Backend: ASP.NET Core Web API, Entity Framework Core, SignalR
    ● Frontend: ReactJS, Material UI
    ● Mobile: Flutter
    ● Database: PostgreSQL
    ● Storage: MinIO
    ● AI: DroneVisionAI, DroneKnowledgeAI, LLM-based summarization
    ● Deployment: Docker, Docker Compose, Cloud Deployment
    ```
  - **After**:
    ```text
    Technologies
    ● Backend: Java 21, Spring Boot, Spring Modulith, Spring Data JPA / Hibernate, Flyway
    ● Frontend: ReactJS, TypeScript, Material UI
    ● Mobile: Flutter
    ● Database: PostgreSQL (with pgvector)
    ● Storage: MinIO
    ● AI: DroneVisionAI (Python FastAPI, YOLO11 & Vision LLM fallback), DroneKnowledgeAI (pgvector RAG), LLM-based summarization
    ● External Integration: SmartDroneHub Mission API, PayOS (VietQR), Google OAuth2
    ● Deployment: Docker, Docker Compose, Cloud Deployment
    ```

---

### 5. Mục `3.2.f) Products (Expected Deliverables)`
- **Lý do sửa**: Giữ nguyên 12/14 dòng gốc, chỉ chỉnh nhẹ 2 dòng tên module:
  1. `● Inspection Request Module` $\rightarrow$ `● Inspection Service Request, Quotation, Contract & PayOS Payment Module`
  2. `● Maintenance Ticket Module` $\rightarrow$ `● Corrective Maintenance Work Order & Re-inspection Module`
  *(12 dòng còn lại trong `f)` giữ nguyên 100%)*

---

### 6. Mục `3.2.g) Proposed Tasks` (Work Packages 1–5)
- **Lý do sửa**: **Giữ nguyên 5 Work Packages gốc** (`WP1`, `WP5` giữ nguyên 100%); chỉ bổ sung vài từ khóa vào `WP2`, `WP3`, `WP4`:
  - **Trong `Work Package 2 - Asset & Inspection Planning`**:
    - **Before**:
      ```text
      ● Asset management module
      ● Inspection planning, inspection request management
      ● Inspection scheduling, notification services
      ```
    - **After**:
      ```text
      ● User management, airspace validation, asset & inspector drone registry module
      ● Service request, quotation, contract management, and inspection planning
      ● Inspection scheduling, notification services
      ```
  - **Trong `Work Package 3 - Mission Integration & Report Management`**:
    - **Before**:
      ```text
      ● SmartDroneHub Mission API integration
      ● Inspection report management, defect management
      ● Maintenance ticket management, dashboard
      ```
    - **After**:
      ```text
      ● Flight permit gate and SmartDroneHub Mission API integration (telemetry, flight trace, MP4 video & flight report)
      ● Inspection report management, defect management, and PayOS payment settlement
      ● Maintenance work order management, 3-way re-inspection verification, and dashboard
      ```
  - **Trong `Work Package 4 - Mobile Application & AI Integration`**:
    - **Before**:
      ```text
      ● Flutter mobile application (Inspector + Maintenance Engineer)
      ● Evidence management
      ● AI services: image analysis, report summarization, case recommendation
      ```
    - **After**:
      ```text
      ● Flutter mobile application (Inspector + Maintenance Engineer)
      ● Photo and MP4 video evidence management (with interactive frame capture/cropping)
      ● AI services: image & video defect analysis (YOLO11), report summarization (LLM), engineering & case recommendation (pgvector RAG)
      ```
