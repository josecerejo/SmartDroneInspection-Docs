---
title: "Report 4 - Database Design"
document_type: report4-sdd-section
weight: 25
source: "report4-software-design-document.docx"
---

## 2. Database Design

The relational database architecture is implemented on PostgreSQL 17 (`pgvector`) with strict foreign key constraints, `ActorZone` and composite tenant boundary checks, optimistic concurrency control (`row_version`), and cryptographic `SHA-256` audit fields. Managed through Flyway migrations `V1`–`V17`, the active schema encompasses identity & onboarding (`MF1`), infrastructure assets & inspector-owned drones (`MF1`), commercial service requests, quotations, contracts & PayOS settlement (`MF2`), 6-state inspection execution & 5-state auto-compiled reporting (`MF3`), and 12-state RAG-assisted maintenance work orders & 3-way re-inspection verification (`MF4`), alongside cross-cutting notifications, audit logs, and the `event_publication` transactional outbox.

```mermaid
%% title: Database Entity Relationship Diagram (ERD)
erDiagram
  organizations ||--o{ users : employs
  users ||--o| prospective_customer_registrations : submits
  users ||--o{ inspector_partner_applications : reviews
  users ||--o| contract_partner_inspectors : partner_profile
  organizations ||--o{ drones : org_owns
  users ||--o{ drones : inspector_owns
  users ||--o{ drone_registration_applications : submits
  drones |o--o{ drone_registration_applications : provisions
  drones ||--o| contract_partner_drones : partner_drone
  users ||--o{ inspection_finance_settings : configures
  organizations ||--o{ assets : owns
  asset_categories ||--o{ assets : categorizes
  assets ||--o{ asset_documents : attaches
  organizations ||--o{ service_requests : requests
  assets ||--o{ service_requests : targets
  service_requests ||--o{ service_request_messages : discusses
  service_requests ||--o{ service_request_quotes : versions
  service_requests ||--o{ service_request_occurrences : materializes
  service_request_occurrences |o--o| inspections : dispatches
  organizations ||--o{ audit_events : records
  organizations ||--o{ notifications : scopes
  users ||--o{ notifications : receives
  users ||--o{ auth_sessions : opens
  organizations ||--o{ inspections : owns
  assets ||--o{ inspections : undergoes
  users ||--o{ inspections : assigned_inspector
  drones ||--o{ inspections : assigned_drone
  organizations ||--o{ recurring_inspection_schedules : schedules
  assets ||--o{ recurring_inspection_schedules : recurs_for
  recurring_inspection_schedules ||--o{ schedule_occurrences : generates
  inspections |o--o{ schedule_occurrences : fulfills
  inspections ||--o{ field_sessions : executes
  inspections ||--o{ evidence : contains
  field_sessions ||--o{ evidence : captures
  inspections ||--o{ findings : records
  evidence ||--o{ findings : locates
  inspections ||--o{ inspection_reports : delivers
  inspections ||--o{ reinspection_defect_verifications : verifies
  findings ||--o{ reinspection_defect_verifications : baseline_defect
  evidence |o--o{ reinspection_defect_verifications : recapture_proof
  organizations ||--o{ maintenance_work_orders : owns
  assets ||--o{ maintenance_work_orders : remediates
  users ||--o{ maintenance_work_orders : governs
  findings ||--o{ maintenance_work_orders : initiates
  inspection_reports ||--o{ maintenance_work_orders : references
  inspections |o--o{ maintenance_work_orders : reinspects
  maintenance_work_orders ||--o{ maintenance_team_members : deploys
  maintenance_work_orders ||--o{ maintenance_tasks : deconstructs
  maintenance_work_orders ||--o{ maintenance_estimate_versions : projects
  maintenance_estimate_versions ||--o{ maintenance_cost_lines : itemizes
  maintenance_tasks ||--o{ maintenance_cost_lines : accrues
  maintenance_work_orders ||--o{ maintenance_change_orders : requests
  maintenance_tasks ||--o{ maintenance_work_logs : tracks
  maintenance_work_orders ||--o{ maintenance_reports : delivers
  maintenance_reports ||--o{ maintenance_acceptance_decisions : accepts
  organizations {
    uuid id PK
    uuid created_by_user_id FK
    timestamptz created_at
    timestamptz updated_at
    varchar legal_name
    varchar display_name
    varchar registration_code
    varchar timezone
    varchar status
    bigint row_version
  }
  users {
    uuid id PK
    uuid organization_id FK
    varchar email
    varchar normalized_email
    varchar full_name
    varchar password_hash
    varchar status
    varchar actor_zone
    integer auth_version
    integer failed_login_count
    timestamptz lockout_until
    boolean must_change_password
    timestamptz last_login_at
    varchar last_login_ip
    timestamptz created_at
    timestamptz updated_at
    boolean vision_fallback_enabled
    varchar phone_number
    varchar avatar_url
    varchar roles
    varchar pilot_license_number
    varchar pilot_license_class
    timestamptz pilot_license_expires_at
    varchar pilot_license_file_key
  }
  auth_sessions {
    uuid id PK
    uuid user_id FK
    varchar client_type
    varchar token_hash
    varchar previous_token_hash
    timestamptz issued_at
    timestamptz expires_at
    timestamptz revoked_at
    varchar revoked_reason
  }
  prospective_customer_registrations {
    uuid id PK
    uuid user_id FK
    varchar organization_name
    varchar organization_code
    uuid asset_category_id FK
    varchar asset_code
    varchar asset_name
    varchar asset_location
    numeric latitude
    numeric longitude
    varchar status
    varchar airspace_classification
    uuid reviewed_by_user_id FK
    timestamptz reviewed_at
    bigint row_version
  }
  inspector_partner_applications {
    uuid id PK
    varchar email
    varchar normalized_email
    varchar full_name
    varchar phone
    varchar pilot_license_number
    varchar pilot_license_class
    date pilot_license_expires_at
    varchar pilot_license_file_key
    varchar partner_contract_file_key
    varchar status
    uuid reviewed_by_user_id FK
    timestamptz reviewed_at
    bigint row_version
  }
  drone_registration_applications {
    uuid id PK
    uuid inspector_user_id FK
    varchar serial_number
    varchar model
    varchar manufacturer
    varchar registration_number
    varchar registration_file_key
    timestamptz registration_expires_at
    varchar ownership_file_key
    varchar inspection_file_key
    varchar status
    uuid drone_id FK
    uuid reviewed_by_user_id FK
    bigint row_version
  }
  contract_partner_inspectors {
    uuid inspector_user_id PK
    uuid registered_by_user_id FK
    varchar status
    timestamptz created_at
    timestamptz updated_at
  }
  contract_partner_drones {
    uuid drone_id PK
    uuid inspector_user_id FK
    uuid registered_by_user_id FK
    varchar status
    timestamptz created_at
    timestamptz updated_at
  }
  drones {
    uuid id PK
    uuid organization_id FK
    uuid inspector_owner_id FK
    varchar serial_number
    varchar model
    varchar manufacturer
    varchar status
    varchar serviceability_status
    varchar registration_number
    timestamptz registration_expires_at
    timestamptz created_at
    timestamptz updated_at
    bigint row_version
  }
  asset_categories {
    uuid id PK
    varchar code
    varchar name
    varchar description
    boolean active
    timestamptz created_at
    timestamptz updated_at
    bigint row_version
  }
  assets {
    uuid id PK
    uuid organization_id FK
    uuid category_id FK
    varchar code
    varchar name
    varchar description
    varchar location
    numeric latitude
    numeric longitude
    jsonb inspection_items
    varchar status
    timestamptz created_at
    timestamptz updated_at
    bigint row_version
  }
  asset_documents {
    uuid id PK
    uuid asset_id FK
    uuid organization_id FK
    uuid uploaded_by_user_id FK
    varchar file_name
    varchar content_type
    bigint size_bytes
    varchar object_key
    character checksum_sha256
    timestamptz created_at
  }
  service_requests {
    uuid id PK
    uuid organization_id FK
    uuid asset_id FK
    uuid created_by_user_id FK
    varchar description
    date requested_from
    date requested_until
    varchar timezone
    varchar request_type
    varchar recurrence_unit
    integer recurrence_interval
    integer occurrence_count
    date recurrence_end_date
    varchar status
    integer accepted_quote_version
    uuid accepted_by_user_id FK
    timestamptz accepted_at
    varchar contract_object_key
    varchar contract_file_name
    varchar contract_content_type
    character contract_checksum_sha256
    bigint row_version
  }
  service_request_messages {
    uuid id PK
    uuid request_id FK
    uuid author_user_id FK
    varchar body
    timestamptz created_at
  }
  service_request_quotes {
    uuid id PK
    uuid request_id FK
    integer version_no
    varchar scope_snapshot
    timestamptz first_occurrence_start_at
    timestamptz first_occurrence_end_at
    uuid inspector_id FK
    uuid drone_id FK
    varchar currency
    numeric price_per_occurrence_vnd
    numeric price_per_occurrence_usd
    uuid issued_by_user_id FK
    timestamptz created_at
  }
  service_request_occurrences {
    uuid id PK
    uuid request_id FK
    uuid organization_id FK
    integer occurrence_index
    timestamptz planned_start_at
    timestamptz planned_end_at
    uuid inspector_id FK
    uuid drone_id FK
    uuid inspection_id FK
    varchar status
    varchar payment_status
    varchar payout_status
    bigint payos_order_code
    varchar payos_payment_link_id
    varchar payment_method
    bigint row_version
  }
  inspection_finance_settings {
    uuid id PK
    numeric commission_rate
    numeric vat_rate
    numeric tncn_rate
    uuid updated_by_user_id FK
    timestamptz updated_at
  }
  recurring_inspection_schedules {
    uuid id PK
    uuid organization_id FK
    uuid asset_id FK
    uuid created_by_user_id FK
    uuid inspector_id FK
    uuid drone_id FK
    varchar timezone
    varchar recurrence_unit
    integer recurrence_interval
    timestamptz anchor_start_at
    bigint duration_seconds
    integer reminder_days
    timestamptz ends_at
    bigint next_occurrence
    varchar status
    bigint row_version
  }
  schedule_occurrences {
    uuid id PK
    uuid schedule_id FK
    uuid organization_id FK
    uuid inspection_id FK
    bigint occurrence_index
    varchar occurrence_key
    timestamptz planned_start_at
    timestamptz planned_end_at
    varchar status
    varchar blocked_reason
    integer retry_count
    bigint row_version
  }
  inspections {
    uuid id PK
    uuid asset_id FK
    uuid organization_id FK
    uuid inspector_id FK
    uuid drone_id FK
    uuid recurring_schedule_id FK
    varchar inspection_type
    uuid work_order_id FK
    uuid source_inspection_id FK
    uuid source_report_version_id FK
    varchar status
    timestamptz planned_start_at
    timestamptz planned_end_at
    varchar flight_permit_file_key
    varchar flight_permit_file_name
    timestamptz flight_permit_uploaded_at
    timestamptz findings_confirmed_at
    varchar findings_snapshot_hash
    bigint row_version
  }
  field_sessions {
    uuid id PK
    uuid inspection_id FK
    varchar status
    timestamptz started_at
    timestamptz ended_at
    varchar abort_reason
    varchar pre_flight_checklist_note
    varchar outcome_notes
    bigint row_version
  }
  evidence {
    uuid id PK
    uuid inspection_id FK
    uuid field_session_id FK
    varchar file_name
    varchar content_type
    bigint size_bytes
    varchar object_key
    timestamptz capture_time
    numeric latitude
    numeric longitude
    varchar location_description
    boolean is_deleted
  }
  findings {
    uuid id PK
    uuid inspection_id FK
    uuid evidence_id FK
    varchar finding_code
    varchar defect_label
    varchar severity
    varchar status
    varchar source
    numeric confidence
    jsonb bounding_box
    varchar component
    varchar location_description
    varchar technical_notes
    varchar recommended_action
    timestamptz forwarded_to_maintenance_at
    boolean is_deleted
  }
  inspection_reports {
    uuid id PK
    uuid inspection_id FK
    uuid author_user_id FK
    uuid reviewer_user_id FK
    integer version_no
    varchar status
    timestamptz submitted_at
    timestamptz reviewed_at
    timestamptz published_at
    varchar review_reason
    varchar artefact_object_key
    character artefact_checksum_sha256
    bigint row_version
  }
  reinspection_defect_verifications {
    uuid id PK
    uuid reinspection_id FK
    uuid source_finding_id FK
    uuid new_evidence_id FK
    varchar resolution_status
    varchar inspector_notes
    varchar repair_proof_url
    varchar repair_engineer_notes
    timestamptz created_at
    timestamptz updated_at
  }
  maintenance_work_orders {
    uuid id PK
    uuid organization_id FK
    uuid asset_id FK
    uuid source_report_version_id FK
    uuid source_finding_id FK
    uuid reinspection_id FK
    uuid reinspection_report_version_id FK
    uuid owner_user_id FK
    uuid budget_approver_user_id FK
    uuid team_lead_user_id FK
    uuid report_author_user_id FK
    uuid accepting_reviewer_user_id FK
    varchar status
    varchar priority
    timestamptz due_at
    varchar corrective_scope
    varchar acceptance_criteria
    bigint row_version
  }
  maintenance_team_members {
    uuid id PK
    uuid work_order_id FK
    uuid engineer_user_id FK
    uuid assigned_by_user_id FK
    varchar member_role
    boolean active
    timestamptz created_at
  }
  maintenance_tasks {
    uuid id PK
    uuid work_order_id FK
    uuid assigned_engineer_user_id FK
    integer task_number
    varchar name
    varchar method
    timestamptz planned_start_at
    timestamptz planned_end_at
    varchar acceptance_criteria
    varchar status
    bigint row_version
  }
  maintenance_estimate_versions {
    uuid id PK
    uuid work_order_id FK
    uuid prepared_by_user_id FK
    uuid approved_by_user_id FK
    integer version_no
    varchar status
    timestamptz approved_at
    character currency
    numeric baseline_total
    varchar assumptions
    timestamptz created_at
  }
  maintenance_cost_lines {
    uuid id PK
    uuid work_order_id FK
    uuid estimate_version_id FK
    uuid task_id FK
    uuid entered_by_user_id FK
    varchar line_kind
    varchar state
    varchar description
    numeric quantity
    varchar unit
    numeric unit_rate
    numeric amount
    character currency
  }
  maintenance_change_orders {
    uuid id PK
    uuid work_order_id FK
    uuid requested_by_user_id FK
    uuid decided_by_user_id FK
    integer change_number
    varchar reason
    numeric proposed_delta
    varchar status
    timestamptz decided_at
    varchar decision_reason
    bigint row_version
  }
  maintenance_work_logs {
    uuid id PK
    uuid work_order_id FK
    uuid task_id FK
    uuid engineer_user_id FK
    timestamptz started_at
    timestamptz ended_at
    numeric hours
    varchar as_left_condition
    varchar test_readings
    varchar status
    bigint row_version
  }
  maintenance_reports {
    uuid id PK
    uuid work_order_id FK
    integer version_no
    varchar status
    timestamptz author_verified_at
    text content_snapshot
    varchar rendered_object_key
    character rendered_checksum_sha256
    timestamptz created_at
  }
  maintenance_acceptance_decisions {
    uuid id PK
    uuid work_order_id FK
    uuid report_version_id FK
    uuid reviewer_user_id FK
    varchar decision
    varchar technical_comments
    varchar acceptance_checklist
    varchar test_result
    timestamptz decided_at
  }
  repair_knowledge_chunks {
    uuid id PK
    varchar standard_code
    varchar title
    varchar category
    text content
    vector embedding
  }
  notifications {
    uuid id PK
    uuid recipient_user_id FK
    uuid organization_id FK
    varchar event_type
    varchar title
    varchar body
    varchar target_path
    varchar status
    varchar deduplication_key
    timestamptz created_at
  }
  audit_events {
    uuid id PK
    uuid organization_id FK
    uuid actor_user_id FK
    varchar action
    varchar aggregate_type
    uuid aggregate_id
    varchar before_status
    varchar after_status
    jsonb safe_metadata
    timestamptz created_at
  }
  event_publication {
    uuid id PK
    text listener_id
    text event_type
    text serialized_event
    timestamptz publication_date
    timestamptz completion_date
    text status
  }
```

