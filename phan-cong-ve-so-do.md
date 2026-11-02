# Phân công vẽ sơ đồ dự án SmartDroneInspection (Chuẩn hóa 8 Features, 4 Main Flows & 5 Roles)

Tài liệu căn cứ:
- **Report 1: Project Introduction (Mục 1.2 & 6.1 - 8 Features, 4 Main Flows, 5 Roles & Governance)**
- **Report 2: Project Management Plan (Mục 1.1 WBS, 1.2 Scope & Mục 4 RACI Responsibility Matrix)**
- **Report 3: Software Requirement Specification (Mục 2 User Requirements, Mục 3 Functional Requirements `FE-01`..`FE-08` & Phụ lục 5.1 Business Rules)**
- **Report 4: Software Design Document (Mục 1 Architecture, Mục 2 Database & Mục 3 Detailed Design)**
- Kho mã nguồn sơ đồ: `diagrams/mermaid/` và file vẽ tổng hợp: `diagrams/smartdrone-use-cases.drawio`

> **CẬP NHẬT CHUẨN HÓA (02/11/2026):**
> - Phân bổ chuẩn hóa **4 Main Flows (`MF1` đến `MF4`)**, mỗi Main Flow gồm đúng **2 Features**, mỗi thành viên phụ trách trọn vẹn **1 Main Flow (2 Features)**.
> - Chuẩn hóa 5 role theo mã: `ADMIN`, `MANAGER`, `CUSTOMER`, `INSPECTOR`, `MAINTENANCE_ENGINEER` (không thêm tiền tố `Platform` vào tên role).
> - Tính năng báo cáo kiểm định tập trung vào **biên dịch, xem xét và phê duyệt báo cáo** trực tiếp trên hệ thống; **xuất file PDF là tính năng phụ trợ tải về**, không phải hành động nghiệp vụ chính hay điều kiện tiên quyết.

---

## 1. Phân bổ phạm vi & Tính năng phụ trách (Feature Ownership — 4 Main Flows / 8 Features)

Mỗi thành viên phụ trách **1 Main Flow trọn vẹn (gồm 2 Features)** và các sơ đồ kiến trúc/hệ thống/quy trình tương ứng:

| Thành viên | Mã sinh viên | Main Flow & 2 Feature đảm nhận chính | Trọng tâm sơ đồ đảm nhận |
| :--- | :---: | :--- | :--- |
| **Trần Hoàng Trung Hiếu** | **SE184212** | **MF1 / WF-01 (FE-01 + FE-02)**<br>Customer Airspace & Partner Onboarding, Asset & Drone Registry | System Context, System Architecture, Database ERD, sơ đồ Auth/5-Role RBAC, Quản lý Inspector & hồ sơ bằng lái, danh mục Asset & kiểm tra vùng cấm bay, Đăng ký Drone sở hữu riêng (3 tài liệu) & WF-01 Activity |
| **Phùng Trung Quốc** | **SE170027** | **MF2 / WF-02 (FE-03 + FE-04)**<br>Service Request, VND Quote, Signed Contract & Cross-Org Partner Dispatch | Sơ đồ Yêu cầu dịch vụ định kỳ & sinh đợt bay hợp đồng, Outbox Notifications, Báo giá VND, Order Chat thương thảo, Hợp đồng giấy offline scan, Phân công điều phối Inspector–Drone chống trùng lịch & WF-02 Activity |
| **Trần Tùng Bách** | **SE180220** | **MF3 / WF-03 (FE-05 + FE-06)**<br>Flight Permit, Field Session, YOLO11, Auto-Compiled Report & PayOS Settlement | Cổng giấy phép bay & Phiên bay thực địa (Start/Complete/Abort), Dashboard & Lịch bay, Thu nhận hình ảnh/video streaming MinIO, AI YOLO11 phát hiện khiếm khuyết, Biên dịch & duyệt báo cáo kiểm định, Thanh toán PayOS & WF-03 Activity |
| **Trương Thái Như** | **SE180082** | **MF4 / WF-04 (FE-07 + FE-08)**<br>Corrective Defect Handoff, Work Order, RAG Scope/Cost Norms, 3-Way Re-inspection & Cost Closure | **Use Case Diagram (toàn hệ thống)**, Screens Flow, Backend Package Diagram, Toàn bộ sơ đồ Module Bảo trì, RAG Scope Advisor (TCVN/EN/ISO), RAG Cost Estimator, Vòng lặp Bay lại đối chiếu 3 chiều, Nghiệm thu & Quyết toán & WF-04 Activity |

