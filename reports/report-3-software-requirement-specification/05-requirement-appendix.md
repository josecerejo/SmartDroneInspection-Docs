---
title: "Report 3 - Requirement Appendix"
document_type: report3-srs-section
weight: 55
source: "report3-software-requirement-specification.docx"
---

## 5. Requirement Appendix

### 5.1 Business Rules

The system enforces 49 normative business rules across multi-zone/tenant isolation, partner onboarding, commercial service contracts, aviation compliance, advisory AI/RAG oversight, report immutability, PayOS settlement, and maintenance cost control:

| ID | Rule Definition |
| --- | --- |
| BR-01 | `ADMIN` and `MANAGER` accounts belong to `ActorZone.PLATFORM` (`organization_id = NULL`) and enforce role separation of duties; `CUSTOMER` and `MAINTENANCE_ENGINEER` accounts belong to `ActorZone.CUSTOMER_ORGANIZATION` (`organization_id IS NOT NULL`); partner `INSPECTOR` accounts belong to `ActorZone.INSPECTOR_PARTNER` (`organization_id = NULL`). |
| BR-02 | A `CUSTOMER` can access and manage only the assets, maintenance workforce, service requests, published inspection reports, and maintenance work orders belonging to their own customer organization. |
| BR-03 | Customer `MAINTENANCE_ENGINEER` accounts belong strictly to a single customer organization, whereas partner `INSPECTOR` accounts are platform-coordinated partners who may be assigned to missions across different customer organizations only through explicit `MANAGER` occurrence dispatch. |
| BR-04 | Partner `INSPECTOR`s and `MAINTENANCE_ENGINEER`s can access and act only upon inspection missions, work orders, or repair tasks explicitly assigned to them. |
| BR-05 | Active user accounts and unexpired remote pilot licenses are mandatory for partner onboarding and flight readiness; expired pilot licenses block occurrence assignment and field session start. |
| BR-06 | Customer onboarding (`POST /api/v1/auth/register`) evaluates the initial infrastructure asset against Vietnam airspace zones: `NO_FLY_ZONE` locations are immediately rejected (`403`), `RESTRICTED_ZONE` locations are held in `prospective_customer_registrations` (`PENDING`) for `ADMIN` review, and `CLEAR_ZONE` locations activate the organization and first asset immediately. |
| BR-07 | Starting an on-site field session (`startFieldSession`) requires an uploaded flight permit (`hasFlightPermit()`), an unexpired pilot license, and a mandatory pre-flight safety checklist note confirming aircraft, battery, and environmental suitability. |
| BR-08 | Software flight permit uploads and airspace Haversine radar checks verify internal readiness compliance only and do not grant governmental aviation exemptions under Decision 18/2020/QĐ-TTg or Decree 288/2025/NĐ-CP. |
| BR-09 | Occurrence dispatch (`assignOccurrence`) and mission reassignment check cross-organization scheduling conflicts (`hasPlatformPartnerScheduleConflict`) so a partner `INSPECTOR` or inspector-owned `Drone` is never double-booked across any customer organization during an overlapping time window. |
| BR-10 | Service request quotations (`service_request_quotes`) support explicit `VND` or `USD` pricing per occurrence, bind to a vetted partner `INSPECTOR` and their approved owned `Drone`, and require configured platform finance rates (`inspection_finance_settings`: commission, VAT, and PIT/TNCN withholding) when quoting in `VND`. |
| BR-11 | Commercial service orders follow a strict state machine (`OPEN` $\rightarrow$ `QUOTED` $\rightarrow$ `ACCEPTED` $\rightarrow$ `CONTRACT_SIGNED` $\rightarrow$ `ASSIGNED`); order chat messages (`service_request_messages`) never auto-mutate quote terms, and mission dispatch is blocked until the executed offline paper contract scan (`PDF`, `DOCX`, `JPEG`, `PNG` with `SHA-256`) is uploaded. |
| BR-12 | Service request quotes, inspection report versions, cost estimate baselines, Change Orders, and acceptance decisions preserve complete version histories; published records cannot be modified in place. |
| BR-13 | For a `RECURRING` service request, a single executed paper contract on the parent request covers all generated `service_request_occurrences` in the agreed term (Decision D2), while each occurrence still requires individual partner assignment, flight permit verification, and report publication. |
| BR-14 | Field flight sessions (`FieldSession`) support two active completion outcomes from `IN_PROGRESS`: `FIELD_COMPLETED` or `ABORTED` (postponement is removed). Aborting a session records the mandatory abort reason, automatically reverts the parent `Inspection` to `SCHEDULED`, and emits `FieldSessionAbortedEvent` to alert the `MANAGER` for rescheduling, reassignment, or cancellation. |
| BR-15 | Inspections follow 6 canonical lifecycle states (`SCHEDULED`, `IN_PROGRESS`, `FIELD_COMPLETED`, `UNDER_REVIEW`, `COMPLETED`, `CANCELLED`); flight readiness is enforced as a domain guard on `startFieldSession` rather than a separate status enum. |
| BR-16 | Aircraft flight operation and physical structural repair are real-world technical actions; system `Start`, `Complete`, and `Abort` commands represent software session logging, not hardware flight actuation. |
| BR-17 | Uploaded digital evidence (`image/jpeg`, `image/png`, `image/webp`, `image/tiff`, `video/mp4`, `application/pdf` up to `10 MB`) retains an upload timestamp, file identity, and original capture metadata; missing telemetry is explicitly disclosed. |
| BR-18 | Duplicate evidence files within the same inspection scope are rejected based on sanitized filename matching. |
| BR-19 | Absence of EXIF GPS coordinates or camera telemetry is recorded as missing metadata and does not automatically invalidate otherwise suitable visual or video evidence. |
| BR-20 | `YOLO11` vision detections (and Vision LLM fallback detections when `YOLO11` returns zero candidates) remain unconfirmed `PENDING` candidates until reviewed by the assigned `INSPECTOR`; only human-confirmed (`CONFIRMED`) findings enter the official inspection record. |
| BR-21 | Rejected or unconfirmed AI defect suggestions are excluded from official defect metrics, auto-compiled inspection reports, and maintenance repair scopes. |
| BR-22 | Inspectors may record manual defect findings backed by photo or MP4 video evidence; unavailability of AI services does not prevent manual finding confirmation or deterministic report compilation. |
| BR-23 | Once the assigned `INSPECTOR` confirms the findings baseline in `FIELD_COMPLETED`, visiting the Report workspace auto-compiles and submits the inspection report (`SUBMITTED`), transitioning the inspection to `UNDER_REVIEW` without requiring manual free-text report notes (`content_snapshot` dropped). |
| BR-24 | A `MANAGER` (or `ADMIN`) distinct from the report author reviews the submitted report (`APPROVED` or `RETURNED`) and publishes the official PDF (`PUBLISHED`); an `INSPECTOR` can never review or publish their own report. |
| BR-25 | Unapproved (`SUBMITTED`, `RETURNED`, `APPROVED`) inspection reports and internal field logs are restricted from `CUSTOMER` access (`403 REPORT_NOT_PUBLISHED`); customers track in-flight missions via the 5-stage Customer Progress Tracker until official publication. |
| BR-26 | Published inspection reports (`PUBLISHED`) are rendered to immutable `SHA-256` A4 PDF artefacts in MinIO and transition the mission to `COMPLETED`; subsequent amendments require publishing a new version that marks the prior version `SUPERSEDED`. |
| BR-27 | All commercial, reporting, and engineering gates require explicit, attributable human decisions; no automated timer-based or silence-based approval is permitted. |
| BR-28 | Returning an inspection report (`RETURNED`) or maintenance report requires mandatory review comments, preserves prior version history, and reverts an inspection from `UNDER_REVIEW` back to `FIELD_COMPLETED` so the author can revise findings and re-compile. |
| BR-29 | `ADMIN` and `MANAGER` govern platform operations, partner onboarding, commercial contracts, and report publication; neither holds authority to approve a `CUSTOMER`'s internal maintenance repair budgets or Change Orders. |
| BR-30 | Application workflow approvals represent auditable software authorizations and do not constitute statutory engineering seals or governmental aviation clearances. |
| BR-31 | Maintenance work orders must reference a confirmed defect (`CONFIRMED`) forwarded from a `PUBLISHED` inspection report belonging to the same customer organization. |
| BR-32 | The `pgvector` RAG Cost & Norms Estimator (`suggest-estimate`) proposes standard Vietnamese construction cost norms (`LABOR`, `MATERIAL`, `EQUIPMENT`, `CONTINGENCY`) as advisory inputs; the submitting `MAINTENANCE_ENGINEER` and approving `CUSTOMER` remain accountable for the final budget. |
| BR-33 | When a `CUSTOMER` accepts a published inspection report (`accept-report`), the occurrence `payment_status` transitions to `PAYMENT_DUE`; downloading the official PDF artefact requires `payment_status = PAID` (via **PayOS VietQR** checkout/webhook or manager confirmation), which simultaneously unlocks `payout_status = ELIGIBLE` for partner settlement. |
| BR-34 | Any increase in repair scope, cost, or schedule during maintenance execution requires a `CUSTOMER`-approved Change Order prior to executing additional work; the initial approved estimate baseline remains immutable, and work cannot be declared complete while a Change Order is pending. |
| BR-35 | Maintenance execution logs require before-and-after repair proof (`repair_proof_url`, `repair_engineer_notes`) and quantitative test readings (`testReadings`), and smart completion reports (`auto-draft`) synthesize these verified records into a 5-part deliverable. |
| BR-36 | Commercial inspection fees are settled per service request occurrence via PayOS VietQR (with platform commission, VAT, and PIT/TNCN withholding), whereas maintenance repair estimates and actuals are tracked as the Customer organization's internal capital/operational expenditure register. |
| BR-37 | Selecting `REINSPECTION_REQUIRED` during maintenance acceptance automatically emits `ReinspectionRequestedEvent` to create a linked `RE_INSPECTION` mission (`work_order_id`, `source_inspection_id`, `source_report_version_id`) and pre-populated `reinspection_defect_verifications` rows; supplementary flights within the same initial inspection use an additional `FieldSession` in `FE-05`. |
| BR-38 | All onboarding reviews, quote acceptances, signed contract uploads, partner assignments, field aborts, finding confirmations, report publications, PayOS settlements, budget approvals, 3-way re-inspection verifications, and work order closures are recorded in `audit_events`. |
| BR-39 | Direct URL navigation, notification deep links, and media object keys confer no authority; backend `ActorZone`, organization, assignment, and payment-gate checks are enforced on every request. |
| BR-40 | Password changes, role updates, and session revocations increment `auth_version` and immediately invalidate active tokens without altering historical audit attribution. |
| BR-41 | Partner `INSPECTOR`s may onboard without owning a drone and register one or more owned drones (`drones.inspector_owner_id`) afterward by uploading three distinct documents (`REGISTRATION`, `OWNERSHIP`, `INSPECTION`) for `ADMIN`/`MANAGER` approval before the drone can be used in quotes or missions. |
| BR-42 | Infrastructure asset registration enforces the Vietnam No-Fly Zone creation guard and defines standardized structural inspection checkpoints inherited by missions on that asset. |
| BR-43 | In a `RE_INSPECTION` mission, the assigned `INSPECTOR` performs 3-way comparative defect verification (`reinspection_defect_verifications`: Prior Defect vs Engineer Repair Proof vs Drone Re-capture) and records `RESOLVED`, `UNRESOLVED`, or `INCONCLUSIVE` for each target defect. |
| BR-44 | The inspection reporting lifecycle enforces 5 canonical report states (`SUBMITTED`, `RETURNED`, `APPROVED`, `PUBLISHED`, `SUPERSEDED`); publishing a Re-inspection Report emits `ReinspectionReportPublishedEvent` to attach `reinspection_report_version_id` to the Work Order and reinstate its completion report for final `CUSTOMER` acceptance. |
| BR-45 | Each maintenance work order designates one `TEAM_LEAD`, one `REPORT_AUTHOR`, and an independent `CUSTOMER` Budget Approver and Accepting Reviewer; no member of the executing repair team may approve budgets or accept their own work. |
| BR-46 | Every repair task is assigned to an approved team member, and all submitted work logs must be `VERIFIED` by the `TEAM_LEAD` (individually or via 1-click `batch-verify`) before the work order can transition to `WORK_COMPLETED`. |
| BR-47 | All quote amounts, tax/commission splits, repair estimates, Change Orders, and actual expenditures use exact decimal arithmetic with explicit currency codes (`VND` or `USD`). |
| BR-48 | The LLM Executive Summary (`/ai-summary`) and RAG Acceptance Compliance Audit (`/acceptance-compliance`) synthesize exclusively from verified findings, field test readings, and seeded `TCVN`/`EN`/`ISO` standards, with deterministic fallbacks when external AI endpoints are offline. |
| BR-49 | A Maintenance Work Order can transition to `CLOSED` only after an independent `CUSTOMER` reviewer records `ACCEPTED` (following Re-inspection Report publication when re-inspection was requested) and reconciles actual costs (`COST_RECONCILED`). |

