---
title: "Report 3 - Non-Functional Requirements"
document_type: report3-srs-section
weight: 45
source: "report3-software-requirement-specification.docx"
---

## 4. Non-Functional Requirements

### 4.1 External Interfaces

- **Web Service Interface**: The service shall be available through a responsive web experience on current, commonly used desktop and mobile browsers. User-facing labels and guidance shall support English and Vietnamese.
- **Mobile Service Interface**: Field users shall be able to access assigned inspections and maintenance activities from supported Android and iOS devices, including viewing relevant records, providing required documents, recording field sessions, uploading inspection evidence, and recording repair work.
- **Advisory Information**: Where automated inspection or maintenance guidance is available, the service shall clearly distinguish suggestions from confirmed findings, approved work, and final human decisions.
- **Payment, Identity, Mapping and Reference Information**: The service shall provide appropriate sign-in, service-payment, location and airspace information, and reference material needed for the agreed business workflows. An external service response does not replace the service's own authorization or human review obligations.

### 4.2 Quality Attributes

#### 4.2.1 Usability

- **Understandable Workflow**: Each inspection and maintenance stage shall clearly communicate its purpose, current status, responsible role, required next action, and any decision or evidence still needed.
- **Efficient Field and Office Work**: Users shall be able to review assigned work, provide required evidence, and complete frequent verification and reporting tasks without unnecessary repetition. Any suggested or prepared content remains subject to user review before submission or approval.
- **Clear Advisory and Verification Labels**: Automated candidate findings, report summaries, and maintenance guidance shall be identified as advisory. Re-inspection results shall make the original defect, repair evidence, and new inspection evidence distinguishable.
- **Bilingual Support**: Users shall be able to work with the service in English or Vietnamese. User-facing generated reports shall use the language selected or required for the engagement.

#### 4.2.2 Reliability

- **Service Availability**: The service shall target availability of at least `99.5%` during standard operating hours (`06:00–22:00 ICT`). This is an acceptance target, not a claim of measured current availability.
- **Recovery and Backup**: Service records and documents shall be backed up daily. The recovery-time target is `30 minutes` or less. This is an acceptance target, not evidence that backup or recovery has been tested.
- **Degraded External Services**: Unavailability of automated analysis or external payment services shall not cause the service to record an unconfirmed finding or payment as confirmed. The business process shall provide an appropriate manual or deferred path where authorized, and identify any resulting decision for accountable review.
- **Financial and Record Integrity**: VND service prices, taxes, platform fees, maintenance estimates, approved changes, and actual costs shall be calculated and recorded consistently with their stated currency and agreed financial rules. Signed service documents, official reports, and accepted maintenance records shall be protected from unauthorized alteration; changes to issued records shall be attributable and preserve prior versions. No particular checksum method is prescribed.

#### 4.2.3 Performance

- **User Response Time**: Under normal operating conditions, at least 95% of standard user actions, searches, and paged list views shall complete within `2.0 seconds` with `50` active users. This is a performance acceptance target, not a report of measured performance.
- **Advisory Analysis**: A single-image defect suggestion and a maintenance guidance request shall complete within `5.0 seconds` under normal operating conditions, for supported inputs. This is a target for responsive user interaction, not an assertion about existing analysis services.
- **Media Access**: Supported inspection videos and images shall be made available for review without making the rest of the user experience unusable during transfer.

#### 4.2.4 Security and Maintainability

- **Organization and Assignment Privacy**: Users shall access only information permitted by their role, customer organization, partner relationship, and explicit work assignment. Direct links, notifications, or knowledge of a record must not grant additional access.
- **Role Permissions and Independent Decisions**: The service shall enforce the role responsibilities in this specification. Report authors cannot review or publish their own reports. Members of an executing repair team cannot approve its budget or make final acceptance of their own work.
- **Account and Session Protection**: Passwords and active access shall be protected against unauthorized use. The service shall restrict repeated failed sign-in attempts and end affected active sessions after security-sensitive account changes or revocation.
- **Attributable Activity History**: Important onboarding, commercial, assignment, inspection, publication, payment, budget, maintenance, and acceptance decisions shall be recorded with the responsible actor and relevant time. Historical activity records shall not be silently rewritten.

**Summary of Quantified Non-Functional Requirements (`NFR-01` to `NFR-06`)**

The thresholds below are requirements and acceptance targets. They are not evidence that the current service meets them. Verification must be performed and recorded separately.

| NFR ID | Category | Requirement Statement | Metric | Target Threshold | Verification Method |
| :---: | --- | --- | --- | --- | --- |
| `NFR-01` | Performance | Standard user actions, searches, and paged list views respond promptly under concurrent use. | 95th percentile response time and server error rate. | `p95 <= 2.0 seconds` and `0%` server errors under `50` concurrent users. | Concurrent user-journey and list-view assessment. |
| `NFR-02` | Performance | Supported image analysis and maintenance guidance remain within interactive response limits under normal conditions. | Processing time per supported image or advisory request. | `<= 5.0 seconds` per request. | Timed assessment of supported user workflows under stated conditions. |
| `NFR-03` | Security | Users are prevented from accessing records or actions outside their role, organization, partner relationship, or assignment. | Unauthorized and cross-scope access attempts blocked. | `100%` blocked; `0` unauthorized disclosures. | Role, organization, and assignment access assessment. |
| `NFR-04` | Security | Sign-in resists repeated password guessing and revoked access cannot continue to be used. | Failed sign-in lockout threshold and sign-in request rate. | Account restriction for `15 minutes` after `5` failed attempts; more than `10` sign-in requests per minute blocked. | Sign-in and access-revocation assessment. |
| `NFR-05` | Reliability | Signed service documents, asset reference documents, and published reports remain intact; published records cannot be silently altered. | File integrity and prevention of unauthorized in-place changes. | `100%` integrity for retained records; `100%` of unauthorized in-place changes prevented. | Document retention, access, and version-history assessment. |
| `NFR-06` | Maintainability | Core business rules and all eight product features (`FE-01`–`FE-08`) have repeatable verification and remain understandable to maintainers. | Business-rule and feature verification coverage; review of internal structure. | All eight features have applicable verification cases; no unresolved structural violations. | Review of test evidence and maintainability assessment. |
