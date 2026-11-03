---
title: "Report 4 - Database Design"
document_type: report4-sdd-section
weight: 25
source: "report4-software-design-document.docx"
---

## 2. Database Design

The relational database is implemented on PostgreSQL 17 with the `pgvector` extension. The schema enforces referential integrity through foreign keys, tenant and role isolation, and optimistic concurrency control. It supports four main business areas:

- **Onboarding, Assets, and Drone Registry (MF1)**: Customer organizations, user accounts, Inspector profiles and flight logs, one-time verification challenges, customer airspace registration reviews, infrastructure assets, asset documents, and Inspector-owned drone registrations.
- **Commercial Requests, Quotations, and Agreements (MF2)**: One-time and recurring service requests, order chat messages, versioned VND quotations, scheduled inspection occurrences, and platform financial rate settings.
- **Field Inspections, Evidence, and Reporting (MF3)**: Inspection missions, on-site field sessions, photograph and video evidence, AI and confirmed defect findings, versioned inspection reports, and three-way re-inspection defect verifications.
- **Corrective Maintenance and Closeout (MF4)**: Maintenance work orders, repair teams, tasks, cost estimates, cost lines, change orders, work logs, completion reports, customer acceptance decisions, and engineering standard knowledge chunks.

```mermaid
%% title: Database Entity Relationship Diagram (ERD)
erDiagram
  organizations ||--o{ users : employs
  users ||--o| prospective_customer_registrations : submits
  users ||--o| inspector_profiles : has_profile
  users |o--o{ otp_challenges : verifies
  users ||--o{ inspector_flight_logs : owns_flight_log
  users ||--o{ drones : owns_drone
  users ||--o{ drone_registration_applications : submits
  drones |o--o{ drone_registration_applications : provisions
  users ||--o{ inspection_finance_settings : configures
  organizations ||--o{ assets : owns
  asset_categories ||--o{ assets : categorizes
  assets ||--o{ asset_documents : attaches
  organizations ||--o{ service_requests : requests
  assets ||--o{ service_requests : targets
  service_requests ||--o{ service_request_messages : discusses
  service_requests ||--o{ service_request_quotes : versions
  service_requests ||--o{ service_request_occurrences : schedules
  service_request_occurrences |o--o| inspections : dispatches
  organizations ||--o{ audit_events : records
  organizations ||--o{ notifications : scopes
  users ||--o{ notifications : receives
  users ||--o{ auth_sessions : opens
  organizations ||--o{ inspections : owns
  assets ||--o{ inspections : undergoes
  users ||--o{ inspections : inspects
  drones ||--o{ inspections : flies
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
  assets ||--o{ maintenance_work_orders : repairs
  users ||--o{ maintenance_work_orders : governs
  findings ||--o{ maintenance_work_orders : initiates
  inspection_reports ||--o{ maintenance_work_orders : references
  inspections |o--o{ maintenance_work_orders : reinspects
  maintenance_work_orders ||--o{ maintenance_team_members : assigns
  maintenance_work_orders ||--o{ maintenance_tasks : plans
  maintenance_work_orders ||--o{ maintenance_estimate_versions : estimates
  maintenance_estimate_versions ||--o{ maintenance_cost_lines : itemizes
  maintenance_tasks ||--o{ maintenance_cost_lines : accrues
  maintenance_work_orders ||--o{ maintenance_change_orders : adjusts
  maintenance_tasks ||--o{ maintenance_work_logs : logs
  maintenance_work_orders ||--o{ maintenance_reports : summarizes
  maintenance_reports ||--o{ maintenance_acceptance_decisions : decides
```

**Table Descriptions**

