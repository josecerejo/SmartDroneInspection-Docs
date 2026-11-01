# Phân công vẽ sơ đồ dự án SmartDroneInspection (Chuẩn hóa 8 Features & 5 Roles)

Tài liệu căn cứ:
- **Report 1: Project Introduction (Mục 1.2 - 8 Features, 5 Roles & Governance)**
- **Report 2: Project Management Plan (Mục 1.1 WBS, 1.2 Scope & Mục 4 RACI Responsibility Matrix)**
- **Report 3: Software Requirement Specification (Mục 2 User Requirements, Mục 3 Functional Requirements `FE-01`..`FE-08` & Phụ lục 5.1 Business Rules)**
- **Report 4: Software Design Document (Mục 1 Architecture, Mục 2 Database & Mục 3 Detailed Design)**
- Kho mã nguồn sơ đồ: `diagrams/mermaid/` và file vẽ tổng hợp: `diagrams/smartdrone-use-cases.drawio`

> ⏰ **CẬP NHẬT ĐỒNG BỘ (01/11/2026):** Đã chuẩn hóa về **8 Features (`FE-01` đến `FE-08` — mỗi thành viên phụ trách 2 Features)** theo mô hình **5 Role (`ADMIN`, `MANAGER`, `CUSTOMER`, `INSPECTOR`, `MAINTENANCE_ENGINEER`)**, loại bỏ Subscription (PayPal) và Drone Leasing khỏi luồng chính.

---

## 1. Phân bổ phạm vi & Tính năng phụ trách (Feature Ownership — 8 Features)

Mỗi thành viên phụ trách **2 Feature lớn** và các sơ đồ kiến trúc/hệ thống tương ứng:

| Thành viên | Mã sinh viên | 2 Feature đảm nhận chính | Trọng tâm sơ đồ đảm nhận |
| :--- | :---: | :--- | :--- |
| **Trần Tùng Bách** | **SE180220** | **FE-01, FE-06** | System Context, System Architecture, Database ERD, sơ đồ Auth (Google OAuth2 & Airspace Onboarding), AI YOLO11, Auto-Compiled Report, AI Executive Summary & PayOS Settlement |
| **Trương Thái Như** | **SE180082** | **FE-07, FE-08** | **Use Case Diagram (toàn hệ thống)**, Screens Flow, Backend Package Diagram, toàn bộ sơ đồ Module Bảo trì, RAG Scope/Norms Advisor, RAG Compliance Audit & Vòng lặp Bay lại đối chiếu 3 chiều (3-Way Re-inspection) |
| **Trần Hoàng Trung Hiếu** | **SE184212** | **FE-02, FE-03** | Toàn bộ 4 State Machine / Lifecycle Diagrams, sơ đồ Tiếp nhận Đối tác Inspector, Đăng ký Drone sở hữu riêng (3 tài liệu), Quản lý Nhân sự Kỹ sư, Lịch định kỳ theo Hợp đồng & Thông báo Outbox |
| **Phùng Trung Quốc** | **SE170027** | **FE-04, FE-05** | Toàn bộ 4 Activity Diagrams (Quy trình nghiệp vụ WF-01..04), sơ đồ Yêu cầu Dịch vụ, Báo giá VND/USD, Order Chat, Hợp đồng giấy, Điều phối chống trùng lịch liên tổ chức, Bản đồ cấm bay, Giấy phép bay & Field Session (Start/Complete/Abort) |

---

## 2. Chi tiết phân công sơ đồ cho từng thành viên

### 👤 1. Trần Tùng Bách (SE180220)
* **Tính năng đảm nhận:**
  - **FE-01: Authentication, Google OAuth2 & 5-Role Access Control** (Đăng ký Customer kèm Asset đầu tiên qua cổng vùng cấm bay, Argon2id sign-in, Google OAuth2 Web/Mobile deep-link, JWT/Refresh token, `/users/me`, 5-role RBAC: `ADMIN`, `MANAGER`, `CUSTOMER`, `INSPECTOR`, `MAINTENANCE_ENGINEER`)
  - **FE-06: Evidence Intake, YOLO11 Detection, Auto-Compiled Report & PayOS** (Tải ảnh & video MP4 streaming MinIO, trích xuất GPS/EXIF, YOLO11 + Vision fallback, xác nhận finding, tự động biên dịch báo cáo `SUBMITTED`, AI Executive Summary, Manager duyệt/xuất PDF bất biến `PUBLISHED`, Customer nghiệm thu & thanh toán VietQR qua PayOS)