### 5.2 Common Requirements

- **Form Validation**: All input forms validate required fields, character limits, numeric bounds, valid date windows, airspace coordinates, and current workflow state before persisting changes.
- **ActorZone, Organization & Assignment Checks**: Every API endpoint verifies the caller's role, `ActorZone`, organization membership, and partner mission or work-order assignment on the server.
- **Date, Time & Timezone Display**: Timestamps are stored in UTC (`TIMESTAMPTZ`) and rendered in the organization's or schedule's configured timezone (`Asia/Ho_Chi_Minh`).
- **Currency & Financial Precision**: All service quotations (`VND`/`USD`), platform commission/VAT/TNCN splits, repair estimates, Change Orders, and actual costs are computed to two decimal places without floating-point drift.
- **Media Upload & Streaming Limits**: Uploaded photos, `video/mp4` captures, signed contracts (`PDF`/`DOCX`/`JPEG`/`PNG`), and drone/license certificates are validated for MIME type and size (up to `10 MB` per file) and delivered via authenticated HTTP/Blob streaming.
- **Idempotency & Deduplication**: Repeated clicks or webhook retries on schedule generation, evidence upload, PayOS webhook capture, batch work-log verification, or outbox notification delivery are safely deduplicated.
- **Cryptographic Document Integrity**: Signed service contracts, published PDF inspection reports, and accepted maintenance completion reports are hashed with `SHA-256` and locked against in-place mutation.

