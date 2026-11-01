# Thiết Kế Cơ Sở Dữ Liệu MF2 Đã Tinh Gọn (Service Request, Quote, Contract & Occurrence)

> **Mục đích:** Tài liệu này mô tả cấu trúc cơ sở dữ liệu đã được **tinh gọn (Simplified)** của **Main Flow 2 (MF2 - Contracts, Quotes & Occurrences)** sau migration `V17__simplify_mf2_schema.sql`.  
> Toàn bộ các bảng trùng lặp với MF1 (`contract_partner_inspectors`, `contract_partner_drones`), các cột tài chính tính toán thừa, cột hợp đồng lặp 2 cấp và các cột write-only đã được loại bỏ.

---

## 1. Tổng quan kết quả tinh gọn (So sánh Trước & Sau `V17`)

| Bảng | Trước `V17` | Sau `V17` | Nội dung tinh gọn |
| :--- | :---: | :---: | :--- |
| `contract_partner_inspectors` | 7 cột | **Đã xóa bảng** | Truy vấn trực tiếp Inspector đối tác (`actor_zone = 'INSPECTOR_PARTNER'`, `status = 'ACTIVE'`, bằng lái còn hạn) từ bảng `users` (MF1). |
| `contract_partner_drones` | 8 cột | **Đã xóa bảng** | Truy vấn trực tiếp Drone đối tác (`inspector_owner_id IS NOT NULL`, `serviceability = 'ACTIVE'`, đăng ký còn hạn) từ bảng `drones` (MF1). |
| `service_requests` | 27 cột | **20 cột (-7)** | Chỉ giữ `contract_object_key`, `contract_uploaded_at`, `accepted_quote_version`. Xóa 5 cột metadata hợp đồng thừa và 2 cột `accepted_by_user_id`, `accepted_at`. |
| `service_request_quotes` | 12 cột | **10 cột (-2)** | Chuẩn hóa 1 cột giá duy nhất `price_per_occurrence_vnd`. Xóa `price_per_occurrence_usd` và `currency`. |
| `service_request_occurrences` | 42 cột | **20 cột (-22)** | Giảm hơn 50% số cột: xóa 8 cột tính toán tài chính (tính động qua `InspectionFinanceCalculator`), xóa 7 cột hợp đồng lặp cấp đợt, xóa 7 cột audit/report/payos write-only. |
| `service_request_messages` | 5 cột | **5 cột** | Giữ nguyên (đã tối giản). |
| `inspection_finance_settings` | 6 cột | **6 cột** | Giữ nguyên (lưu 3 tỷ lệ `commission_rate`, `vat_rate`, `tncn_rate`). |

---

## 2. Sơ đồ thực thể ERD của MF2 (5 Bảng cốt lõi)