---

## 2. Chi tiết phân công sơ đồ cho từng thành viên

### 👤 1. Trần Hoàng Trung Hiếu (SE184212) — Chủ nhiệm & Phụ trách MF1 / WF-01
* **Tính năng đảm nhận:**
  - **FE-01: Customer Registration & 5-Role Access Control** (Đăng ký Customer kèm Asset đầu tiên qua cổng kiểm tra vùng cấm bay, Argon2id sign-in, Google OAuth2 Web/Mobile deep-link, JWT/Refresh token rotation, `/users/me`, 5-role RBAC: `ADMIN`, `MANAGER`, `CUSTOMER`, `INSPECTOR`, `MAINTENANCE_ENGINEER`).
  - **FE-02: Partner Inspector & Drone Fleet Management, Asset Registry** (Platform cấp tài khoản Inspector và quản lý hồ sơ/bằng lái phi công, Customer cấp tài khoản kỹ sư bảo trì, danh mục tài sản & cổng chặn vùng cấm bay, đăng ký & xét duyệt Drone thuộc sở hữu Inspector với 3 tài liệu: đăng ký, sở hữu, kiểm định).

| STT | Tên sơ đồ | Loại | Mã tệp Mermaid (`diagrams/mermaid/`) / Vị trí tài liệu |
| :---: | :--- | :---: | :--- |
| 1 | **System Context Diagram** | Context | `01_report-3-..._system-context-diagram_076430d8b186.mmd` *(SRS 1.1)* |
| 2 | **System Architecture Diagram** | Architecture | `29_report-4-..._system-architecture-diagram_1847a5137a52.mmd` *(SDD 1.1)* |
| 3 | **Database Entity Relationship Diagram (ERD)** | ERD | `31_report-4-..._database-entity-relationship-diagram-erd_8100b531f290.mmd` *(SRS 3.1.5 / SDD 2.0)* |
| 4 | **Identity, Onboarding & 5-Role Access Control Class Diagram** | Class | `36_report-4-..._identity-workforce-and-subscription-class-diagra_b306a9c86f64.mmd` *(SDD 3.1.1)* |
| 5 | **User Authentication, Google OAuth2 & Airspace Onboarding Sequence Diagram** | Sequence | `37_report-4-..._user-authentication-sequence-diagram_0a420defa049.mmd` *(SDD 3.1.2)* |
| 6 | **Partner Inspector Provisioning & Customer Workforce Provisioning Sequence Diagram** | Sequence | `38_report-4-..._workforce-provisioning-and-pilot-license-sequenc_f01a93088565.mmd` *(SDD 3.2.2)* |
| 7 | **Asset Registry, Airspace Guard & Inspector-Owned Drone Class Diagram** | Class | `40_report-4-..._asset-drone-fleet-and-drone-equipment-leasing-cl_5efd1e2bdde2.mmd` *(SDD 3.2.1)* |
| 8 | **Inspector Drone 3-Document Registration & Review Sequence Diagram** | Sequence | `41_report-4-..._drone-equipment-leasing-and-fleet-provisioning-s_65adc355e88c.mmd` *(SDD 3.2.4)* |
| 9 | **WF-01 Activity Diagram: Partner & Customer Airspace Onboarding, Asset & Drone Registry** | Activity | `44_report-4-..._wf-01-activity-diagram-enterprise-onboarding-dro_26036e59e988.mmd` *(SDD 3.2.5)* |

---