**Table Descriptions**

| No | Table | Description |
| :---: | :--- | :--- |
| 01 | `organizations` | Stores customer organizations (`ActorZone.CUSTOMER_ORGANIZATION`) that own assets, commission inspection service contracts, and govern maintenance work orders.<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `created_by_user_id` references `users(id)` |
| 02 | `users` | Stores system user accounts across the 5 canonical roles (`ADMIN`, `MANAGER`, `CUSTOMER`, `INSPECTOR`, `MAINTENANCE_ENGINEER`), `actor_zone` (`PLATFORM`, `CUSTOMER_ORGANIZATION`, `INSPECTOR_PARTNER`, `PROSPECT_CUSTOMER`), account status (`ACTIVE`, `SUSPENDED`, `DISABLED`), and remote pilot license credentials (`V7`).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `organization_id` references `organizations(id)` |
| 03 | `auth_sessions` | Tracks active user login sessions (`WEB`, `MOBILE`), hashed refresh tokens, expiration timestamps, and revocation status.<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `user_id` references `users(id)` |
| 04 | `prospective_customer_registrations` | Holds prospective customer onboarding records and initial asset coordinates when airspace evaluation returns `RESTRICTED_ZONE` (`PENDING`, `APPROVED`, `REJECTED` — `V7`).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `user_id` references `users(id)`, `asset_category_id` references `asset_categories(id)`, `reviewed_by_user_id` references `users(id)` |
| 05 | `inspector_partner_applications` | Tracks partner Inspector onboarding applications, pilot license metadata, uploaded license file keys, and executed offline partner contract keys (`partner_contract_file_key` — `V7`).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `reviewed_by_user_id` references `users(id)` |
| 06 | `drone_registration_applications` | Stores partner Inspector owned-drone registration applications requiring 3 mandatory document keys (`registration_file_key`, `ownership_file_key`, `inspection_file_key` — `V7`).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `inspector_user_id` references `users(id)`, `drone_id` references `drones(id)`, `reviewed_by_user_id` references `users(id)` |
| 07 | `drones` | Catalogs aircraft scoped either to a partner Inspector (`inspector_owner_id`) or a customer organization (`organization_id`), enforcing `ck_drones_owner_scope` and global serial uniqueness (`V7`).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `inspector_owner_id` references `users(id)`, `organization_id` references `organizations(id)` |
| 08 | `asset_categories` | Global structural categorization catalog for infrastructure assets managed by `ADMIN`.<br>- Primary keys: `id` (UUID)<br>- Foreign keys: None |
| 09 | `assets` | Manages physical infrastructure assets (`ACTIVE`, `INACTIVE`, `RETIRED`), GPS coordinates verified against No-Fly Zones, and `inspection_items` (`jsonb` array of structural checkpoints).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `category_id` references `asset_categories(id)`, `organization_id` references `organizations(id)` |
| 10 | `asset_documents` | Engineering schematics, structural drawings, and technical specifications attached to an asset with 64-character `SHA-256` deduplication.<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `asset_id` references `assets(id)`, `uploaded_by_user_id` references `users(id)` |
| 11 | `contract_partner_inspectors` & `contract_partner_drones` | Registry tables linking approved partner Inspectors and inspector-owned Drones into the commercial contract assignment pool (`ACTIVE`, `INACTIVE` — `V8`, `V9`).<br>- Primary keys: `inspector_user_id` / `drone_id` (UUID)<br>- Foreign keys: `registered_by_user_id` references `users(id)` |
| 12 | `service_requests` | Commercial inspection service requests (`ONE_TIME`, `RECURRING`) tracking lifecycle status (`OPEN`, `QUOTED`, `ACCEPTED`, `CONTRACT_SIGNED`, `ASSIGNED`, `CANCELLED`), accepted quote version, and uploaded signed paper contract scan (`PDF`, `DOCX`, `JPEG`, `PNG` with `SHA-256` — `V8`, `V12`).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `organization_id` references `organizations(id)`, `asset_id` references `assets(id)`, `created_by_user_id` references `users(id)`, `accepted_by_user_id` references `users(id)`, `contract_uploaded_by_user_id` references `users(id)` |
| 13 | `service_request_messages` | In-context order chat messages exchanged between `CUSTOMER` and `MANAGER` during service request and quote negotiation (`V8`).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `request_id` references `service_requests(id)`, `author_user_id` references `users(id)` |
| 14 | `service_request_quotes` | Versioned commercial quotations (`version_no`) recording scope snapshot, proposed schedule, partner `inspector_id`, inspector-owned `drone_id`, currency (`VND`, `USD`), and price per occurrence (`V8`, `V12`).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `request_id` references `service_requests(id)`, `inspector_id` references `users(id)`, `drone_id` references `drones(id)`, `issued_by_user_id` references `users(id)` |
| 15 | `service_request_occurrences` | Individual inspection delivery occurrences (`PENDING_ASSIGNMENT`, `ASSIGNED`, `CANCELLED`) tracking inherited/attached contracts, `payos_order_code`, `payos_payment_link_id`, `payment_status` (`PENDING`, `PAYMENT_DUE`, `PAID`), and `payout_status` (`PENDING`, `ELIGIBLE`, `PAID` — `V8`, `V12`, `V13`).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `request_id` references `service_requests(id)`, `inspector_id` references `users(id)`, `drone_id` references `drones(id)`, `inspection_id` references `inspections(id)` |
| 16 | `inspection_finance_settings` | Platform financial rate configuration (`commission_rate`, `vat_rate`, `tncn_rate`) governing VND quote settlement and partner net payout calculations (`V12`).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `updated_by_user_id` references `users(id)` |
| 17 | `inspections` | Core inspection mission table tracking 6-state canonical lifecycle status (`SCHEDULED`, `IN_PROGRESS`, `FIELD_COMPLETED`, `UNDER_REVIEW`, `COMPLETED`, `CANCELLED` — `V15`), `inspection_type` (`INITIAL`, `RE_INSPECTION` — `V10`), partner assignment flag, flight permit attributes, and source Work Order linkage.<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `asset_id` references `assets(id)`, `drone_id` references `drones(id)`, `inspector_id` references `users(id)`, `organization_id` references `organizations(id)`, `work_order_id` references `maintenance_work_orders(id)`, `source_inspection_id` references `inspections(id)` |
| 18 | `recurring_inspection_schedules` & `schedule_occurrences` | Timezone-anchored repeating inspection rules (`WEEK`, `MONTH`, `YEAR`) and generated/blocked/skipped occurrence records (`V4`).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `organization_id` references `organizations(id)`, `asset_id` references `assets(id)`, `inspection_id` references `inspections(id)` |
| 19 | `field_sessions` | Records individual on-site flight survey sessions, pre-flight safety checklist notes, abort reasons, and operational outcomes (`PLANNED`, `IN_PROGRESS`, `FIELD_COMPLETED`, `ABORTED`; historical `POSTPONED` read-only).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `inspection_id` references `inspections(id)` |
| 20 | `evidence` | Digital photo and `video/mp4` captures collected during field sessions with MinIO object keys, EXIF capture timestamps, GPS coordinates, location descriptions, and soft-delete flag (`is_deleted`).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `field_session_id` references `field_sessions(id)`, `inspection_id` references `inspections(id)` |
| 21 | `findings` | Unified defect findings table managing `YOLO11` / Vision fallback candidates (`PENDING`) and Inspector-confirmed findings (`CONFIRMED`) with bounding boxes and maintenance forwarding timestamps.<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `evidence_id` references `evidence(id)`, `inspection_id` references `inspections(id)` |
| 22 | `inspection_reports` | Versioned inspection report deliverables with 5 canonical states (`SUBMITTED`, `RETURNED`, `APPROVED`, `PUBLISHED`, `SUPERSEDED` — `V16`, `V17`), auto-compiled from confirmed findings and rendered to immutable `SHA-256` PDFs.<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `author_user_id` references `users(id)`, `reviewer_user_id` references `users(id)`, `inspection_id` references `inspections(id)` |
| 23 | `reinspection_defect_verifications` | Three-way comparative defect verification records (`V10`, `V14`) linking a `RE_INSPECTION` mission to each original `source_finding_id`, engineer `repair_proof_url` and `repair_engineer_notes`, drone `new_evidence_id`, and `resolution_status` (`RESOLVED`, `UNRESOLVED`, `INCONCLUSIVE`).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `reinspection_id` references `inspections(id)`, `source_finding_id` references `findings(id)`, `new_evidence_id` references `evidence(id)` |
| 24 | `maintenance_work_orders` | Remediation projects initiated from confirmed published findings, tracking corrective scope, acceptance criteria, team role assignments, `reinspection_id`, `reinspection_report_version_id`, and 12-state lifecycle status (`V6`, `V10`).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `asset_id` references `assets(id)`, `organization_id` references `organizations(id)`, `source_finding_id` references `findings(id)`, `source_report_version_id` references `inspection_reports(id)`, `reinspection_id` references `inspections(id)`, `reinspection_report_version_id` references `inspection_reports(id)` |
| 25 | `maintenance_team_members` & `maintenance_tasks` | Engineering team members (`LEAD`, `REPORT_AUTHOR`, `MEMBER`) and decomposed repair tasks (`PLANNED`, `READY`, `IN_PROGRESS`, `PAUSED_FOR_CHANGE`, `WORK_COMPLETED`, `REWORK_REQUIRED`, `ACCEPTED`, `CANCELLED`).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `work_order_id` references `maintenance_work_orders(id)`, `engineer_user_id` / `assigned_engineer_user_id` references `users(id)` |
| 26 | `maintenance_estimate_versions`, `maintenance_cost_lines` & `maintenance_change_orders` | Versioned repair budgets (`DRAFT`, `SUBMITTED`, `APPROVED`, `REJECTED`, `SUPERSEDED`), itemized cost rows (`LABOR`, `MATERIAL`, `EQUIPMENT`, `SERVICE`, `CONTINGENCY`), and Change Order variance requests.<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `work_order_id` references `maintenance_work_orders(id)` |
| 27 | `maintenance_work_logs`, `maintenance_reports` & `maintenance_acceptance_decisions` | Field execution logs (`IN_PROGRESS`, `PAUSED_FOR_CHANGE`, `SUBMITTED`, `VERIFIED`), auto-drafted completion reports rendered to PDF, and independent `CUSTOMER` acceptance decisions (`ACCEPTED`, `REWORK_REQUIRED`, `REINSPECTION_REQUIRED`).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `work_order_id` references `maintenance_work_orders(id)` |
| 28 | `repair_knowledge_chunks` | Civil and structural engineering repair standard chunks (`TCVN`, `ACI`, `EN`, `ISO`, `ASTM`) and 1536-dim `pgvector` embeddings supporting RAG scope, cost norm, and compliance advisors.<br>- Primary keys: `id` (UUID)<br>- Foreign keys: None |
| 29 | `notifications`, `audit_events` & `event_publication` | Deduplicated in-app notifications (`V5`), append-only security/workflow audit trail, and Spring Modulith transactional event outbox.<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `organization_id` references `organizations(id)`, `recipient_user_id` / `actor_user_id` references `users(id)` |