```mermaid
erDiagram
    ORGANIZATIONS ||--o{ SERVICE_REQUESTS : "organization_id"
    USERS ||--o{ SERVICE_REQUESTS : "created_by_user_id"
    ASSETS ||--o{ SERVICE_REQUESTS : "asset_id"

    SERVICE_REQUESTS ||--o{ SERVICE_REQUEST_MESSAGES : "request_id"
    USERS ||--o{ SERVICE_REQUEST_MESSAGES : "author_user_id"

    SERVICE_REQUESTS ||--o{ SERVICE_REQUEST_QUOTES : "request_id"
    USERS ||--o{ SERVICE_REQUEST_QUOTES : "issued_by_user_id / inspector_id"
    DRONES ||--o{ SERVICE_REQUEST_QUOTES : "drone_id"
    SERVICE_REQUESTS ||--o| SERVICE_REQUEST_QUOTES : "accepted_quote_version"

    SERVICE_REQUESTS ||--o{ SERVICE_REQUEST_OCCURRENCES : "request_id"
    USERS ||--o{ SERVICE_REQUEST_OCCURRENCES : "inspector_id"
    DRONES ||--o{ SERVICE_REQUEST_OCCURRENCES : "drone_id"
    INSPECTIONS ||--o| SERVICE_REQUEST_OCCURRENCES : "inspection_id"

    USERS ||--o{ INSPECTION_FINANCE_SETTINGS : "updated_by_user_id"

    SERVICE_REQUESTS {
        uuid id PK
        uuid organization_id FK
        uuid asset_id FK
        uuid created_by_user_id FK
        varchar description
        date requested_from
        date requested_until
        varchar timezone
        time window_start
        time window_end
        varchar request_type
        varchar recurrence_unit
        integer recurrence_interval
        integer occurrence_count
        date recurrence_end_date
        varchar status
        integer accepted_quote_version FK
        varchar contract_object_key
        timestamptz contract_uploaded_at
        timestamptz created_at
        timestamptz updated_at
        bigint row_version
    }

    SERVICE_REQUEST_QUOTES {
        uuid id PK
        uuid request_id FK
        integer version_no
        varchar scope_snapshot
        timestamptz first_occurrence_start_at
        timestamptz first_occurrence_end_at
        uuid inspector_id FK
        uuid drone_id FK
        numeric price_per_occurrence_vnd
        uuid issued_by_user_id FK
        timestamptz created_at
    }

    SERVICE_REQUEST_OCCURRENCES {
        uuid id PK
        uuid request_id FK
        integer occurrence_index
        timestamptz planned_start_at
        timestamptz planned_end_at
        varchar status
        uuid inspector_id FK
        uuid drone_id FK
        uuid inspection_id FK_UK
        numeric total_price
        numeric vat_rate
        numeric commission_rate
        numeric tncn_rate
        timestamptz report_accepted_at
        varchar payment_status
        varchar payment_reference
        timestamptz payment_confirmed_at
        bigint payos_order_code UK
        varchar payment_method
        varchar payout_status
        varchar payout_reference
        timestamptz payout_recorded_at
        timestamptz created_at
        timestamptz updated_at
        bigint row_version
    }

    SERVICE_REQUEST_MESSAGES {
        uuid id PK
        uuid request_id FK
        uuid author_user_id FK
        varchar body
        timestamptz created_at
    }

    INSPECTION_FINANCE_SETTINGS {
        uuid id PK
        numeric commission_rate
        numeric vat_rate
        numeric tncn_rate
        uuid updated_by_user_id FK
        timestamptz updated_at
    }
```

---

## 3. Chi tiết các bảng thuộc MF2 (Sau khi tinh gọn)

### 3.1. Bảng `service_requests` (20 cột)
Lưu trữ đơn yêu cầu dịch vụ kiểm định từ Customer (một lần hoặc định kỳ), phiên bản báo giá được chấp nhận và đường dẫn tệp hợp đồng giấy đã ký.

| Tên cột | Kiểu dữ liệu | Ràng buộc | Ý nghĩa nghiệp vụ |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, Default `gen_random_uuid()` | Khóa chính của yêu cầu dịch vụ. |
| `organization_id` | `UUID` | NOT NULL, FK `organizations(id)` | Tổ chức khách hàng sở hữu yêu cầu. |
| `asset_id` | `UUID` | NOT NULL, FK `assets(id, organization_id)` | Công trình/tài sản cần bay kiểm tra. |
| `created_by_user_id` | `UUID` | NOT NULL, FK `users(id, organization_id)` | Đại diện khách hàng tạo yêu cầu. |
| `description` | `VARCHAR(4000)` | NOT NULL | Mô tả phạm vi, yêu cầu kỹ thuật kiểm tra. |
| `requested_from` | `DATE` | NOT NULL | Ngày bắt đầu mong muốn. |
| `requested_until` | `DATE` | NOT NULL | Ngày kết thúc mong muốn (`>= requested_from`). |
| `timezone` | `VARCHAR(64)` | NOT NULL | Múi giờ của công trình (VD: `Asia/Ho_Chi_Minh`). |
| `window_start` | `TIME` | NOT NULL, Default `'08:00'` | Giờ bắt đầu khung thời gian bay trong ngày. |
| `window_end` | `TIME` | NOT NULL, Default `'17:00'` | Giờ kết thúc khung thời gian bay (`> window_start`). |
| `request_type` | `VARCHAR(16)` | NOT NULL, CHECK in (`ONE_TIME`, `RECURRING`) | Loại yêu cầu: 1 lần hay định kỳ nhiều đợt. |
| `recurrence_unit` | `VARCHAR(16)` | CHECK in (`DAY`, `WEEK`, `MONTH`), NULL nếu ONE_TIME | Đơn vị lặp lại cho định kỳ. |
| `recurrence_interval` | `INTEGER` | CHECK `1..52`, NULL nếu ONE_TIME | Khoảng cách chu kỳ. |
| `occurrence_count` | `INTEGER` | CHECK `1..100` | Số lượng đợt bay mong muốn (XOR với `recurrence_end_date`). |
| `recurrence_end_date` | `DATE` | NULL nếu ONE_TIME | Ngày kết thúc chu kỳ định kỳ. |
| `status` | `VARCHAR(24)` | NOT NULL, Default `'OPEN'`, CHECK in (`OPEN`, `QUOTED`, `ACCEPTED`, `CONTRACT_SIGNED`, `ASSIGNED`, `CANCELLED`) | Trạng thái vòng đời yêu cầu dịch vụ. |
| `accepted_quote_version`| `INTEGER` | FK `(id, accepted_quote_version)` $\rightarrow$ `service_request_quotes` | Phiên bản báo giá mà khách hàng đã bấm Accept. |
| `contract_object_key` | `VARCHAR(1000)`| NULL | Đường dẫn lưu trữ file hợp đồng scan trên MinIO (`contracts/requests/{requestId}/{uuid}/{fileName}`). |
| `contract_uploaded_at`| `TIMESTAMPTZ` | NULL | Thời điểm upload hợp đồng hoàn tất. |
| `created_at` / `updated_at` / `row_version` | `TIMESTAMPTZ` / `BIGINT` | NOT NULL | Audit thời gian và khóa lạc quan. |