| STT | Tên sơ đồ | Loại | Mã tệp Mermaid (`diagrams/mermaid/`) / Vị trí tài liệu |
| :---: | :--- | :---: | :--- |
| 1 | **System Context Diagram** | Context | `01_report-3-..._system-context-diagram_076430d8b186.mmd` *(SRS 1.1)* |
| 2 | **System Architecture Diagram** | Architecture | `29_report-4-..._system-architecture-diagram_1847a5137a52.mmd` *(SDD 1.1)* |
| 3 | **Database Entity Relationship Diagram (ERD)** | ERD | `04_...` / `31_report-4-..._database-entity-relationship-diagram-erd_8100b531f290.mmd` *(SRS 3.1.5 / SDD 2.0)* |
| 4 | **Identity, Onboarding & 5-Role Access Control Class Diagram** | Class | `36_report-4-..._identity-workforce-and-subscription-class-diagra_b306a9c86f64.mmd` *(SDD 3.1.1)* |
| 5 | **User Authentication, Google OAuth2 & Airspace Onboarding Sequence Diagram** | Sequence | `37_report-4-..._user-authentication-sequence-diagram_0a420defa049.mmd` *(SDD 3.1.2)* |
| 6 | **YOLO11 Defect Detection & Finding Verification Class Diagram** | Class | `50_report-4-..._yolo11-defect-detection-and-finding-verification_64eb1d90feeb.mmd` *(SDD 3.6.1)* |
| 7 | **YOLO11 Defect Detection & Verification Sequence Diagram** | Sequence | `51_report-4-..._yolo11-defect-detection-and-verification-sequenc_436962a7b8b8.mmd` *(SDD 3.6.2)* |
| 8 | **Auto-Compiled Inspection Report, Review, PDF Publication & PayOS Class Diagram** | Class | `52_report-4-..._inspection-report-authoring-review-and-pdf-publi_e00807180de7.mmd` *(SDD 3.6.3)* |
| 9 | **Report Auto-Compilation, Manager Publication & PayOS Settlement Sequence Diagram** | Sequence | `53_report-4-..._report-synthesis-review-and-immutable-publicatio_2065932a94b4.mmd` *(SDD 3.6.4)* |

---

### 👤 2. Trương Thái Như (SE180082)
* **Tính năng đảm nhận:**
  - **FE-07: Maintenance Work Orders, RAG Scope/Norms Advisor & Repair Execution** (Tiếp nhận lỗi hỏng, pgvector RAG tư vấn tiêu chuẩn TCVN/EN/ISO kèm 1-click khởi tạo task, phân công đội ngũ, RAG gợi ý định mức dự toán, Customer duyệt ngân sách & Change Order, thi công và Team Lead duyệt hàng loạt nhật ký `batch-verify`)
  - **FE-08: Completion Report, 3-Way Re-inspection Verification & Cost Closure** (Tự động kết xuất báo cáo hoàn thành `auto-draft`, RAG thẩm tra tuân thủ nghiệm thu `acceptance-compliance`, vòng lặp bay lại 3 bước kèm đối chiếu 3 chiều `reinspection_defect_verifications`, nghiệm thu độc lập, quyết toán chi phí & đóng Work Order)

| STT | Tên sơ đồ | Loại | Mã tệp Mermaid (`diagrams/mermaid/`) / Vị trí tài liệu |
| :---: | :--- | :---: | :--- |
| 1 | **Use Case Diagram (Toàn hệ thống - Thống nhất 1 sơ đồ hoàn chỉnh)** | Use Case | `02_report-3-..._use-case-diagram_f568970e5ba2.mmd` *(tab "use cases" trong `diagrams/smartdrone-use-cases.drawio` - SRS 2.0)* |
| 2 | **Screens Flow Diagram (8 Features & 5 Roles)** | Screen Flow | `03_report-3-..._screens-flow-diagram_351dade920d7.mmd` *(SRS 3.1.1)* |
| 3 | **Backend Subsystem Package Diagram** | Package | `30_report-4-..._backend-subsystem-package-diagram_0fa0880aa8fb.mmd` *(SDD 1.2)* |
| 4 | **Maintenance Work Order, RAG Advisor, Re-inspection & Cost Control Class Diagram** | Class | `55_report-4-..._maintenance-work-order-rag-advisor-and-cost-cont_8b41a0e47679.mmd` *(SDD 3.7.1)* |
| 5 | **FE-07: Work Order Planning, 1-Click Tasks & AI RAG Scope Advisory Sequence Diagram** | Sequence | Tách từ `56_...` *(SDD 3.7.2)* |
| 6 | **FE-07: RAG Cost Norms Estimation, Budget Approval & Change Order Sequence Diagram** | Sequence | Tách từ `56_...` *(SDD 3.7.3)* |
| 7 | **FE-07: Field Repair Execution & Batch Work Log Verification Sequence Diagram** | Sequence | Tách từ `56_...` *(SDD 3.7.4)* |
| 8 | **FE-08: Auto-Draft Completion Report, 3-Way Re-inspection, RAG Audit & Closure Sequence Diagram** | Sequence | Tách từ `56_...` *(SDD 3.8.2)* |