| No | Table | Description |
| :---: | :--- | :--- |
| 01 | `organizations` | Stores customer organizations that own infrastructure assets, request inspection services, and govern maintenance work orders.<br>- Primary keys: `id`<br>- Foreign keys: None |
| 02 | `users` | Stores user accounts across the five system roles (Platform Administrator, Platform Manager, Customer, Inspector, and Maintenance Engineer), account status, and organization scope.<br>- Primary keys: `id`<br>- Foreign keys: `organization_id` |
| 03 | `inspector_profiles` | Stores Inspector pilot license numbers, license classes, expiration dates, scanned license files, flight hours, and technical specializations.<br>- Primary keys: `user_id`<br>- Foreign keys: `user_id` |
| 04 | `otp_challenges` | Stores one-time verification codes for user sign-in, customer registration, and password reset.<br>- Primary keys: `id`<br>- Foreign keys: `user_id` |
| 05 | `inspector_flight_logs` | Records historical flight missions, flight duration, aircraft details, location, and safety notes for Inspectors.<br>- Primary keys: `id`<br>- Foreign keys: `inspector_user_id`, `recorded_by_user_id` |
| 06 | `auth_sessions` | Tracks active web and mobile login sessions, hashed refresh tokens, expiration times, and session revocation records.<br>- Primary keys: `id`<br>- Foreign keys: `user_id` |
| 07 | `prospective_customer_registrations` | Stores customer organization and initial asset registration requests that require platform review due to restricted airspace proximity.<br>- Primary keys: `id`<br>- Foreign keys: `user_id`, `asset_category_id`, `reviewed_by_user_id` |
| 08 | `drone_registration_applications` | Stores Inspector applications to register owned drones with registration, ownership, and technical inspection documents.<br>- Primary keys: `id`<br>- Foreign keys: `inspector_user_id`, `drone_id`, `reviewed_by_user_id` |
| 09 | `drones` | Catalogs approved drones owned by Inspectors or customer organizations, including serial number, model, and serviceability status.<br>- Primary keys: `id`<br>- Foreign keys: `inspector_owner_id`, `organization_id` |
| 10 | `asset_categories` | Defines the global catalog of infrastructure asset categories managed by platform administrators.<br>- Primary keys: `id`<br>- Foreign keys: None |
| 11 | `assets` | Stores customer infrastructure assets, geographic coordinates, technical profiles, and structural inspection checkpoints.<br>- Primary keys: `id`<br>- Foreign keys: `organization_id`, `category_id` |
| 12 | `asset_documents` | Stores engineering drawings and reference documents attached to an infrastructure asset.<br>- Primary keys: `id`<br>- Foreign keys: `asset_id`, `uploaded_by_user_id` |
| 13 | `service_requests` | Stores one-time and recurring customer inspection requests, preferred time windows, recurrence rules, accepted quotation version, and signed agreement file reference.<br>- Primary keys: `id`<br>- Foreign keys: `organization_id`, `asset_id`, `created_by_user_id` |
| 14 | `service_request_messages` | Stores chat messages exchanged between the Customer and the Platform Manager during service request negotiation.<br>- Primary keys: `id`<br>- Foreign keys: `request_id`, `author_user_id` |
| 15 | `service_request_quotes` | Stores versioned VND quotations proposing the inspection scope, schedule window, Inspector, drone, and fee per occurrence.<br>- Primary keys: `id`<br>- Foreign keys: `request_id`, `inspector_id`, `drone_id`, `issued_by_user_id` |
| 16 | `service_request_occurrences` | Stores individual inspection occurrences generated from an accepted service request, tracking dispatch status, payment status, and partner payout status.<br>- Primary keys: `id`<br>- Foreign keys: `request_id`, `inspector_id`, `drone_id`, `inspection_id` |
| 17 | `inspection_finance_settings` | Stores platform commission, VAT, and personal income tax rates used to calculate net partner payouts.<br>- Primary keys: `id`<br>- Foreign keys: `updated_by_user_id` |
| 18 | `inspections` | Stores scheduled inspection missions (initial inspections and re-inspections), assigned Inspector and drone, flight permit reference, and mission status.<br>- Primary keys: `id`<br>- Foreign keys: `organization_id`, `asset_id`, `inspector_id`, `drone_id`, `work_order_id`, `source_inspection_id` |
| 19 | `field_sessions` | Records on-site field flight sessions, pre-flight safety notes, completion outcome notes, abort reasons, persisted `SmartDroneHub` flight report metrics (`telemetry_source`, `flight_duration_seconds`, `distance_flown_meters`, `max_altitude_meters`, `start_battery_percent`, `end_battery_percent`, `flight_final_state`, `flight_report_note`), GPS flight trace (`flight_trace_json`), and synced flight video reference (`flight_video_evidence_id`).<br>- Primary keys: `id`<br>- Foreign keys: `inspection_id`, `flight_video_evidence_id` |
| 20 | `evidence` | Stores metadata and object storage keys for photographs and MP4 videos captured during field sessions, including capture time and GPS coordinates.<br>- Primary keys: `id`<br>- Foreign keys: `inspection_id`, `field_session_id` |
| 21 | `findings` | Stores AI-suggested defect candidates and Inspector-confirmed defect findings, including defect label, severity, confidence score, and bounding box.<br>- Primary keys: `id`<br>- Foreign keys: `inspection_id`, `evidence_id` |
| 22 | `inspection_reports` | Stores versioned inspection report records, their status and publication metadata, submission and review timestamps, and return feedback.<br>- Primary keys: `id`<br>- Foreign keys: `inspection_id`, `reviewer_user_id` |
| 23 | `reinspection_defect_verifications` | Stores three-way verification records comparing the original defect finding, repair proof, and new re-inspection evidence.<br>- Primary keys: `id`<br>- Foreign keys: `reinspection_id`, `source_finding_id`, `new_evidence_id` |
| 24 | `maintenance_work_orders` | Stores corrective maintenance work orders created from published inspection defects, tracking scope, priority, assigned roles, and lifecycle status.<br>- Primary keys: `id`<br>- Foreign keys: `organization_id`, `asset_id`, `source_finding_id`, `source_report_version_id`, `reinspection_id`, `owner_user_id`, `budget_approver_user_id`, `team_lead_user_id`, `report_author_user_id`, `accepting_reviewer_user_id` |
| 25 | `maintenance_team_members` | Stores Maintenance Engineers assigned to a work order along with their team role (Team Lead, Report Author, or Member).<br>- Primary keys: `id`<br>- Foreign keys: `work_order_id`, `engineer_user_id`, `assigned_by_user_id` |
| 26 | `maintenance_tasks` | Stores individual repair tasks, repair methods, planned schedules, acceptance criteria, and task status under a work order.<br>- Primary keys: `id`<br>- Foreign keys: `work_order_id`, `assigned_engineer_user_id` |
| 27 | `maintenance_estimate_versions` | Stores versioned repair cost estimates prepared by Maintenance Engineers and reviewed by the Customer budget approver.<br>- Primary keys: `id`<br>- Foreign keys: `work_order_id`, `prepared_by_user_id`, `approved_by_user_id` |
| 28 | `maintenance_cost_lines` | Stores itemized planned and actual cost entries (labor, material, equipment, external service, and contingency) for a work order.<br>- Primary keys: `id`<br>- Foreign keys: `work_order_id`, `estimate_version_id`, `task_id`, `entered_by_user_id` |
| 29 | `maintenance_change_orders` | Stores scope or budget change requests submitted during repair execution and decided by the Customer.<br>- Primary keys: `id`<br>- Foreign keys: `work_order_id`, `requested_by_user_id`, `decided_by_user_id` |
| 30 | `maintenance_work_logs` | Stores field repair execution logs, labor hours, test measurements, as-left conditions, and Team Lead verification status.<br>- Primary keys: `id`<br>- Foreign keys: `work_order_id`, `task_id`, `engineer_user_id` |
| 31 | `maintenance_reports` | Stores versioned maintenance completion reports prepared by the Report Author for Customer review.<br>- Primary keys: `id`<br>- Foreign keys: `work_order_id` |
| 32 | `maintenance_acceptance_decisions` | Records independent Customer acceptance decisions, technical review comments, and re-inspection or rework outcomes.<br>- Primary keys: `id`<br>- Foreign keys: `work_order_id`, `report_version_id`, `reviewer_user_id` |
| 33 | `repair_knowledge_chunks` | Stores civil and structural engineering standard excerpts and vector embeddings used by the maintenance advisor.<br>- Primary keys: `id`<br>- Foreign keys: None |
| 34 | `notifications`, `audit_events` & `event_publication` | Store deduplicated user notifications, security audit trails, and transactional domain event publications.<br>- Primary keys: `id`<br>- Foreign keys: `organization_id`, `recipient_user_id`, `actor_user_id` |