---

### 3.2. Bảng `service_request_quotes` (10 cột)
Lưu trữ lịch sử các phiên bản báo giá (theo VND) do Manager ban hành.

| Tên cột | Kiểu dữ liệu | Ràng buộc | Ý nghĩa nghiệp vụ |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, Default `gen_random_uuid()` | Khóa chính báo giá. |
| `request_id` | `UUID` | NOT NULL, FK `service_requests(id)` | Liên kết đến yêu cầu dịch vụ. |
| `version_no` | `INTEGER` | NOT NULL, CHECK `> 0`, UNIQUE `(request_id, version_no)` | Số thứ tự phiên bản báo giá (1, 2, 3,...). |
| `scope_snapshot` | `VARCHAR(4000)`| NOT NULL | Snapshot phạm vi công việc cam kết tại báo giá này. |
| `first_occurrence_start_at` | `TIMESTAMPTZ` | NOT NULL | Thời gian bắt đầu dự kiến của đợt đầu tiên. |
| `first_occurrence_end_at` | `TIMESTAMPTZ` | NOT NULL, CHECK `> start_at` | Thời gian kết thúc dự kiến của đợt đầu tiên. |
| `inspector_id` | `UUID` | NOT NULL, FK `users(id)` | Inspector đối tác được đề xuất. |
| `drone_id` | `UUID` | NOT NULL, FK `drones(id)` | Drone đối tác được đề xuất. |
| `price_per_occurrence_vnd` | `NUMERIC(15,2)` | NOT NULL, CHECK `> 0` | Đơn giá trọn gói (đã gồm VAT) cho mỗi đợt bay (VND). |
| `issued_by_user_id` | `UUID` | NOT NULL, FK `users(id)` | Manager ban hành báo giá. |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, Default CURRENT_TIMESTAMP | Thời điểm ban hành báo giá. |

---

### 3.3. Bảng `service_request_occurrences` (20 cột)
Quản lý từng đợt bay trong hợp đồng, liên kết 1-1 sang nhiệm vụ thực địa `inspections` (MF3), lưu 4 tham số gốc tài chính và trạng thái nghiệm thu/thanh toán/chi trả.