### 👤 2. Phùng Trung Quốc (SE170027) — Kỹ sư Backend / Mobile & Phụ trách MF2 / WF-02
* **Tính năng đảm nhận:**
  - **FE-03: Service Requests, Recurring Occurrences & Outbox Notifications** (Yêu cầu dịch vụ định kỳ, sinh các đợt kiểm tra `service_request_occurrences` theo phạm vi hợp đồng, và hàng đợi thông báo Outbox đa kênh nội bộ).
  - **FE-04: Service Requests, Quotations, Signed Contracts & Partner Dispatch** (Khách hàng gửi yêu cầu dịch vụ, `MANAGER` phát hành báo giá VND versioned, Order Chat thương thảo hai chiều, ghi nhận bản scan hợp đồng giấy ký offline, phân công điều phối cặp Inspector–Drone cho từng đợt bay có kiểm tra chống trùng lịch liên tổ chức, xử lý điều phối lại sau hủy/hoãn bay, và bản đồ thông tin vùng trời tác nghiệp).

| STT | Tên sơ đồ | Loại | Mã tệp Mermaid (`diagrams/mermaid/`) / Vị trí tài liệu |
| :---: | :--- | :---: | :--- |
| 1 | **Notification Inbox, Recurring Occurrences & Event Listeners Class Diagram** | Class | `42_report-4-..._notification-inbox-and-event-listeners-class-dia_43ef662062fa.mmd` *(SDD 3.3.1)* |
| 2 | **Event-Driven Transactional Outbox Notification Sequence Diagram** | Sequence | `43_report-4-..._event-driven-transactional-outbox-notification-s_0e6cc48673be.mmd` *(SDD 3.3.2)* |
| 3 | **Service Request, Quotation, Signed Contract & Partner Dispatch Class Diagram** | Class | `45_report-4-..._inspection-mission-recurring-schedule-and-permit_e1af3b4245e9.mmd` *(SDD 3.4.1)* |
| 4 | **Service Request Negotiation, Signed Contract & Cross-Org Dispatch Sequence Diagram** | Sequence | `46_report-4-..._mission-dispatch-and-self-service-permit-upload-_4ec4bbad15f8.mmd` *(SDD 3.4.2)* |
| 5 | **Service Request & Quotation Version Lifecycle State Machine Diagram** | State | `36_report-4-..._service-request-quotation-signed-contract-and-pa_dfa67ceebe38.mmd` *(SDD 3.4.4)* |
| 6 | **Contract Occurrence Scheduling & Assignment Sequence Diagram** | Sequence | `37_report-4-..._service-request-negotiation-signed-contract-and-_82246ee7b9d5.mmd` *(SDD 3.4.5)* |
| 7 | **Service Request, Occurrence & PayOS Payment State Machines** | State | `32_report-4-..._subscription-and-drone-equipment-lease-state-mac_d532e1bb2148.mmd` *(SDD 2.0)* |
| 8 | **WF-02 Activity Diagram: Service Request, Quote, Chat, Signed Contract & Partner Dispatch** | Activity | `49_report-4-..._wf-02-activity-diagram-mission-dispatch-flight-p_b38950c713f6.mmd` *(SDD 3.4.3)* |

---

### 👤 3. Trần Tùng Bách (SE180220) — Kỹ sư Full-Stack / AI & Phụ trách MF3 / WF-03
* **Tính năng đảm nhận:**
  - **FE-05: Flight Permit Gate, Field Flight Execution, Dashboard & Calendar** (Cổng kiểm tra giấy phép bay trước khi cất cánh, phiên bay thực địa 2 kết quả Start -> Complete hoặc Abort có ghi lý do, bảng điều khiển vận hành phân quyền 5 role, lịch điều phối bay và thanh tiến độ kiểm định 5 giai đoạn cho khách hàng).
  - **FE-06: Evidence Intake, YOLO11 Detection, Auto-Compiled Report & PayOS Settlement** (Tải ảnh & video MP4 streaming MinIO, trích xuất GPS/EXIF, AI YOLO11 phát hiện khiếm khuyết với Vision LLM fallback, xác nhận finding, tự động biên dịch báo cáo kiểm định `SUBMITTED`, AI Executive Summary, Manager xem xét & phê duyệt báo cáo `PUBLISHED`, Customer nghiệm thu báo cáo và thanh toán VietQR qua PayOS; xuất file PDF là tính năng phụ trợ tải về).