---

**Domain Entity State Machine Diagrams**

**1. Service Request and Payment State Machines**

```mermaid
%% title: Service Request and Occurrence Payment State Machine Diagram
stateDiagram-v2
  direction LR
  state "Service Request Lifecycle" as ReqSM {
    [*] --> OPEN : Submit Request
    OPEN --> QUOTED : Issue VND Quotation
    QUOTED --> QUOTED : Revise Quotation Version
    QUOTED --> ACCEPTED : Customer Accepts Quote
    ACCEPTED --> CONTRACT_SIGNED : Upload Signed Agreement
    CONTRACT_SIGNED --> ASSIGNED : Dispatch Inspector & Drone
    OPEN --> CANCELLED : Cancel Request
    QUOTED --> CANCELLED : Cancel Request
    ASSIGNED --> [*]
    CANCELLED --> [*]
  }

  state "Occurrence Payment Lifecycle" as PaySM {
    [*] --> PENDING : Occurrence Created
    PENDING --> PAYMENT_DUE : Customer Accepts Report
    PAYMENT_DUE --> PAID : Online Payment Confirmed
    PAID --> [*]
  }
```

| Domain Entity | Lifecycle States | Key Transition Rules |
| --- | --- | --- |
| **Customer & Drone Onboarding** | `PENDING`, `APPROVED`, `REJECTED` | Locations inside a prohibited No-Fly Zone are rejected immediately; restricted airspace locations remain pending until reviewed by an Administrator or Manager. Drone registration requires all three supporting documents before approval. |
| **Service Request** | `OPEN`, `QUOTED`, `ACCEPTED`, `CONTRACT_SIGNED`, `ASSIGNED`, `CANCELLED` | Accepting a quotation materializes the planned inspection occurrences. Uploading the signed offline agreement moves the request to the contract-signed state so occurrences can be dispatched. |
| **Occurrence Payment & Payout** | Payment: `PENDING`, `PAYMENT_DUE`, `PAID`<br>Payout: `PENDING`, `ELIGIBLE`, `PAID` | Customer acceptance of a published report makes payment due for that occurrence. Confirmed payment via PayOS or VNPay marks the occurrence as paid and records Inspector payout settlement. |