| Tên cột | Kiểu dữ liệu | Ràng buộc | Ý nghĩa nghiệp vụ |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, Default `gen_random_uuid()` | Khóa chính đợt kiểm định. |
| `request_id` | `UUID` | NOT NULL, FK `service_requests(id)` | Thuộc yêu cầu / hợp đồng nào. |
| `occurrence_index` | `INTEGER` | NOT NULL, CHECK `> 0`, UNIQUE `(request_id, occurrence_index)` | Số thứ tự đợt kiểm định (1, 2, 3,...). |
| `planned_start_at` | `TIMESTAMPTZ` | NOT NULL | Thời gian bắt đầu bay kế hoạch của đợt. |
| `planned_end_at` | `TIMESTAMPTZ` | NOT NULL, CHECK `> planned_start_at` | Thời gian kết thúc bay kế hoạch của đợt. |
| `status` | `VARCHAR(24)` | NOT NULL, CHECK in (`PENDING_ASSIGNMENT`, `ASSIGNED`, `CANCELLED`) | Trạng thái điều phối của đợt. |
| `inspector_id` | `UUID` | FK `users(id)` | Inspector thực tế được phân công cho đợt này. |
| `drone_id` | `UUID` | FK `drones(id)` | Drone thực tế được phân công cho đợt này. |
| `inspection_id` | `UUID` | UNIQUE, FK `inspections(id)` | Liên kết 1-1 với nhiệm vụ thực địa MF3 sinh ra khi phân công. |
| `total_price` | `NUMERIC(15,2)` | NULL | Tổng giá tiền khách hàng phải trả cho đợt (VND, đã gồm VAT). |
| `vat_rate` | `NUMERIC(5,2)` | NULL | Thuế suất VAT snapshot tại thời điểm chốt báo giá (%). |
| `commission_rate` | `NUMERIC(5,2)` | NULL | Tỷ lệ hoa hồng platform snapshot (%). |
| `tncn_rate` | `NUMERIC(5,2)` | NULL | Thuế suất TNCN khấu trừ snapshot (%). |
| `report_accepted_at` | `TIMESTAMPTZ` | NULL | Thời điểm khách hàng nghiệm thu báo cáo MF3 để mở khóa thanh toán. |
| `payment_status` | `VARCHAR(24)` | NOT NULL, CHECK in (`PENDING`, `PAYMENT_DUE`, `PAID`) | Trạng thái thanh toán từ Khách hàng. |
| `payment_reference` | `VARCHAR(255)` | NULL | Mã giao dịch thanh toán (PayOS / Sao kê ngân hàng). |
| `payment_confirmed_at` | `TIMESTAMPTZ` | NULL | Thời điểm xác nhận thanh toán thành công. |
| `payos_order_code` | `BIGINT` | UNIQUE | Mã đơn hàng 64-bit tích hợp cổng PayOS. |
| `payment_method` | `VARCHAR(30)` | NULL | Phương thức thanh toán (`PAYOS`, `MANUAL_WIRE`). |
| `payout_status` | `VARCHAR(24)` | NOT NULL, CHECK in (`PENDING`, `ELIGIBLE`, `PAID`) | Trạng thái chi trả thù lao cho Inspector. |
| `payout_reference` | `VARCHAR(255)` | NULL | Mã giao dịch chuyển khoản chi trả cho Inspector. |
| `payout_recorded_at` | `TIMESTAMPTZ` | NULL | Thời điểm hoàn tất chi trả cho Inspector. |
| `created_at` / `updated_at` / `row_version` | `TIMESTAMPTZ` / `BIGINT` | NOT NULL | Audit thời gian và khóa lạc quan. |

> **Cơ chế tính toán động từ 4 cột gốc (`total_price`, `vat_rate`, `commission_rate`, `tncn_rate`) qua `InspectionFinanceCalculator`:**
> - `service_base_amount` = $\text{ROUND}(\text{total\_price} / (1 + \text{vat\_rate}/100), 2)$
> - `vat_amount` = $\text{total\_price} - \text{service\_base\_amount}$
> - `commission_amount` = $\text{ROUND}(\text{service\_base\_amount} \times \text{commission\_rate}/100, 2)$
> - `inspector_gross_payout` = $\text{service\_base\_amount} - \text{commission\_amount}$
> - `tncn_amount` = $\text{ROUND}(\text{inspector\_gross\_payout} \times \text{tncn\_rate}/100, 2)$
> - `inspector_net_payout` = $\text{inspector\_gross\_payout} - \text{tncn\_amount}$

---

### 3.4. Bảng `service_request_messages` (5 cột)
Lưu trữ hội thoại thương lượng giữa Customer và Manager trong ngữ cảnh đơn yêu cầu (`id`, `request_id`, `author_user_id`, `body`, `created_at`).

---

### 3.5. Bảng `inspection_finance_settings` (6 cột)
Lưu trữ cấu hình tỷ lệ tài chính toàn hệ thống do Admin quản lý (`id`, `commission_rate`, `vat_rate`, `tncn_rate`, `updated_by_user_id`, `updated_at`).