---

**Main Domain Entity State Machine Diagrams**

Every lifecycle entity in `SmartDroneInspection-backend` is governed by an explicit state machine with guarded domain methods.

**1. Service Request, Contract Occurrence & PayOS Payment State Machines**

```mermaid
%% title: Service Request, Contract Occurrence and PayOS Payment State Machines
stateDiagram-v2
  direction LR
  state "Service Request (service_requests.status)" as ReqSM {
    [*] --> REQ_OPEN : createRequest() [FE-04]
    REQ_OPEN --> REQ_QUOTED : issueQuote(VND/USD) [FE-04]
    REQ_QUOTED --> REQ_QUOTED : issueQuote(versionNo + 1) [FE-04]
    REQ_QUOTED --> REQ_ACCEPTED : acceptQuote(versionNo) [FE-04]
    REQ_ACCEPTED --> REQ_CONTRACT_SIGNED : uploadSignedContract(SHA-256) [FE-04]
    REQ_CONTRACT_SIGNED --> REQ_ASSIGNED : assignOccurrences() [FE-04]
    REQ_OPEN --> REQ_CANCELLED : cancel() [FE-04]
    REQ_QUOTED --> REQ_CANCELLED : cancel() [FE-04]
    REQ_ASSIGNED --> [*]
    REQ_CANCELLED --> [*]
  }

  state "Occurrence Payment & Payout (service_request_occurrences)" as PaySM {
    [*] --> PAY_PENDING : occurrenceCreated() [FE-03, FE-04]
    PAY_PENDING --> PAYMENT_DUE : customerAcceptsReport() [FE-06]
    PAYMENT_DUE --> PAID : payOSWebhookVerified() / confirmPayment() [FE-06]
    PAID --> PAYOUT_ELIGIBLE : unlockPartnerPayout() [FE-06]
    PAYOUT_ELIGIBLE --> PAYOUT_PAID : recordPayout() [FE-06]
    PAYOUT_PAID --> [*]
  }
```