| STT | Tên sơ đồ | Loại | Mã tệp Mermaid (`diagrams/mermaid/`) / Vị trí tài liệu |
| :---: | :--- | :---: | :--- |
| 1 | **Field Flight Session & Operational Dashboard Class Diagram** | Class | `47_report-4-..._flight-session-and-airspace-conflict-evaluatio_13717dfb1191.mmd` *(SDD 3.5.1)* |
| 2 | **Flight Permit Upload Gate & On-Site Field Flight Sequence Diagram** | Sequence | `48_report-4-..._field-execution-flight-logging-and-gps-telemet_4be09fbe7954.mmd` *(SDD 3.5.2)* |
| 3 | **YOLO11 Defect Detection & Finding Verification Class Diagram** | Class | `50_report-4-..._yolo11-defect-detection-and-finding-verification_64eb1d90feeb.mmd` *(SDD 3.6.1)* |
| 4 | **YOLO11 Defect Detection & Verification Sequence Diagram** | Sequence | `51_report-4-..._yolo11-defect-detection-and-verification-sequenc_436962a7b8b8.mmd` *(SDD 3.6.2)* |
| 5 | **Auto-Compiled Inspection Report, Review, Approval & PayOS Class Diagram** | Class | `52_report-4-..._inspection-report-authoring-review-and-pdf-publi_e00807180de7.mmd` *(SDD 3.6.3)* |
| 6 | **Report Synthesis, Manager Review, Approval & PayOS Settlement Sequence Diagram** | Sequence | `53_report-4-..._report-synthesis-review-and-immutable-publicatio_2065932a94b4.mmd` *(SDD 3.6.4)* |
| 7 | **Inspection (6-State) & FieldSession State Machine Diagram** | State | `33_report-4-..._inspection-fieldsession-and-inspectionreport-sta_53a33f372cdf.mmd` *(SDD 2.0)* |
| 8 | **InspectionReport 5-State Lifecycle State Machine Diagram** | State | `34_report-4-..._inspectionreport-version-lifecycle-state-machine_4400d944dca4.mmd` *(SDD 2.0)* |
| 9 | **WF-03 Activity Diagram: Permit Gate, Field Session, YOLO11, Auto-Compiled Report & PayOS** | Activity | `54_report-4-..._wf-03-activity-diagram-ai-defect-detection-repor_c8f1710d6cb7.mmd` *(SDD 3.6.5)* |

---

### 👤 4. Trương Thái Như (SE180082) — Kỹ sư Full-Stack & Phụ trách MF4 / WF-04
* **Tính năng đảm nhận:**
  - **FE-07: Maintenance Work Orders, RAG Scope/Norms Advisor & Repair Execution** (Tiếp nhận lỗi hỏng từ báo cáo kiểm định, pgvector RAG tư vấn tiêu chuẩn TCVN/EN/ISO kèm 1-click khởi tạo task, phân công đội ngũ, RAG gợi ý định mức dự toán, Customer duyệt ngân sách & Change Order, thi công và Team Lead duyệt hàng loạt nhật ký `batch-verify`).
  - **FE-08: Completion Report, 3-Way Re-inspection Verification & Cost Closure** (Tự động soạn báo cáo hoàn thành bảo trì `auto-draft`, RAG thẩm tra tuân thủ nghiệm thu `acceptance-compliance`, vòng lặp bay lại 3 bước kèm đối chiếu 3 chiều `reinspection_defect_verifications`, nghiệm thu độc lập, quyết toán chi phí & đóng Work Order).