### 5.3 Application Messages List

The system defines standard user-facing messages, validation alerts, and toast notifications across web and mobile clients.

| # | Message code | Message Type | Context | Content |
| --- | --- | --- | --- | --- |
| 1 | MSG01 | In line | Search has no authorized records | No results found. |
| 2 | MSG02 | Under field | Required field empty | This field is required. |
| 3 | MSG03 | Under field | Configured length exceeded | Must not exceed {maxLength} characters. |
| 4 | MSG04 | Under field | Invalid email | Enter a valid email address. |
| 5 | MSG05 | Toast | Record created | Created successfully. |
| 6 | MSG06 | Toast | Record updated | Updated successfully. |
| 7 | MSG07 | Dialog | Irreversible/versioned action | Confirm this action and the version you are acting on. |
| 8 | MSG08 | In line | Authentication failed | Email or password is incorrect. |
| 9 | MSG09 | In line | Disabled/suspended account | Unable to sign in. Contact your administrator. |
| 10 | MSG10 | In line | Expired/revoked session | Your session has expired. Sign in again. |
| 11 | MSG11 | Under field | Password policy failure | Password does not meet the security requirements. |
| 12 | MSG12 | Toast | Inspection mission dispatched | Inspection scheduled with its asset and assigned partner Inspector/Drone snapshot. |
| 13 | MSG13 | In line | Stale quote, report or estimate version | A newer version is available. Refresh and review it before continuing. |
| 14 | MSG14 | Toast | Quote or assignment accepted | Accepted successfully. |
| 15 | MSG15 | Under field | Rejection/abort lacks reason | Enter a mandatory reason before submitting. |
| 16 | MSG16 | In line | Unsupported/corrupt/large file | This file cannot be uploaded. Check its type, integrity and 10 MB size limit. |
| 17 | MSG17 | In line | Duplicate evidence | This evidence file has already been uploaded in this inspection scope. |
| 18 | MSG18 | Toast | Upload saved | Media uploaded and available for review. |
| 19 | MSG19 | In line | AI unavailable | External AI service is unavailable. Deterministic fallback or manual entry is active. |
| 20 | MSG20 | Toast | Report auto-compiled & submitted | Inspection report auto-compiled from confirmed findings and submitted to Platform Manager for review. |
| 21 | MSG21 | In line | Unreviewed findings remaining | Confirm or remove all pending AI defect candidates before confirming the findings baseline. |
| 22 | MSG22 | Toast | Inspection report published | Approved inspection report published as an immutable PDF and delivered to the Customer. |
| 23 | MSG23 | Toast | Repair Change Order submitted | Scope/cost/schedule Change Order submitted to Customer for approval. |
| 24 | MSG24 | In line | Unapproved additional work | Additional work requires a Customer-approved Change Order before completion. |
| 25 | MSG25 | Toast | Work order closed | Accepted and cost-reconciled work order closed; source inspection and re-inspection history is preserved. |
| 26 | MSG26 | In line | Required credential/document missing | Provide all required license, registration, ownership, and inspection documents. |
| 27 | MSG27 | Toast | Compliance document recorded | Document verification recorded. Internal review does not replace statutory aviation authorization. |
| 28 | MSG28 | In line | Airspace No-Fly / Restricted Zone alert | Location falls inside a prohibited No-Fly Zone (blocked) or Restricted Zone (requires review under Decision 18/2020/QĐ-TTg & Decree 288/2025/NĐ-CP). |
| 29 | MSG29 | Toast | Service request & quote recorded | Commercial service request or quotation version saved. |
| 30 | MSG30 | Toast | Report or estimate returned | Returned to the author with mandatory review comments. |
| 31 | MSG31 | In line | Independent reviewer missing | Assign a reviewer who is not the author or a member of the executing team. |
| 32 | MSG32 | Under field | Pre-flight checklist incomplete | Enter the mandatory pre-flight safety checklist note before starting the field session. |
| 33 | MSG33 | In line | Source findings changed | Confirmed findings changed after compilation; the report version has been refreshed. |
| 34 | MSG34 | Toast | Budget baseline approved | Repair scope and cost estimate approved by Customer. The original baseline is preserved. |
| 35 | MSG35 | Toast | Signed service contract uploaded | Executed paper service contract scan uploaded with SHA-256 verification (`CONTRACT_SIGNED`). |
| 36 | MSG36 | In line | Invalid partner Inspector/Drone pair | Select an approved partner Inspector and an active Drone owned by that Inspector with no schedule conflict. |
| 37 | MSG37 | In line | Missing flight permit or expired license | Cannot start field session. Ensure the mission flight permit is uploaded and the pilot license is unexpired. |
| 38 | MSG38 | Toast | Findings baseline confirmed | Findings baseline locked; navigating to the Report tab will auto-compile and submit the report. |
| 39 | MSG39 | In line | AI summary fallback | Using deterministic executive summary synthesis from confirmed findings. |
| 40 | MSG40 | In line | Missing maintenance lead/author | Assign one Team Lead and one Report Author before releasing the work order. |
| 41 | MSG41 | In line | Invalid cost line | Quantity and unit rate must be non-negative with an explicit currency code. |
| 42 | MSG42 | Toast | Work logs batch-verified & work completed | All submitted work logs verified by Team Lead and repair work declared complete (`WORK_COMPLETED`). |
| 43 | MSG43 | In line | Unverified logs or pending Change Order | Verify all submitted work logs and resolve any pending Change Orders before declaring work complete. |
| 44 | MSG44 | In line | Self-approval or self-acceptance blocked | Authors and executing repair team members cannot approve their own budgets or accept their own work. |
| 45 | MSG45 | In line | Cost reconciliation required | Reconcile actual costs against the approved budget and Change Orders before closing the work order. |
| 46 | MSG46 | Toast | Auto-drafted completion report submitted | Maintenance completion report synthesized and submitted to Customer for acceptance review. |
| 47 | MSG47 | Toast | PayOS VietQR payment confirmed | Service occurrence payment verified (`PAID`); official PDF download and partner payout eligibility unlocked. |
| 48 | MSG48 | In line | Payment required for PDF download | Accept the published report and complete VietQR payment via PayOS (or manager confirmation) to download the official PDF. |