| Domain Entity | Lifecycle States & Key Transitions | Business Rule Guards |
| --- | --- | --- |
| **Onboarding Applications**<br>(`ProspectiveCustomerRegistration`, `InspectorPartnerApplication`, `DroneRegistrationApplication`) | - **States**: `PENDING`, `APPROVED`, `REJECTED`<br>- **Customer Airspace**: `NO_FLY_ZONE` rejected immediately (`403`); `RESTRICTED_ZONE` $\rightarrow$ `PENDING`; `CLEAR_ZONE` auto-approved<br>- **Partner & Drone**: `/approve` (`-> APPROVED`), `/reject` (`-> REJECTED`) | - Partner Inspector approval requires `partnerContractFileKey`.<br>- Drone approval requires all 3 files (`REGISTRATION`, `OWNERSHIP`, `INSPECTION`) and provisions `Drone` (`inspector_owner_id`). |
| **Service Request & Quote**<br>(`ServiceRequestStatus`) | - **States**: `OPEN`, `QUOTED`, `ACCEPTED`, `CONTRACT_SIGNED`, `ASSIGNED`, `CANCELLED`<br>- **Transitions**: `/quotes` (`-> QUOTED`), `/accept` (`-> ACCEPTED`), `/signed-contract` (`-> CONTRACT_SIGNED`), `/assign` (`-> ASSIGNED`) | - Quote drone must belong to the selected partner Inspector (`inspector_owner_id`).<br>- Recurring occurrences inherit the parent request's signed paper contract (Decision D2). |
| **Occurrence Payment & Payout**<br>(`OccurrencePaymentStatus`, `PayoutStatus`) | - **Payment States**: `PENDING` $\rightarrow$ `PAYMENT_DUE` $\rightarrow$ `PAID`<br>- **Payout States**: `PENDING` $\rightarrow$ `ELIGIBLE` $\rightarrow$ `PAID`<br>- **Transitions**: `/accept` (`-> PAYMENT_DUE`), `/payos/create-payment-link` & `/webhooks/payos` (`-> PAID`), `/record-payout` (`-> PAID`) | - Customer PDF report download requires `payment_status = PAID` (`402 Payment Required` when `PAYMENT_DUE`).<br>- Net payout deducts platform commission and PIT/TNCN withholding per `inspection_finance_settings`. |
| **Asset & Drone Fleet**<br>(`AssetStatus`, `DroneStatus`) | - **Asset States**: `ACTIVE`, `INACTIVE`, `RETIRED`<br>- **Drone States**: `AVAILABLE` / `ACTIVE`, `MAINTENANCE`, `SUSPENDED`, `RETIRED`<br>- **Transitions**: `/retire` (`-> RETIRED`), `/serviceability` | - Asset creation in a `NO_FLY_ZONE` is blocked.<br>- Only `ACTIVE` assets and `ACTIVE` inspector-owned drones can be dispatched. |