**2. Inspection, Field Session, and Inspection Report State Machines**

```mermaid
%% title: Inspection and Field Session State Machine Diagram
stateDiagram-v2
  direction TB
  [*] --> SCHEDULED : Dispatch Inspector & Drone
  SCHEDULED --> IN_PROGRESS : Start Field Session (Flight Permit Required)
  IN_PROGRESS --> SCHEDULED : Abort Session (Notify Manager)
  IN_PROGRESS --> FIELD_COMPLETED : Complete Field Session
  FIELD_COMPLETED --> UNDER_REVIEW : Submit Inspection Report
  UNDER_REVIEW --> FIELD_COMPLETED : Return or Withdraw Report
  UNDER_REVIEW --> COMPLETED : Approve & Publish Report
  SCHEDULED --> CANCELLED : Cancel Inspection
  COMPLETED --> [*]
  CANCELLED --> [*]
```

```mermaid
%% title: Inspection Report Version State Machine Diagram
stateDiagram-v2
  direction LR
  [*] --> SUBMITTED : Submit Compiled Report
  SUBMITTED --> RETURNED : Manager Returns or Author Withdraws
  RETURNED --> SUBMITTED : Resubmit Updated Report
  SUBMITTED --> PUBLISHED : Independent Manager Approves & Publishes Report
  PUBLISHED --> SUPERSEDED : Newer Version Published
  PUBLISHED --> [*]
  SUPERSEDED --> [*]
```

