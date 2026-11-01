---
title: "Report 3 - Non-Functional Requirements"
document_type: report3-srs-section
weight: 45
source: "report3-software-requirement-specification.docx"
---

## 4. Non-Functional Requirements

### 4.1 External Interfaces

- **Web Portal Interface**: Responsive React 19 web application segmented into three role-scoped portals (`/admin`, `/client`, `/operations`) accessible over HTTPS on modern browsers (Google Chrome, Microsoft Edge, Mozilla Firefox, Apple Safari), supporting Light and Dark themes and bilingual English/Vietnamese (`EN`/`VI`) localization.
- **Mobile Application Interface**: Cross-platform Flutter mobile application (Android and iOS) for partner Inspectors and Maintenance Engineers supporting Google OAuth2 deep-link sign-in (`smartdrone://auth`), airspace advisories, flight permit uploads, field flight session logging (`Start`, `Complete`, `Abort`), streaming photo/MP4 video evidence intake (`file_picker`), and field repair work logging.
- **AI Defect Detection, Executive Summary & RAG Advisory Interfaces**: Internal service adapters connecting to `YOLO11` (with Vision LLM fallback) for defect candidate detection, LLM report synthesis for automated executive summaries, and `pgvector`-backed Retrieval-Augmented Generation (`TCVN`, `ACI`, `EN 1504`, `ISO 12944`, `ASTM`) for maintenance repair scope, cost norms estimation, and technical acceptance compliance auditing.
- **Online Payment, OAuth2 & Mapping Interfaces**: Integration with **PayOS** for VietQR online payment link generation and HMAC-SHA256 webhook verification on accepted inspection reports, **Google OAuth2** for federated authentication, and **OpenStreetMap / Nominatim** layers for Vietnam infrastructure address lookup and Decision 18/2020/QD-TTg / Decree 288/2025/ND-CP airspace evaluation.

### 4.2 Quality Attributes

#### 4.2.1 Usability

- **Streamlined Workflow & Auto-Compilation**: Inspections follow 6 canonical states (`SCHEDULED`, `IN_PROGRESS`, `FIELD_COMPLETED`, `UNDER_REVIEW`, `COMPLETED`, `CANCELLED`) and reports follow 5 states (`SUBMITTED`, `RETURNED`, `APPROVED`, `PUBLISHED`, `SUPERSEDED`) with automatic compilation on tab visit, eliminating redundant manual draft buttons and free-text note duplication.
- **1-Click Maintenance Acceleration**: Engineers and Team Leads can initialize tasks from RAG suggestions in 1 click, batch-verify submitted work logs in 1 click, auto-draft completion reports from field logs, and pre-fill cost reconciliation lines from approved baselines.
- **Clear AI & Verification Labeling**: AI defect candidates, LLM executive summaries, and RAG compliance checks are explicitly badged as advisory, while re-inspection missions present a side-by-side 3-way verification card (Prior Defect vs Repair Handover Proof vs Drone Re-capture).
- **Bilingual Support**: Users can switch seamlessly between English (`EN`) and Vietnamese (`VI`) across Web, Mobile, and generated PDF reports.

#### 4.2.2 Reliability

- **Service Availability**: Target system availability is at least `99.5%` during standard operating hours (`06:00–22:00 ICT`).
- **Recovery & Backup**: Automated daily PostgreSQL and MinIO backups allow recovery within `30 minutes` (`MTTR <= 30 minutes`).
- **Deterministic Fallback When AI or External Gateways Are Offline**: If `YOLO11`, the Vision/Summary LLM, `pgvector` RAG, or PayOS is temporarily unavailable, the system falls back deterministically to manual finding entry, deterministic report compilation, standard TCVN engineering templates, and manual payment confirmation by a Platform Manager.
- **Accurate Financial & Document Integrity**: All VND and USD service quotes, VAT, platform commissions, PIT/TNCN withholdings, repair estimates, Change Orders, and actual costs are computed using exact decimal arithmetic, and signed contracts and published PDF reports are protected with `SHA-256` checksums.

#### 4.2.3 Performance