**2. Inspection, FieldSession, Finding & InspectionReport State Machines**

```mermaid
%% title: Inspection, FieldSession and InspectionReport State Machine Diagram
stateDiagram-v2
  direction TB
  [*] --> SCHEDULED : assignOccurrence / createInspection(inspectorId, droneId) [FE-04]
  SCHEDULED --> IN_PROGRESS : startFieldSession(preFlightNote) [FE-05] (requires hasFlightPermit())
  IN_PROGRESS --> SCHEDULED : abortSession(reason) [FE-05] (notifies MANAGER)
  IN_PROGRESS --> FIELD_COMPLETED : completeSession(outcomeNotes) [FE-05]
  FIELD_COMPLETED --> IN_PROGRESS : startAdditionalSession() [FE-05]
  FIELD_COMPLETED --> UNDER_REVIEW : autoCompileAndSubmitReport() [FE-06]
  UNDER_REVIEW --> FIELD_COMPLETED : returnReport(reason) / withdraw() [FE-06]
  UNDER_REVIEW --> COMPLETED : publishReport() (PDF + SHA-256) [FE-06]
  SCHEDULED --> CANCELLED : cancel() [FE-04]
  COMPLETED --> [*]
  CANCELLED --> [*]
```

```mermaid
%% title: InspectionReport Version Lifecycle State Machine Diagram
stateDiagram-v2
  direction LR
  [*] --> SUBMITTED : submitReport (auto-compiled from confirmed findings) [FE-06]
  SUBMITTED --> RETURNED : reviewBy(approve=false, reason) [FE-06]
  SUBMITTED --> RETURNED : withdraw() (before review decision) [FE-06]
  RETURNED --> SUBMITTED : submit() (after re-confirming findings) [FE-06]
  SUBMITTED --> APPROVED : reviewBy(approve=true) [FE-06]
  APPROVED --> PUBLISHED : publish() (renders PDF to MinIO) [FE-06]
  PUBLISHED --> SUPERSEDED : newer version PUBLISHED [FE-06]
  PUBLISHED --> [*]
  SUPERSEDED --> [*]
```