| Domain Entity | Lifecycle States | Key Transition Rules |
| --- | --- | --- |
| **Inspection Mission** | `SCHEDULED`, `IN_PROGRESS`, `FIELD_COMPLETED`, `UNDER_REVIEW`, `COMPLETED`, `CANCELLED` | A field session can start only when the mission is scheduled and a flight permit is on file. Once a session completes, no additional field session can be started; the Inspector proceeds to evidence review and report submission. |
| **Field Session** | `PLANNED`, `IN_PROGRESS`, `FIELD_COMPLETED`, `ABORTED` | Starting a session requires a pre-flight safety note, and completing a session requires outcome notes. Aborting a session records the abort reason, reverts the mission to scheduled, and alerts the Manager to reschedule, reassign, or cancel. |
| **Defect Finding** | `PENDING`, `CONFIRMED` | AI-detected defect candidates start as pending. All pending candidates must be confirmed or removed by the assigned Inspector before the findings baseline can be locked. |
| **Inspection Report** | `SUBMITTED`, `RETURNED`, `PUBLISHED`, `SUPERSEDED` | A qualified Manager or Administrator other than the author either returns a submitted report with a reason or approves and publishes it in one action. Publication marks the report version official and immutable and completes the inspection. |

**3. Maintenance Work Order State Machine**

```mermaid
%% title: Maintenance Work Order Lifecycle State Machine Diagram
stateDiagram-v2
  direction TB
  [*] --> DRAFT : Create Work Order from Defect
  DRAFT --> AWAITING_APPROVAL : Submit Cost Estimate
  AWAITING_APPROVAL --> APPROVED : Customer Approves Estimate
  AWAITING_APPROVAL --> REWORK_REQUIRED : Customer Rejects Estimate
  REWORK_REQUIRED --> AWAITING_APPROVAL : Submit Revised Estimate
  APPROVED --> READY : Release Work Order
  READY --> IN_PROGRESS : Start Field Repair
  IN_PROGRESS --> WORK_COMPLETED : Complete Repair (All Work Logs Verified)
  WORK_COMPLETED --> SUBMITTED_FOR_ACCEPTANCE : Submit Completion Report
  SUBMITTED_FOR_ACCEPTANCE --> ACCEPTED : Customer Accepts Repair
  SUBMITTED_FOR_ACCEPTANCE --> REWORK_REQUIRED : Customer Requests Rework
  SUBMITTED_FOR_ACCEPTANCE --> REINSPECTION_REQUIRED : Customer Requests Drone Re-inspection
  REWORK_REQUIRED --> IN_PROGRESS : Resume Repair Work
  REINSPECTION_REQUIRED --> REINSPECTION_REPORT_ATTACHED : Re-inspection Report Published
  REINSPECTION_REPORT_ATTACHED --> ACCEPTED : Customer Accepts After Re-inspection
  REINSPECTION_REPORT_ATTACHED --> REWORK_REQUIRED : Customer Requests Further Rework
  ACCEPTED --> COST_RECONCILED : Reconcile Actual Costs
  COST_RECONCILED --> CLOSED : Close Work Order
  CLOSED --> [*]
```

| Domain Entity | Lifecycle States | Key Transition Rules |
| --- | --- | --- |
| **Maintenance Work Order** | `DRAFT`, `AWAITING_APPROVAL`, `APPROVED`, `READY`, `IN_PROGRESS`, `WORK_COMPLETED`, `SUBMITTED_FOR_ACCEPTANCE`, `ACCEPTED`, `REWORK_REQUIRED`, `REINSPECTION_REQUIRED`, `COST_RECONCILED`, `CLOSED` | The Customer budget approver and accepting reviewer must be independent of the executing repair team. Requesting a drone re-inspection creates a linked re-inspection mission and attaches its published report back to the work order. |
| **Estimate & Change Order** | `DRAFT`, `SUBMITTED`, `APPROVED`, `REJECTED`, `SUPERSEDED` | A work order cannot be declared complete while any change order is awaiting approval. Approved change orders adjust the authorized budget ceiling without overwriting the original estimate. |
| **Maintenance Work Log** | `IN_PROGRESS`, `PAUSED_FOR_CHANGE`, `SUBMITTED`, `VERIFIED` | Every submitted work log must be verified by the designated Team Lead before the work order can be declared complete. |