### 5.4 Other Requirements

#### 5.4.1 Scope and Operational Constraints
- **Multi-Zone & Tenant Isolation**: Platform operations (`ADMIN`, `MANAGER`), customer organizations (`CUSTOMER`, `MAINTENANCE_ENGINEER`), and independent partner pilots (`INSPECTOR`) are strictly segregated by `ActorZone`, organization ownership, and explicit mission assignment.
- **No Direct Drone Flight Control**: The platform governs commercial contracts, aviation compliance documents, field session logs, aerial photo/video evidence, AI/RAG analysis, reporting, and maintenance work orders; physical aircraft piloting is performed by licensed partner pilots using their own flight controllers.
- **Human-in-the-Loop AI & RAG Governance**: `YOLO11` defect detections, Vision LLM fallbacks, AI Executive Summaries, and `pgvector` RAG scope/norm/compliance outputs are advisory decision-support tools. Every official finding, published report, and maintenance budget or acceptance decision requires explicit human confirmation.

#### 5.4.2 Feature and Flow Traceability

This traceability matrix maps the **eight core product features (`FE-01` to `FE-08`, two features per team member)** to system use cases and main workflows (`MF1` to `MF4`).

| Product Feature | Feature Name | Operational Responsibility & Owner | Supported Use Cases |
| :---: | --- | --- | --- |
| `FE-01` | Authentication, Google OAuth2 & 5-Role Access Control | Customer registration with initial asset & airspace gate, Argon2id & Google OAuth2 sign-in (Web & Mobile deep-link), `/users/me` profile, and 5-role `ActorZone` RBAC *(Trần Tùng Bách)* | UC-01, UC-02, UC-03, UC-28 |
| `FE-02` | Partner Onboarding, Workforce, Asset & Inspector Drone Registry | Partner Inspector license/contract review (drone optional at signup), Customer Maintenance Engineer provisioning, Asset catalog with No-Fly Zone guard, and Inspector-owned Drone 3-document review *(Trần Hoàng Trung Hiếu)* | UC-02, UC-04, UC-05, UC-06 |
| `FE-03` | Recurring Schedules, Contract Occurrences & Outbox Notifications | Timezone-anchored recurring inspection schedules, multi-occurrence contract inheritance (Decision D2), and deduplicated Spring Modulith outbox notifications *(Trần Hoàng Trung Hiếu)* | UC-07, UC-08, UC-20 |
| `FE-04` | Service Requests, Quotations, Contracts, Dispatch & Airspace Map | One-time/recurring Service Requests, VND/USD quotes, Order Chat, signed paper contract upload, cross-org partner dispatch, abort re-dispatch, and Vietnam Airspace Map *(Phùng Trung Quốc)* | UC-07, UC-08, UC-09, UC-13 |
| `FE-05` | Flight Permit Gate, Field Execution, Dashboard & Calendar | Aviation flight permit upload gate, Web/Mobile field sessions (`Start`, `Complete`, `Abort`), 5-role analytics dashboard, Inspector calendar, and Customer 5-stage Progress Tracker *(Phùng Trung Quốc)* | UC-10, UC-11, UC-12, UC-20 |
| `FE-06` | Evidence Intake, YOLO11 Detection, Auto-Compiled Report & PayOS | Photo & MP4 video streaming (`file_picker`, `AuthenticatedMedia`), `YOLO11` + Vision fallback, findings preview, tab-visit auto-compiled report (`SUBMITTED`), AI Executive Summary, Manager PDF publish (`PUBLISHED`), and PayOS VietQR settlement *(Trần Tùng Bách)* | UC-14, UC-15, UC-16, UC-17, UC-18, UC-19 |
| `FE-07` | Maintenance Work Orders, RAG Scope/Norms Advisor & Repair Execution | Defect handoff to Work Order, `pgvector` RAG Scope Advisor with 1-click initial tasks, team assignment, RAG Cost Norms Estimator (`suggest-estimate`), Customer budget/Change Order approval, and 1-click batch work-log verification *(Trương Thái Như)* | UC-21, UC-22, UC-23, UC-24 |
| `FE-08` | Completion Report, 3-Way Re-inspection Verification & Cost Closure | Smart auto-drafted Maintenance Completion Report (`auto-draft`), RAG Acceptance Compliance Audit (`acceptance-compliance`), 3-step/3-way Re-inspection defect verification loop, independent Customer acceptance, cost reconciliation, and Work Order closure *(Trương Thái Như)* | UC-25, UC-26, UC-27, UC-28 |