| Domain Entity | Lifecycle States & Key Transitions | Business Rule Guards |
| --- | --- | --- |
| **Inspection Mission**<br>(`InspectionStatus` — 6 Canonical States `V15`) | - **States**: `SCHEDULED`, `IN_PROGRESS`, `FIELD_COMPLETED`, `UNDER_REVIEW`, `COMPLETED`, `CANCELLED`<br>- **Key Steps**: Dispatch (`-> SCHEDULED`), Field Session (`-> IN_PROGRESS -> FIELD_COMPLETED`), Auto-Compile & Submit Report (`-> UNDER_REVIEW`), Publish (`-> COMPLETED`) | - Flight readiness verified via permit on file (`hasFlightPermit()`) and active pilot licensing.<br>- Findings confirmation and report auto-compilation occur in `FIELD_COMPLETED`; publication moves directly to `COMPLETED`. |
| **Field Session**<br>(`FieldSessionStatus`) | - **States**: `PLANNED`, `IN_PROGRESS`, `FIELD_COMPLETED`, `ABORTED` (historical `POSTPONED` retained for read-only history)<br>- **Transitions**: Start (`/field-sessions`), Abort (`/abort`), Complete (`/completion`) | - Requires non-blank `preFlightChecklistNote` on start and `outcomeNotes` on completion.<br>- Aborting a session returns the inspection to `SCHEDULED` and emits `FieldSessionAbortedEvent` to `MANAGER` for rescheduling, reassignment, or cancellation.<br>- At most one `IN_PROGRESS` session per mission. |
| **Defect Finding & 3-Way Verification**<br>(`FindingStatus`, `ResolutionStatus`) | - **Finding States**: `PENDING`, `CONFIRMED`, plus soft-delete (`is_deleted`)<br>- **Re-inspection 3-Way States**: `RESOLVED`, `UNRESOLVED`, `INCONCLUSIVE`<br>- **Transitions**: AI/Manual create (`-> PENDING`), Confirm (`/confirmation -> CONFIRMED`), Verify (`/reinspection-verifications/{id}`) | - Every `PENDING` AI candidate must be confirmed or soft-deleted before `POST /findings/confirm`.<br>- `RE_INSPECTION` compares Prior Defect vs Engineer Repair Proof (`repair_proof_url`) vs Drone Re-capture (`new_evidence_id`). |
| **Inspection Report**<br>(`ReportStatus` — 5 Canonical States `V17`) | - **States**: `SUBMITTED`, `RETURNED`, `APPROVED`, `PUBLISHED`, `SUPERSEDED`<br>- **Transitions**: Auto-Compile & Submit (`/report/draft`), Review (`/review`), Publish (`/publish`), Withdraw (`/withdraw`) | - `DRAFT` and `AUTHOR_VERIFIED` states and manual `content_snapshot` notes are eliminated (`V16`, `V17`).<br>- Independent reviewer (`MANAGER` / `ADMIN`) must not equal the author `INSPECTOR`.<br>- `CUSTOMER` access is restricted to `PUBLISHED` reports (`403 REPORT_NOT_PUBLISHED`). |