---

### 👤 3. Trần Hoàng Trung Hiếu (SE184212)
* **Tính năng đảm nhận:**
  - **FE-02: Partner Onboarding, Workforce, Asset & Inspector Drone Registry** (Tiếp nhận & xét duyệt đối tác Inspector kèm bằng lái & hợp đồng đối tác, Customer cấp tài khoản kỹ sư bảo trì, danh mục tài sản & cổng chặn vùng cấm bay, đăng ký & xét duyệt Drone thuộc sở hữu Inspector với 3 tài liệu: đăng ký, sở hữu, kiểm định)
  - **FE-03: Recurring Schedules, Contract Occurrences & Outbox Notifications** (Lịch kiểm tra định kỳ theo múi giờ, kế thừa hợp đồng dịch vụ cho nhiều đợt thực hiện, thông báo Outbox phi đồng bộ)

| STT | Tên sơ đồ | Loại | Mã tệp Mermaid (`diagrams/mermaid/`) / Vị trí tài liệu |
| :---: | :--- | :---: | :--- |
| 1 | **Service Request, Occurrence & PayOS Payment State Machines** | State | `32_report-4-..._subscription-and-drone-equipment-lease-state-mac_d532e1bb2148.mmd` *(SDD 2.0)* |
| 2 | **Inspection (6-State) & FieldSession State Machine** | State | `33_report-4-..._inspection-fieldsession-and-inspectionreport-sta_53a33f372cdf.mmd` *(SDD 2.0)* |
| 3 | **InspectionReport 5-State Lifecycle State Machine Diagram** | State | `34_report-4-..._inspectionreport-version-lifecycle-state-machine_4400d944dca4.mmd` *(SDD 2.0)* |
| 4 | **MaintenanceWorkOrder 12-State Lifecycle Diagram** | State | `35_report-4-..._maintenanceworkorder-12-state-lifecycle-diagram_1750d55011cc.mmd` *(SDD 2.0)* |
| 5 | **Partner Inspector Application & Customer Workforce Provisioning Sequence Diagram** | Sequence | `38_report-4-..._workforce-provisioning-and-pilot-license-sequenc_f01a93088565.mmd` *(SDD 3.2.2)* |
| 6 | **Partner Contract Approval & Inspector Account Activation Sequence Diagram** | Sequence | `39_report-4-..._paypal-subscription-payment-and-webhook-capture-_18cdcd15e4f4.mmd` *(SDD 3.2.3)* |
| 7 | **Asset Registry, Airspace Guard & Inspector-Owned Drone Class Diagram** | Class | `40_report-4-..._asset-drone-fleet-and-drone-equipment-leasing-cl_5efd1e2bdde2.mmd` *(SDD 3.2.1)* |
| 8 | **Inspector Drone 3-Document Registration & Review Sequence Diagram** | Sequence | `41_report-4-..._drone-equipment-leasing-and-fleet-provisioning-s_65adc355e88c.mmd` *(SDD 3.2.4)* |
| 9 | **Notification Inbox, Recurring Occurrences & Event Listeners Class Diagram** | Class | `42_report-4-..._notification-inbox-and-event-listeners-class-dia_43ef662062fa.mmd` *(SDD 3.3.1)* |
| 10 | **Event-Driven Transactional Outbox Notification Sequence Diagram** | Sequence | `43_report-4-..._event-driven-transactional-outbox-notification-s_0e6cc48673be.mmd` *(SDD 3.3.2)* |

---