- **Screen & Action Response Time**: At least `95%` of standard user actions, searches, and paginated list loads complete within `2.0 seconds` under normal concurrent usage (`50` active users).
- **AI Defect Detection & Streaming Media**: Single-image AI defect analysis completes within `5.0 seconds` for inspection photographs up to `10 MB`, and MP4 video evidence up to `10 MB` streams via chunked HTTP/Blob delivery without blocking the UI.
- **Optimized Frontend Bundle**: Code-split portal routes keep initial bundle load fast across Admin, Client, and Operations workspaces.

#### 4.2.4 Security and Maintainability

- **Strict Multi-Zone & Tenant Isolation**: Every user account is bound to an `ActorZone` (`PLATFORM`, `CUSTOMER_ORGANIZATION`, `INSPECTOR_PARTNER`, `PROSPECT_CUSTOMER`). Customers and Maintenance Engineers can access only their own organization's assets, contracts, reports, and work orders, while partner Inspectors can access only missions explicitly assigned to them.
- **Role-Based Permissions & Separation of Duties**: Authors cannot review or publish their own inspection reports, and executing repair team members cannot approve their own budgets or perform final technical acceptance on their own work orders.
- **Account & Session Protection**: Passwords use `Argon2id` hashing, accounts lock for `15 minutes` after `5` failed sign-in attempts, and active JWT/refresh sessions are immediately invalidated upon role, password, or status changes.
- **Cryptographic Audit Trail**: Critical lifecycle transitions — onboarding approvals, quote acceptance, signed contract uploads, mission dispatch, field aborts, report publication, PayOS settlement, budget approvals, and work order closure — are recorded in an append-only audit log.

**Summary of Quantified Non-Functional Requirements (`NFR-01` to `NFR-06`)**

| NFR ID | Category | Requirement Statement | Metric | Target Threshold | Verification Method |
| :---: | --- | --- | --- | --- | --- |
| `NFR-01` | Performance (System Response) | Standard list views, searches, and workflow actions must respond quickly under multi-user load. | 95th percentile (`p95`) response time and error rate. | `p95 <= 2.0 seconds` and `0%` server errors under `50` concurrent users. | Automated concurrent API and pagination verification (`FE-04`, `FE-05`). |
| `NFR-02` | Performance (AI Detection & RAG) | On-demand `YOLO11` defect detection (with Vision fallback) and RAG advisory queries must complete within interactive limits. | Processing time per image (up to `10 MB` JPEG/PNG) or RAG query. | `<= 5.0 seconds` per request (with deterministic fallback if offline). | Automated AI inference and RAG advisor integration tests (`FE-06`, `FE-07`). |
| `NFR-03` | Security (ActorZone & Role Isolation) | Users must be blocked from accessing screens or records belonging to another organization, unassigned partner mission, or unauthorized role. | Rejection rate for unauthorized role, zone, or cross-organization requests. | `100%` of unauthorized or cross-scope requests blocked (`0` data leaks). | Automated 5-role matrix and cross-tenant security test suite (`FE-01`, `FE-04`, `FE-06`). |
| `NFR-04` | Security (Sign-In & OAuth2 Protection) | Sign-in endpoints must block brute-force password guessing, invalid OAuth2 states, and revoked sessions. | Failed sign-in lockout threshold and rate limit per network address. | Account locks for `15 minutes` after `5` failed attempts; `> 10` sign-in requests per minute blocked. | Automated authentication, OAuth2, and rate-limit test suite (`FE-01`). |
| `NFR-05` | Reliability (Contract & PDF Integrity) | Uploaded signed contracts, asset documents, and published PDF reports must remain intact and immutable after publication. | `SHA-256` checksum match rate and post-publish edit rejection rate. | `100%` file integrity verification; `100%` of in-place edits to published reports blocked. | Automated PDF publication, contract checksum, and immutability test (`FE-04`, `FE-06`). |
| `NFR-06` | Maintainability (Automated Testing & Modulith Boundaries) | Core business rules, Spring Modulith boundaries, and workflows must be continuously verified by automated tests. | Automated unit/integration coverage and architectural boundary compliance. | `>= 80%` backend JaCoCo gate, `0` Modulith violations, and all 8 features (`FE-01`–`FE-08`) covered by automated tests. | Continuous integration verification across Backend, Frontend, Mobile, and Docs (`FE-01`–`FE-08`). |