**3. Maintenance Work Order & Sub-Entity State Machines**

```mermaid
%% title: MaintenanceWorkOrder 12-State Lifecycle Diagram
stateDiagram-v2
  direction TB
  [*] --> WO_DRAFT : createWorkOrder(initialTasks) [FE-07]
  WO_DRAFT --> AWAITING_APPROVAL : submitEstimate() [FE-07]
  AWAITING_APPROVAL --> APPROVED : approveEstimate() [FE-07]
  AWAITING_APPROVAL --> REWORK_REQUIRED : rejectEstimate(reason) [FE-07]
  REWORK_REQUIRED --> AWAITING_APPROVAL : submitEstimate() (revised) [FE-07]
  APPROVED --> READY : release() [FE-07]
  READY --> IN_PROGRESS : start() [FE-07]
  IN_PROGRESS --> WORK_COMPLETED : declareComplete() (all logs VERIFIED) [FE-07]
  WORK_COMPLETED --> SUBMITTED_FOR_ACCEPTANCE : submitCompletionReport(autoDraft) [FE-08]
  SUBMITTED_FOR_ACCEPTANCE --> ACCEPTED : recordAcceptance(ACCEPTED) [FE-08]
  SUBMITTED_FOR_ACCEPTANCE --> REWORK_REQUIRED : recordAcceptance(REWORK_REQUIRED) [FE-08]
  SUBMITTED_FOR_ACCEPTANCE --> REINSPECTION_REQUIRED : recordAcceptance(REINSPECTION_REQUIRED) [FE-08]
  REWORK_REQUIRED --> IN_PROGRESS : resumeAfterRework() [FE-07]
  REINSPECTION_REQUIRED --> SUBMITTED_FOR_ACCEPTANCE : reinspectionReportPublished() [FE-08]
  REINSPECTION_REQUIRED --> IN_PROGRESS : resumeAfterReinspection() [FE-07]
  ACCEPTED --> COST_RECONCILED : reconcileCosts(actualLines) [FE-08]
  COST_RECONCILED --> CLOSED : close() [FE-08]
  CLOSED --> [*]
```