### 👤 4. Phùng Trung Quốc (SE170027)
* **Tính năng đảm nhận:**
  - **FE-04: Service Requests, Quotations, Contracts, Dispatch & Airspace Map** (Yêu cầu dịch vụ một lần/định kỳ, báo giá phiên bản VND/USD, Order Chat, chấp thuận báo giá, upload hợp đồng giấy đã ký, phân công cặp Inspector–Drone chống trùng lịch liên tổ chức, điều phối lại khi Abort, bản đồ vùng cấm bay OpenStreetMap/Nominatim)
  - **FE-05: Flight Permit Gate, Field Execution, Dashboard & Calendar** (Cổng tải giấy phép bay, kiểm tra bằng lái, ghi nhận phiên bay thực địa Web/Mobile Start/Complete/Abort, Dashboard phân tích theo 5 vai trò, lịch làm việc Calendar, Customer 5-Stage Progress Tracker)

| STT | Tên sơ đồ | Loại | Mã tệp Mermaid (`diagrams/mermaid/`) / Vị trí tài liệu |
| :---: | :--- | :---: | :--- |
| 1 | **WF-01 Activity Diagram: Partner & Customer Airspace Onboarding, Asset & Drone Registry** | Activity | `44_report-4-..._wf-01-activity-diagram-enterprise-onboarding-dro_26036e59e988.mmd` *(SDD 3.2.5)* |
| 2 | **WF-02 Activity Diagram: Service Request, Quote, Chat, Signed Contract & Partner Dispatch** | Activity | `49_report-4-..._wf-02-activity-diagram-mission-dispatch-flight-p_b38950c713f6.mmd` *(SDD 3.4.3)* |
| 3 | **WF-03 Activity Diagram: Permit Gate, Field Session, YOLO11, Auto-Compiled Report & PayOS** | Activity | `54_report-4-..._wf-03-activity-diagram-ai-defect-detection-repor_c8f1710d6cb7.mmd` *(SDD 3.6.5)* |
| 4 | **WF-04 Activity Diagram: Maintenance Work Order, RAG Advisor, 3-Way Re-inspection & Closure** | Activity | `57_report-4-..._wf-04-activity-diagram-maintenance-work-order-li_12bbeb320003.mmd` *(SDD 3.8.3)* |
| 5 | **Service Request, Quotation, Signed Contract & Partner Dispatch Class Diagram** | Class | `45_report-4-..._inspection-mission-recurring-schedule-and-permit_e1af3b4245e9.mmd` *(SDD 3.4.1)* |
| 6 | **Service Request Negotiation, Signed Contract & Cross-Org Dispatch Sequence Diagram** | Sequence | `46_report-4-..._mission-dispatch-and-self-service-permit-upload-_4ec4bbad15f8.mmd` *(SDD 3.4.2)* |
| 7 | **Flight Permit Gate, Field Session & Abort Dispatch Class Diagram** | Class | `47_report-4-..._field-session-and-evidence-management-class-diag_44ec52e3b942.mmd` *(SDD 3.5.1)* |
| 8 | **Field Flight Session, Abort Alert & Evidence Upload Sequence Diagram** | Sequence | `48_report-4-..._field-flight-session-and-evidence-upload-sequenc_c480adaed363.mmd` *(SDD 3.5.2)* |

---

## 3. Tổng hợp số lượng sơ đồ chốt

| Thành viên | Số lượng | Feature đảm nhận (WBS / RACI) | Trọng tâm sơ đồ chính |
| :--- | :---: | :---: | :--- |
| **Trần Tùng Bách** | **9** | **FE-01, FE-06** | System Context, Architecture, ERD + Luồng Auth/OAuth2, AI YOLO11, Báo cáo tự động & PayOS |
| **Trương Thái Như** | **8** | **FE-07, FE-08** | **Use Case tổng hoàn chỉnh**, Screens Flow, Package + Luồng Bảo trì/RAG & Bay lại 3 chiều |
| **Trần Hoàng Trung Hiếu** | **10** | **FE-02, FE-03** | 4 State Machine lớn + Module Đối tác Inspector, Drone sở hữu riêng, Lịch định kỳ & Thông báo |
| **Phùng Trung Quốc** | **8** | **FE-04, FE-05** | 4 Activity Diagram quy trình lớn (WF-01..04) + Module Hợp đồng Dịch vụ, Dispatch, Giấy phép bay & Field Session |
| **TỔNG CỘNG** | **35** | **8 Features (FE-01..08)** | Phân chia công bằng (2 Features / thành viên), đồng bộ 100% với Reports 1–5 |
