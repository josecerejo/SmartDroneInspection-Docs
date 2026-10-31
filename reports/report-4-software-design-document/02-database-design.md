---
title: "Report 4 - Database Design"
document_type: report4-sdd-section
weight: 25
source: "report4-software-design-document.docx"
---

## 2. Database Design

The relational database architecture is implemented on PostgreSQL 17 with strict foreign key constraints, index-optimized tenant filtering, and cryptographic audit fields. The database schema encompasses 30 application tables (plus the `event_publication` transactional outbox) categorized across identity, assets and drone equipment leasing, inspection workflow, maintenance remediation, and cross-cutting infrastructure.

```mermaid
%% title: Database Entity Relationship Diagram (ERD)
erDiagram
  organizations ||--o{ users : employs
  organizations ||--o{ subscriptions : holds
  subscriptions ||--o{ payment_transactions : settles
  organizations ||--o{ drones : owns
  organizations ||--o{ drone_leases : contracts
  platform_drones ||--o{ drone_leases : leased_via
  drone_leases ||--o| drones : provisions
  users ||--o{ drone_leases : requests
  organizations ||--o{ assets : owns
  asset_categories ||--o{ assets : categorizes
  assets ||--o{ asset_documents : attaches
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
  users ||--o{ recurring_inspection_schedules : default_inspector
  drones ||--o{ recurring_inspection_schedules : default_drone
  recurring_inspection_schedules ||--o{ schedule_occurrences : generates
  organizations ||--o{ schedule_occurrences : scopes
  inspections |o--o{ schedule_occurrences : fulfills
  recurring_inspection_schedules ||--o{ inspections : dispatches
  inspections ||--o{ field_sessions : executes
  inspections ||--o{ evidence : contains
  field_sessions ||--o{ evidence : captures
  inspections ||--o{ findings : records
  evidence ||--o{ findings : locates
  inspections ||--o{ inspection_reports : delivers
  organizations ||--o{ maintenance_work_orders : owns
  assets ||--o{ maintenance_work_orders : remediates
  users ||--o{ maintenance_work_orders : governs
  findings ||--o{ maintenance_work_orders : initiates
  inspection_reports ||--o{ maintenance_work_orders : references
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
  subscriptions {
    uuid id PK
    uuid organization_id FK
    uuid confirmed_by_user_id FK
    varchar plan_code
    integer billing_period_months
    numeric agreed_amount_usd
    varchar status
    timestamptz starts_at
    timestamptz ends_at
    varchar external_reference
    jsonb terms_snapshot
    timestamptz confirmed_at
    timestamptz created_at
    timestamptz updated_at
    bigint row_version
  }
  payment_transactions {
    uuid id PK
    uuid subscription_id FK
    varchar paypal_order_id
    varchar paypal_capture_id
    numeric amount
    varchar currency
    varchar status
    varchar payer_email
    timestamptz captured_at
    timestamptz created_at
    timestamptz updated_at
    bigint row_version
  }
  platform_drones {
    uuid id PK
    varchar serial_number
    varchar model
    varchar manufacturer
    jsonb payload_metadata
    numeric monthly_rate_usd
    varchar status
    varchar notes
    timestamptz created_at
    timestamptz updated_at
    bigint row_version
  }
  drone_leases {
    uuid id PK
    uuid platform_drone_id FK
    uuid organization_id FK
    uuid customer_drone_id FK
    uuid requested_by_user_id FK
    uuid confirmed_by_user_id FK
    integer lease_period_months
    numeric monthly_rate_usd
    numeric agreed_amount_usd
    varchar status
    timestamptz starts_at
    timestamptz ends_at
    timestamptz reclaimed_at
    varchar external_reference
    varchar paypal_order_id
    varchar paypal_capture_id
    timestamptz confirmed_at
    varchar notes
    timestamptz created_at
    timestamptz updated_at
    bigint row_version
  }
  drones {
    uuid id PK
    uuid organization_id FK
    uuid lease_id FK
    varchar serial_number
    varchar model
    varchar manufacturer
    jsonb payload_metadata
    varchar serviceability
    timestamptz last_maintenance_at
    timestamptz next_maintenance_at
    varchar notes
    varchar registration_number
    varchar registration_file_key
    timestamptz registration_expires_at
    timestamptz created_at
    timestamptz updated_at
    bigint row_version
    varchar ownership_type
    timestamptz lease_expires_at
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
    varchar name
    varchar description
    numeric latitude
    numeric longitude
    varchar status
    timestamptz created_at
    timestamptz updated_at
    bigint row_version
    varchar asset_code
    jsonb location
    jsonb technical_profile
    jsonb inspection_items
  }
  asset_documents {
    uuid id PK
    uuid asset_id FK
    uuid uploaded_by_user_id FK
    varchar document_type
    varchar file_name
    varchar content_type
    bigint size_bytes
    character checksum_sha256
    varchar object_key
    date document_date
    timestamptz created_at
  }
  recurring_inspection_schedules {
    uuid id PK
    uuid organization_id FK
    uuid asset_id FK
    uuid created_by_user_id FK
    uuid inspector_id FK
    uuid drone_id FK
    timestamp anchor_date
    varchar timezone
    varchar recurrence_unit
    integer recurrence_interval
    bigint duration_seconds
    integer reminder_days
    timestamptz ends_at
    bigint next_occurrence
    varchar status
    timestamptz created_at
    timestamptz updated_at
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
    timestamptz reminder_sent_at
    timestamptz created_at
    timestamptz updated_at
    bigint row_version
  }
  inspections {
    uuid id PK
    uuid asset_id FK
    uuid organization_id FK
    uuid inspector_id FK
    uuid drone_id FK
    uuid recurring_schedule_id FK
    varchar status
    timestamptz created_at
    timestamptz updated_at
    bigint row_version
    timestamptz planned_start_at
    timestamptz planned_end_at
    varchar flight_permit_file_key
    varchar flight_permit_file_name
    timestamptz flight_permit_uploaded_at
    timestamptz findings_confirmed_at
    varchar findings_snapshot_hash
  }
  field_sessions {
    uuid id PK
    uuid inspection_id FK
    varchar status
    timestamptz started_at
    timestamptz ended_at
    varchar postponement_reason
    varchar abort_reason
    timestamptz created_at
    timestamptz updated_at
    bigint row_version
    varchar pre_flight_checklist_note
    varchar outcome_notes
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
    timestamptz created_at
  }
  findings {
    uuid id PK
    uuid inspection_id FK
    uuid evidence_id FK
    varchar finding_code
    varchar defect_label
    varchar severity
    jsonb bounding_box
    varchar technical_notes
    varchar recommended_action
    varchar status
    varchar model_name
    numeric confidence
    timestamptz forwarded_to_maintenance_at
    boolean is_deleted
    timestamptz created_at
  }
  inspection_reports {
    uuid id PK
    uuid inspection_id FK
    uuid reviewer_user_id FK
    integer version_no
    varchar status
    jsonb content_snapshot
    timestamptz submitted_at
    timestamptz reviewed_at
    varchar return_reason
    varchar rendered_object_key
    character rendered_checksum_sha256
    timestamptz published_at
    timestamptz created_at
  }
  repair_knowledge_chunks {
    uuid id PK
    varchar standard_code
    varchar title
    varchar category
    varchar defect_patterns
    text content
    varchar reference_url
    timestamptz created_at
  }
  notifications {
    uuid id PK
    uuid recipient_user_id FK
    uuid organization_id FK
    varchar event_type
    varchar channel
    varchar title
    varchar body
    varchar target_path
    varchar status
    integer attempt_count
    varchar last_error_code
    timestamptz sent_at
    timestamptz read_at
    timestamptz created_at
    varchar aggregate_type
    uuid aggregate_id
    varchar deduplication_key
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
    bigint aggregate_version
    varchar reason
    varchar trace_id
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
    integer completion_attempts
    timestamptz last_resubmission_date
  }
  maintenance_work_orders {
    uuid id PK
    uuid organization_id FK
    uuid asset_id FK
    uuid source_report_version_id FK
    uuid source_finding_id FK
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
    timestamptz created_at
    timestamptz updated_at
    bigint row_version
  }
  maintenance_team_members {
    uuid id PK
    uuid work_order_id FK
    uuid engineer_user_id FK
    uuid assigned_by_user_id FK
    varchar member_role
    timestamptz effective_from
    timestamptz effective_until
    varchar reason
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
    timestamptz created_at
    timestamptz updated_at
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
    timestamptz created_at
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
    timestamptz created_at
    timestamptz updated_at
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
    timestamptz created_at
    timestamptz updated_at
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
```