| STT | Tên sơ đồ | Loại | Mã tệp Mermaid (`diagrams/mermaid/`) / Vị trí tài liệu |
| :---: | :--- | :---: | :--- |
| 1 | **Use Case Diagram (Toàn hệ thống - Thống nhất 1 sơ đồ hoàn chỉnh)** | Use Case | `02_report-3-..._use-case-diagram_f568970e5ba2.mmd` *(tab "use cases" trong `diagrams/smartdrone-use-cases.drawio` - SRS 2.0)* |
| 2 | **Screens Flow Diagram (8 Features & 5 Roles)** | Screen Flow | `03_report-3-..._screens-flow-diagram_351dade920d7.mmd` *(SRS 3.1.1)* |
| 3 | **Backend Subsystem Package Diagram** | Package | `30_report-4-..._backend-subsystem-package-diagram_0fa0880aa8fb.mmd` *(SDD 1.2)* |
| 4 | **Maintenance Work Order, RAG Advisor, Re-inspection & Cost Control Class Diagram** | Class | `55_report-4-..._maintenance-work-order-rag-advisor-and-cost-cont_8b41a0e47679.mmd` *(SDD 3.7.1)* |
| 5 | **FE-07: Work Order Planning, 1-Click Tasks & AI RAG Scope Advisory Sequence Diagram** | Sequence | `56_report-4-..._maintenance-work-order-rag-re-inspection-and-co_2f3d61b365ff.mmd` *(SDD 3.7.2)* |
| 6 | **FE-07: RAG Cost Norms Estimation, Budget Approval & Change Order Sequence Diagram** | Sequence | `56_...` *(SDD 3.7.3)* |
| 7 | **FE-07: Field Repair Execution & Batch Work Log Verification Sequence Diagram** | Sequence | `56_...` *(SDD 3.7.4)* |
| 8 | **FE-08: Auto-Draft Completion Report, 3-Way Re-inspection, RAG Audit & Closure Sequence Diagram** | Sequence | `56_...` *(SDD 3.8.2)* |
| 9 | **MaintenanceWorkOrder 12-State Lifecycle Diagram** | State | `35_report-4-..._maintenanceworkorder-12-state-lifecycle-diagram_1750d55011cc.mmd` *(SDD 2.0)* |
| 10 | **WF-04 Activity Diagram: Maintenance Work Order, RAG Advisor, 3-Way Re-inspection & Closure** | Activity | `57_report-4-..._wf-04-activity-diagram-maintenance-work-order-li_12bbeb320003.mmd` *(SDD 3.8.3)* |

---

## 3. Tổng hợp số lượng sơ đồ chốt

| Thành viên | Số lượng | Main Flow & Feature đảm nhận (WBS / RACI) | Trọng tâm sơ đồ chính |
| :--- | :---: | :---: | :--- |
| **Trần Hoàng Trung Hiếu** | **9** | **MF1 / WF-01 (FE-01 + FE-02)** | System Context, Architecture, ERD + Auth/RBAC, Partner/Workforce, Asset/Drone & WF-01 Activity |
| **Phùng Trung Quốc** | **8** | **MF2 / WF-02 (FE-03 + FE-04)** | Thông báo Outbox, Yêu cầu dịch vụ, Báo giá VND, Hợp đồng giấy, Phân công điều phối, State Machines & WF-02 Activity |
| **Trần Tùng Bách** | **9** | **MF3 / WF-03 (FE-05 + FE-06)** | Cổng giấy phép bay, Phiên bay thực địa, Dashboards, AI YOLO11, Biên dịch & duyệt báo cáo kiểm định, PayOS & WF-03 Activity |
| **Trương Thái Như** | **10** | **MF4 / WF-04 (FE-07 + FE-08)** | **Use Case tổng hoàn chỉnh**, Screens Flow, Package + Module Bảo trì/RAG, Bay lại 3 chiều, State Machine & WF-04 Activity |
| **TỔNG CỘNG** | **36** | **4 Main Flows / 8 Features** | Phân chia công bằng, gắn liền 100% với 4 Main Flows và đồng bộ Reports 1–5 |