| Domain Entity | Lifecycle States & Key Transitions | Business Rule Guards |
| --- | --- | --- |
| **Maintenance Work Order**<br>(`WorkOrderStatus`) | - **12 States**: `DRAFT`, `AWAITING_APPROVAL`, `APPROVED`, `READY`, `IN_PROGRESS`, `WORK_COMPLETED`, `SUBMITTED_FOR_ACCEPTANCE`, `ACCEPTED`, `REWORK_REQUIRED`, `REINSPECTION_REQUIRED`, `COST_RECONCILED`, `CLOSED`<br>- **Plan & Budget**: Create with 1-Click `initialTasks` (`-> DRAFT`), Submit RAG Estimate (`-> AWAITING_APPROVAL`), Approve (`-> APPROVED`)<br>- **Execute**: Release (`-> READY`), Start (`-> IN_PROGRESS`), Batch-Verify & Declare Complete (`-> WORK_COMPLETED`)<br>- **Accept & Close**: Auto-Draft & Submit Report (`-> SUBMITTED_FOR_ACCEPTANCE`), Accept (`-> ACCEPTED`), Reconcile (`-> COST_RECONCILED`), Close (`-> CLOSED`) | - Budget Approver and Accepting Reviewer must be independent `CUSTOMER` users outside the executing repair team.<br>- `REINSPECTION_REQUIRED` emits `ReinspectionRequestedEvent` to spawn a linked `RE_INSPECTION` mission; `ReinspectionReportPublishedEvent` attaches the published report and reinstates the Work Order for final acceptance. |
| **Estimate Version**<br>(`EstimateStatus`) | - **States**: `DRAFT`, `SUBMITTED`, `APPROVED`, `REJECTED`, `SUPERSEDED`<br>- **Transitions**: RAG Norms (`/suggest-estimate`), Submit (`/submit`), Approve (`/approve`, prior `-> SUPERSEDED`), Reject (`/reject`) | - Approver (`CUSTOMER`) must not equal `preparedByUserId`. |
| **Maintenance Work Log**<br>(`WorkLogStatus`) | - **States**: `IN_PROGRESS`, `PAUSED_FOR_CHANGE`, `SUBMITTED`, `VERIFIED`<br>- **Transitions**: Log (`/work-logs`), Submit (`/submit`), Verify (`/verify` or 1-Click `/work-logs/batch-verify` by Team Lead) | - Every submitted work log must be `VERIFIED` by the Team Lead and no Change Order may be `AWAITING_APPROVAL` before `declareComplete()` is allowed. |
| **Change Order**<br>(`ChangeOrderStatus`) | - **States**: `DRAFT`, `AWAITING_APPROVAL`, `APPROVED`, `REJECTED`, `RETURNED`, `SUPERSEDED`<br>- **Transitions**: Propose (`/changes`), Decide (`/approve`, `/reject`, `/return`) | - Approved deltas adjust the budget ceiling during cost reconciliation without mutating the initial baseline. |
| **Completion Report**<br>(`ReportVersionStatus`) | - **States**: `DRAFT`, `AUTHOR_VERIFIED`, `SUBMITTED`, `RETURNED`, `APPROVED`, `SUPERSEDED`<br>- **Transitions**: Auto-Draft (`/reports/auto-draft`), Verify & Submit (`/verify`, `/submit`), RAG Audit (`/acceptance-compliance`), Accept (`/acceptance-decisions`) | - Only the designated Report Author can verify/submit; only the independent `CUSTOMER` Accepting Reviewer can accept. |