**Table Descriptions**

| No | Table | Description |
| :---: | :--- | :--- |
| 01 | `organizations` | Stores tenant enterprise companies subscribing to the platform. (`10` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `created_by_user_id` references `users(id)`|
| 02 | `users` | Stores system user accounts across `ADMIN`, `PLATFORM_MANAGER`, `ORG_MANAGER`, `INSPECTOR`, and `MAINTENANCE_ENGINEER`, account status (`ACTIVE`, `SUSPENDED`, `DISABLED`), and self-declared remote pilot license credentials. (`24` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `organization_id` references `organizations(id)`|
| 03 | `auth_sessions` | Tracks active user login sessions (`WEB`, `MOBILE`), hashed refresh tokens, expiration timestamps, and revocation status. (`9` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `user_id` references `users(id)`|
| 04 | `subscriptions` | Tracks ENTERPRISE subscription contracts, billing periods (`1..120` months), agreed USD amounts, immutable contract terms snapshots, and lifecycle status (`PENDING`, `ACTIVE`, `PAST_DUE`, `SUSPENDED`, `EXPIRED`, `CANCELLED`). (`15` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `confirmed_by_user_id` references `users(id)`, `organization_id` references `organizations(id)`|
| 05 | `payment_transactions` | Records PayPal Orders v2 checkout and capture transactions linked to enterprise subscriptions (`PENDING`, `COMPLETED`, `FAILED`, `REFUNDED`). (`12` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `subscription_id` references `subscriptions(id)`|
| 06 | `platform_drones` | Platform-owned serial-numbered leasable drone pool managed by `PLATFORM_MANAGER` (`AVAILABLE`, `LEASED`, `MAINTENANCE`, `RETIRED`). (`11` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: None|
| 07 | `drone_leases` | drone equipment lease contracts between the platform and a customer organization (`PENDING`, `ACTIVE`, `RECLAIMED`, `CANCELLED`) with wire/PayPal settlement and customer fleet provisioning. (`21` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `platform_drone_id` references `platform_drones(id)`, `organization_id` references `organizations(id)`, `customer_drone_id` references `drones(id)`, `requested_by_user_id` references `users(id)`, `confirmed_by_user_id` references `users(id)`|
| 08 | `drones` | Catalogs customer organization drone aircraft (`OWNED` or `LEASED`), hardware serial numbers, payload metadata, serviceability status (`ACTIVE`, `MAINTENANCE`, `SUSPENDED`, `RETIRED`), and CAAV registration metadata. (`19` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `organization_id` references `organizations(id)`, `lease_id` references `drone_leases(id)`|
| 09 | `asset_categories` | Global structural categorization catalog for infrastructure assets managed by `ADMIN`. (`8` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: None|
| 10 | `assets` | Manages physical infrastructure assets (`ACTIVE`, `INACTIVE`, `RETIRED`), GPS coordinates, and `inspection_items` (`jsonb` array of standardized structural checkpoints). (`15` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `category_id` references `asset_categories(id)`, `organization_id` references `organizations(id)`|
| 11 | `asset_documents` | Engineering schematics, structural drawings, and technical specifications attached to an asset with 64-character SHA-256 deduplication. (`11` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `asset_id` references `assets(id)`, `uploaded_by_user_id` references `users(id)`|
| 12 | `inspections` | Core inspection mission table tracking scheduled time windows, direct Inspector and Drone assignment, optional `recurring_schedule_id`, self-service flight permit attributes, and 10-state lifecycle status. (`17` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `asset_id` references `assets(id)`, `drone_id` references `drones(id)`, `inspector_id` references `users(id)`, `organization_id` references `organizations(id)`, `recurring_schedule_id` references `recurring_inspection_schedules(id)`|
| 13 | `recurring_inspection_schedules` | Periodic inspection recurrence rules per asset with timezone-anchored cadence (`WEEK`, `MONTH`, `YEAR`), default Inspector/Drone, duration, reminder lead days, and status (`ACTIVE`, `PAUSED`, `ENDED`). (`18` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `organization_id` references `organizations(id)`, `asset_id` references `assets(id)`, `created_by_user_id` references `users(id)`, `inspector_id` references `users(id)`, `drone_id` references `drones(id)`|
| 14 | `schedule_occurrences` | Individual `GENERATED`, `BLOCKED`, or `SKIPPED` recurring schedule occurrences linked to dispatched `inspections`. (`15` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `schedule_id` references `recurring_inspection_schedules(id)`, `organization_id` references `organizations(id)`, `inspection_id` references `inspections(id)`|
| 15 | `field_sessions` | Records individual on-site flight survey sessions, pre-flight safety checklist notes, and operational outcomes (`PLANNED`, `IN_PROGRESS`, `FIELD_COMPLETED`, `POSTPONED`, `ABORTED`). (`12` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `inspection_id` references `inspections(id)`|
| 16 | `evidence` | Digital media captures collected during inspection field sessions with MinIO object keys, EXIF capture timestamps, GPS coordinates, location descriptions, and soft-delete flag (`is_deleted`). (`13` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `field_session_id` references `field_sessions(id)`, `inspection_id` references `inspections(id)`|
| 17 | `findings` | Unified defect findings table managing YOLO11 AI defect candidates (`PENDING`) and human-verified official findings (`CONFIRMED`) with bounding boxes and maintenance forwarding timestamps. (`15` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `evidence_id` references `evidence(id)`, `inspection_id` references `inspections(id)`|
| 18 | `inspection_reports` | Versioned inspection report deliverables (`DRAFT`, `AUTHOR_VERIFIED`, `SUBMITTED`, `RETURNED`, `APPROVED`, `PUBLISHED`, `SUPERSEDED`), review gates, rendered PDF object keys, and SHA-256 checksums. (`13` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `reviewer_user_id` references `users(id)`, `inspection_id` references `inspections(id)`|
| 19 | `maintenance_work_orders` | Remediation projects initiated from confirmed inspection findings, tracking corrective scope, acceptance criteria, team role assignments, and 12-state lifecycle status. (`18` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `asset_id` references `assets(id)`, `accepting_reviewer_user_id` references `users(id)`, `budget_approver_user_id` references `users(id)`, `organization_id` references `organizations(id)`, `owner_user_id` references `users(id)`, `report_author_user_id` references `users(id)`, `source_finding_id` references `findings(id)`, `source_report_version_id` references `inspection_reports(id)`, `team_lead_user_id` references `users(id)`|
| 20 | `maintenance_team_members` | Engineering team members allocated to a maintenance work order (`LEAD`, `REPORT_AUTHOR`, `MEMBER`) with partial unique indexes on active leadership roles. (`10` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `assigned_by_user_id` references `users(id)`, `engineer_user_id` references `users(id)`, `work_order_id` references `maintenance_work_orders(id)`|
| 21 | `maintenance_tasks` | Decomposed repair tasks (`PLANNED`, `READY`, `IN_PROGRESS`, `PAUSED_FOR_CHANGE`, `WORK_COMPLETED`, `REWORK_REQUIRED`, `ACCEPTED`, `CANCELLED`) with technical methods and assigned engineers. (`13` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `assigned_engineer_user_id` references `users(id)`, `work_order_id` references `maintenance_work_orders(id)`|
| 22 | `maintenance_estimate_versions` | Versioned financial projection baselines (`DRAFT`, `SUBMITTED`, `APPROVED`, `REJECTED`, `SUPERSEDED`) for labor, materials, equipment, and services. (`11` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `approved_by_user_id` references `users(id)`, `prepared_by_user_id` references `users(id)`, `work_order_id` references `maintenance_work_orders(id)`|
| 23 | `maintenance_cost_lines` | Individual itemized cost rows (`LABOR`, `MATERIAL`, `EQUIPMENT`, `SERVICE`) within an `ESTIMATE` baseline or `ACTUAL` expenditure reconciliation. (`14` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `entered_by_user_id` references `users(id)`, `estimate_version_id` references `maintenance_estimate_versions(id)`, `task_id` references `maintenance_tasks(id)`, `work_order_id` references `maintenance_work_orders(id)`|
| 24 | `maintenance_change_orders` | Formal variance requests (`DRAFT`, `AWAITING_APPROVAL`, `APPROVED`, `REJECTED`, `RETURNED`, `SUPERSEDED`) adjusting repair scope or budget ceiling. (`13` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `decided_by_user_id` references `users(id)`, `requested_by_user_id` references `users(id)`, `work_order_id` references `maintenance_work_orders(id)`|
| 25 | `maintenance_work_logs` | Execution entries (`IN_PROGRESS`, `PAUSED_FOR_CHANGE`, `SUBMITTED`, `VERIFIED`) logging task labor hours, as-left conditions, and test readings. (`13` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `task_id` references `maintenance_tasks(id)`, `engineer_user_id` references `users(id)`, `work_order_id` references `maintenance_work_orders(id)`|
| 26 | `maintenance_reports` | Versioned maintenance completion deliverables (`DRAFT`, `AUTHOR_VERIFIED`, `SUBMITTED`, `RETURNED`, `APPROVED`, `SUPERSEDED`) verified by the Report Author and rendered to PDF. (`9` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `work_order_id` references `maintenance_work_orders(id)`|
| 27 | `maintenance_acceptance_decisions` | Formal independent technical acceptance records (`ACCEPTED`, `REWORK_REQUIRED`, `REINSPECTION_REQUIRED`) evaluating repair completion. (`9` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `report_version_id` references `maintenance_reports(id)`, `reviewer_user_id` references `users(id)`, `work_order_id` references `maintenance_work_orders(id)`|
| 28 | `repair_knowledge_chunks` | Civil and structural engineering repair standard chunks (`TCVN`, `EN`, `ISO`, `ASTM`) and 1536-dim `pgvector` embeddings supporting RAG scope suggestions. (`9` columns including `embedding vector(1536)`).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: None|
| 29 | `notifications` | Operational alerts and deduplicated in-app notifications (`SENT`, `READ`, `FAILED`) delivered to system users. (`17` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `organization_id` references `organizations(id)`, `recipient_user_id` references `users(id)`|
| 30 | `audit_events` | Append-only security audit trail recording consequential domain transitions and access events. (`13` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: `actor_user_id` references `users(id)`, `organization_id` references `organizations(id)`|
| 31 | `event_publication` | Spring Modulith transactional outbox table for reliable asynchronous domain event delivery. (`9` columns).<br>- Primary keys: `id` (UUID)<br>- Foreign keys: None|


---

**Main Domain Entity State Machine Diagrams**

Every lifecycle entity in `SmartDroneInspection-backend` is governed by an explicit state machine with guarded domain methods.

**1. Enterprise Subscription & Drone Equipment Lease State Machines**

```mermaid
%% title: Subscription and Drone Equipment Lease State Machines
stateDiagram-v2
  direction LR
  state "Enterprise Subscription (subscriptions.status)" as SubSM {
    [*] --> SUB_PENDING : requestEnterprise() [FR-03]
    SUB_PENDING --> SUB_ACTIVE : confirmPayment() / captureOrder() [FR-03]
    SUB_PENDING --> SUB_CANCELLED : cancel() [FR-03]
    SUB_ACTIVE --> SUB_PAST_DUE : markPastDue() [FR-03]
    SUB_PAST_DUE --> SUB_ACTIVE : confirmPayment() [FR-03]
    SUB_PAST_DUE --> SUB_SUSPENDED : suspend() [FR-03]
    SUB_SUSPENDED --> SUB_ACTIVE : confirmPayment() [FR-03]
    SUB_ACTIVE --> SUB_EXPIRED : expire() / superseded by renewal [FR-03]
    SUB_ACTIVE --> SUB_CANCELLED : cancel() [FR-03]
    SUB_EXPIRED --> [*]
    SUB_CANCELLED --> [*]
  }

  state "Drone Equipment Lease (drone_leases.status)" as LeaseSM {
    [*] --> LEASE_PENDING : requestLease() [FR-05]
    LEASE_PENDING --> LEASE_ACTIVE : activateWire() / activatePayPal() [FR-05]
    LEASE_PENDING --> LEASE_CANCELLED : cancel() [FR-05]
    LEASE_ACTIVE --> LEASE_RECLAIMED : reclaim() [FR-05]
    LEASE_RECLAIMED --> [*]
    LEASE_CANCELLED --> [*]
  }
```

| Domain Entity | Lifecycle States & Key Transitions | Business Rule Guards |
| --- | --- | --- |
| **Enterprise Subscription**<br>(`Subscription.Status`) | - **States**: `PENDING`, `ACTIVE`, `PAST_DUE`, `SUSPENDED`, `EXPIRED`, `CANCELLED`<br>- **Request**: `POST /subscriptions` (`-> PENDING`)<br>- **Activate**: Wire confirmation or PayPal capture (`-> ACTIVE`)<br>- **Renew / End**: Prior active term transitions to `EXPIRED` | - Enforces at most one `ACTIVE` subscription per organization (unique active subscription index). |
| **Drone Equipment Lease & Pool**<br>(`DroneLeaseStatus`) | - **Lease States**: `PENDING`, `ACTIVE`, `RECLAIMED`, `CANCELLED`<br>- **Pool States**: `AVAILABLE`, `LEASED`, `MAINTENANCE`, `RETIRED`<br>- **Activate / Reclaim**: `/confirm-payment` (`-> ACTIVE`), `/reclaim` (`-> RECLAIMED`) | - Auto-provisions customer `Drone` (`LEASED`, `ACTIVE`) on activation.<br>- Retires customer `Drone` (`RETIRED`) on reclaim. |
| **Asset & Drone Fleet**<br>(`AssetStatus`, `DroneStatus`) | - **Asset States**: `ACTIVE`, `INACTIVE`, `RETIRED`<br>- **Drone States**: `ACTIVE`, `MAINTENANCE`, `SUSPENDED`, `RETIRED`<br>- **Transitions**: `/retire` (`-> RETIRED`), `/serviceability` | - `RETIRED` is terminal and blocks new edits or schedules.<br>- Only `ACTIVE` assets and `ACTIVE` drones can be scheduled. |
| **Recurring Schedule & Inbox**<br>(`ScheduleStatus`) | - **Schedule**: `ACTIVE`, `PAUSED`, `ENDED` (`/pause`, `/resume`, `/end`)<br>- **Occurrence**: `GENERATED`, `BLOCKED`, `SKIPPED` (`/retry`, `/skip`)<br>- **Notification**: `PENDING`, `SENT`, `READ`, `FAILED` | - At most one `ACTIVE` schedule per asset.<br>- `GENERATED` occurrence links to a dispatched `ASSIGNED` inspection. |

**2. Inspection, FieldSession, Finding & InspectionReport State Machines**

```mermaid
%% title: Inspection, FieldSession and InspectionReport State Machine Diagram
stateDiagram-v2
  direction TB
  [*] --> SCHEDULED : createInspection(inspectorId, droneId) [FR-06, FR-07]
  SCHEDULED --> IN_PROGRESS : startFieldSession(preFlightNote) [FR-09] (requires hasFlightPermit())
  IN_PROGRESS --> SCHEDULED : postponeSession(reason) [FR-09]
  IN_PROGRESS --> FIELD_COMPLETED : completeSession(outcomeNotes) [FR-09]
  FIELD_COMPLETED --> IN_PROGRESS : startAdditionalSession() [FR-09]
  FIELD_COMPLETED --> UNDER_REVIEW : submitReport() [FR-13]
  UNDER_REVIEW --> FIELD_COMPLETED : returnToDraft() / withdraw() [FR-13, FR-14]
  UNDER_REVIEW --> COMPLETED : publishReport() (PDF + SHA-256) [FR-14]
  FIELD_COMPLETED --> COMPLETED : publishReport() [FR-14]
  SCHEDULED --> CANCELLED : cancel() [FR-06]
  COMPLETED --> [*]
  CANCELLED --> [*]
```

```mermaid
%% title: InspectionReport Version Lifecycle State Machine Diagram
stateDiagram-v2
  direction LR
  [*] --> RPT_DRAFT : createDraft (AI / Manual) [FR-13]
  RPT_DRAFT --> AUTHOR_VERIFIED : verifyAsAuthor() [FR-13]
  AUTHOR_VERIFIED --> SUBMITTED : submit() [FR-13]
  SUBMITTED --> RPT_DRAFT : withdraw() (before review) [FR-13]
  SUBMITTED --> RETURNED : reviewBy(approve=false, reason) [FR-14]
  RETURNED --> AUTHOR_VERIFIED : verifyAsAuthor() (after edit) [FR-13]
  SUBMITTED --> APPROVED : reviewBy(approve=true) [FR-14]
  APPROVED --> PUBLISHED : publish() (renders PDF to MinIO) [FR-14]
  PUBLISHED --> SUPERSEDED : newer version PUBLISHED [FR-14]
  PUBLISHED --> [*]
  SUPERSEDED --> [*]
```

| Domain Entity | Lifecycle States & Key Transitions | Business Rule Guards |
| --- | --- | --- |
| **Inspection Mission**<br>(`InspectionStatus`) | - **States**: `SCHEDULED`, `IN_PROGRESS`, `FIELD_COMPLETED`, `UNDER_REVIEW`, `COMPLETED`, `CANCELLED`<br>- **Key Steps**: Create (`-> SCHEDULED`), Field Session (`-> IN_PROGRESS -> FIELD_COMPLETED`), Submit Report (`-> UNDER_REVIEW`), Publish / Close (`-> COMPLETED`) | - Flight readiness verified via permit on file (`hasFlightPermit()`) and active pilot licensing.<br>- Findings confirmation and report drafting occur within `FIELD_COMPLETED`; publication moves directly to `COMPLETED`. |
| **Field Session**<br>(`FieldSessionStatus`) | - **States**: `PLANNED`, `IN_PROGRESS`, `FIELD_COMPLETED`, `ABORTED` (historical `POSTPONED` retained for read-only history)<br>- **Transitions**: Start (`/field-sessions`), Abort (`/abort`), Complete (`/completion`) | - Requires non-blank `preFlightChecklistNote` on start and `outcomeNotes` on completion.<br>- Aborting a session returns the inspection to `SCHEDULED` and emits an alert to managers for rescheduling, reassignment, or cancellation.<br>- At most one `IN_PROGRESS` session per mission. |
| **Defect Finding**<br>(`FindingStatus`) | - **States**: `PENDING`, `CONFIRMED`, plus soft-delete (`is_deleted`)<br>- **Transitions**: AI/Manual create (`-> PENDING`), Confirm (`/confirmation -> CONFIRMED`), Retire (`DELETE`), Restore (`/restore`) | - Every `PENDING` AI candidate must be confirmed or soft-deleted before `POST /findings/confirm`. |
| **Inspection Report**<br>(`ReportStatus`) | - **States**: `DRAFT`, `AUTHOR_VERIFIED`, `SUBMITTED`, `RETURNED`, `APPROVED`, `PUBLISHED`, `SUPERSEDED`<br>- **Transitions**: Author (`/draft`, `/verify`, `/submit`), Review (`/review`), Publish (`/publish`) | - Independent `ORG_MANAGER` reviewer must not equal the author `Inspector`.<br>- Evidence and findings are locked during `SUBMITTED` and `PUBLISHED`. |

**3. Maintenance Work Order & Sub-Entity State Machines**

```mermaid
%% title: MaintenanceWorkOrder 12-State Lifecycle Diagram
stateDiagram-v2
  direction TB
  [*] --> WO_DRAFT : createWorkOrder() [FR-15]
  WO_DRAFT --> AWAITING_APPROVAL : submitEstimate() [FR-15]
  AWAITING_APPROVAL --> APPROVED : approveEstimate() [FR-15]
  AWAITING_APPROVAL --> REWORK_REQUIRED : rejectEstimate(reason) [FR-15]
  REWORK_REQUIRED --> AWAITING_APPROVAL : submitEstimate() (revised) [FR-15]
  APPROVED --> READY : release() [FR-15]
  READY --> IN_PROGRESS : start() [FR-15]
  IN_PROGRESS --> WORK_COMPLETED : declareComplete() (all logs VERIFIED) [FR-15]
  WORK_COMPLETED --> SUBMITTED_FOR_ACCEPTANCE : submitCompletionReport() [FR-16]
  SUBMITTED_FOR_ACCEPTANCE --> ACCEPTED : recordAcceptance(ACCEPTED) [FR-16]
  SUBMITTED_FOR_ACCEPTANCE --> REWORK_REQUIRED : recordAcceptance(REWORK_REQUIRED) [FR-16]
  SUBMITTED_FOR_ACCEPTANCE --> REINSPECTION_REQUIRED : recordAcceptance(REINSPECTION_REQUIRED) [FR-16]
  REWORK_REQUIRED --> IN_PROGRESS : resumeAfterRework() [FR-15]
  REINSPECTION_REQUIRED --> IN_PROGRESS : resumeAfterReinspection() [FR-15]
  ACCEPTED --> COST_RECONCILED : reconcileCosts(actualLines) [FR-16]
  COST_RECONCILED --> CLOSED : close() [FR-16]
  CLOSED --> [*]
```

| Domain Entity | Lifecycle States & Key Transitions | Business Rule Guards |
| --- | --- | --- |
| **Maintenance Work Order**<br>(`WorkOrderStatus`) | - **12 States**: `DRAFT`, `AWAITING_APPROVAL`, `APPROVED`, `READY`, `IN_PROGRESS`, `WORK_COMPLETED`, `SUBMITTED_FOR_ACCEPTANCE`, `ACCEPTED`, `REWORK_REQUIRED`, `REINSPECTION_REQUIRED`, `COST_RECONCILED`, `CLOSED`<br>- **Plan & Budget**: Create (`-> DRAFT`), Submit Estimate (`-> AWAITING_APPROVAL`), Approve (`-> APPROVED`)<br>- **Execute**: Release (`-> READY`), Start (`-> IN_PROGRESS`), Declare Complete (`-> WORK_COMPLETED`)<br>- **Accept & Close**: Submit Report (`-> SUBMITTED_FOR_ACCEPTANCE`), Accept (`-> ACCEPTED`), Reconcile (`-> COST_RECONCILED`), Close (`-> CLOSED`) | - Budget Approver and Accepting Reviewer must be independent `ORG_MANAGER`s outside the executing repair team.<br>- `REINSPECTION_REQUIRED` automatically creates a linked verification `Inspection`. |
| **Estimate Version**<br>(`EstimateStatus`) | - **States**: `DRAFT`, `SUBMITTED`, `APPROVED`, `REJECTED`, `SUPERSEDED`<br>- **Transitions**: Submit (`/submit`), Approve (`/approve`, prior `-> SUPERSEDED`), Reject (`/reject`) | - Approver (`ORG_MANAGER`) must not equal `preparedByUserId`. |
| **Maintenance Work Log**<br>(`WorkLogStatus`) | - **States**: `IN_PROGRESS`, `PAUSED_FOR_CHANGE`, `SUBMITTED`, `VERIFIED`<br>- **Transitions**: Log (`/work-logs`), Submit (`/submit`), Verify (`/verify` by Team Lead) | - Every submitted work log must be `VERIFIED` by the Team Lead before `declareComplete()` is allowed. |
| **Change Order**<br>(`ChangeOrderStatus`) | - **States**: `DRAFT`, `AWAITING_APPROVAL`, `APPROVED`, `REJECTED`, `RETURNED`, `SUPERSEDED`<br>- **Transitions**: Propose (`/changes`), Decide (`/approve`, `/reject`, `/return`) | - Approved deltas adjust the budget ceiling during cost reconciliation without mutating the initial baseline. |
| **Completion Report**<br>(`ReportVersionStatus`) | - **States**: `DRAFT`, `AUTHOR_VERIFIED`, `SUBMITTED`, `RETURNED`, `APPROVED`, `SUPERSEDED`<br>- **Transitions**: Author (`/reports`, `/verify`, `/submit`), Accept (`/acceptance-decisions`) | - Only the designated Report Author can verify/submit; only the independent Accepting Reviewer can accept. |