#### 5.4.3 Research Basis and References

- **Non-Destructive Testing & Inspection Reporting:** Incorporates American Society for Nondestructive Testing (ASNT) guidelines regarding reproducible inspection techniques, explicit equipment and methodology disclosure, and attributable technician accountability. Visual capture annotations follow Pix4D inspection reporting benchmarks.
- **Maintenance Lifecycle & Work Order Governance:** Maintenance workflows reflect standards from enterprise asset management benchmarks (Oracle PeopleSoft Maintenance Management, IBM Maximo), distinguishing physical task completion from formal administrative and financial closure.
- **Cost Estimation & Engineering Change Control:** Engineering change orders follow established principles from construction and plant engineering (Primavera Unifier) and Vietnamese construction norms (`TCVN 9343:2012`, `EN 1504-9`, `ISO 12944-5`), enforcing itemized cost baselines, explicit change justification, and independent budget approval.
- **Artificial Intelligence Governance:** AI defect detection, executive summaries, and RAG advisories comply with National Institute of Standards and Technology (NIST AI 600-1) recommendations on generative artificial intelligence risk management, ensuring source-grounded synthesis and mandatory human oversight.
- **Civil Aviation Regulations:** Drone compliance references Vietnamese Government Decision No. 18/2020/QĐ-TTg and Decree No. 288/2025/NĐ-CP governing prohibited/restricted airspace zones and unmanned aerial vehicles, enforcing flight permit verification, 3-document drone registration, and remote pilot credential tracking.

- [1] ASNT Pulse. *Nondestructive Testing Report Writing: Back to Basics*. American Society for Nondestructive Testing. https://www.asnt.org/standards-publications/blog/nondestructive-testing-report-writing-back-to-basics
- [2] Oracle Corporation. *PeopleSoft Maintenance Management Process Flow*. Oracle Help Center. https://docs.oracle.com/en/applications/peoplesoft/financials-and-supply-chain-management/9.2.056/peoplesoft-maintenance-management/peoplesoft-maintenance-management-process-flow.html
- [3] IBM Corporation. *Maximo Manage: Work Order Statuses*. IBM Documentation. https://www.ibm.com/docs/en/maximo-manage/cd?topic=orders-work-order-statuses
- [4] Oracle Corporation. *Primavera Unifier: Change Order Business Process*. Oracle Help Center. https://docs.oracle.com/en/industries/construction-engineering/primavera-unifier/26/accelerator-user/changeorderbusinessprocess-10296629a.html
- [5] National Institute of Standards and Technology. *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile (NIST AI 600-1)*. U.S. Department of Commerce. https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
- [6] Chính phủ nước Cộng hòa Xã hội Chủ nghĩa Việt Nam. *Nghị định số 288/2025/NĐ-CP: Quy định về quản lý tàu bay không người lái và phương tiện bay khác*. Cổng Thông tin điện tử Chính phủ. https://vanban.chinhphu.vn/?docid=215810&pageid=27160
- [7] Pix4D. *Annotations Report - PIX4Dcloud Pro*. Pix4D Support. https://support.pix4d.com/hc/en-us/articles/13552115283613
- [8] Oracle Corporation. *Understanding Work Orders in Maintenance Management*. Oracle Documentation. https://docs.oracle.com/cd/G47724_01/fscm92pbr55/eng/fscm/fwkm/UnderstandingWorkOrders-c9f12c.html
