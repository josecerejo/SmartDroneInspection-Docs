---
title: "Report 3 - Requirement Appendix"
document_type: report3-srs-section
weight: 55
source: "report3-software-requirement-specification.docx"
---

## 5. Requirement Appendix

### 5.1 Business Rules

The following normative business rules govern role and organization boundaries, partner onboarding, commercial agreements, aviation readiness, evidence and reporting, payment, and corrective maintenance. They state required business outcomes and do not assert that a capability is already implemented.

| ID | Rule Definition |
| --- | --- |
| BR-01 | `ADMIN` and `MANAGER` perform platform responsibilities. `CUSTOMER` and `MAINTENANCE_ENGINEER` act within a customer organization. `INSPECTOR` acts as a partner and may be assigned across customer organizations only through an authorized dispatch. |
| BR-02 | A `CUSTOMER` accesses and manages only their own organization's assets, workforce, service requests, published inspection reports, and maintenance work orders. |
| BR-03 | A `MAINTENANCE_ENGINEER` belongs to one customer organization. A partner `INSPECTOR` may serve different customer organizations only through an explicit `MANAGER` assignment. |
| BR-04 | An `INSPECTOR` or `MAINTENANCE_ENGINEER` may act only on inspection or maintenance work assigned to them. |
| BR-05 | Partner Inspectors must have current pilot credentials for flight assignment and field work. An expired credential prevents the Inspector from being assigned or starting field work. |
| BR-06 | Customer onboarding screens the initial asset location against applicable Vietnam airspace information. A prohibited No-Fly Zone location is not accepted; a location requiring review remains pending for an `ADMIN` decision; a location that passes screening may proceed. Screening does not grant governmental flight clearance. |
| BR-07 | Before starting an on-site field session, the assigned Inspector must provide the required flight permit, have current pilot credentials, and record a pre-flight safety note addressing aircraft, battery, and environmental suitability. |
| BR-08 | Airspace checks and flight permit records support internal readiness review only; they do not grant a government aviation exemption or clearance under applicable regulations. |
| BR-09 | Inspection assignment and reassignment must consider overlapping commitments across all customer organizations so that a partner Inspector or drone is not double-booked. |
| BR-10 | Service quotations are stated in VND per occurrence, identify the agreed scope and timing, and are associated with an eligible partner Inspector and a drone owned by that Inspector. |
| BR-11 | Commercial service requests proceed through request, quotation, customer acceptance, signed agreement, and occurrence assignment. Negotiation messages do not change quotation terms. Dispatch is not ready until the parties have signed the offline agreement and `MANAGER` has recorded it. |
| BR-12 | Service quotations, inspection reports, maintenance estimate baselines, change requests, and acceptance decisions preserve attributable versions. Published records cannot be silently modified in place. |
| BR-13 | For a recurring service request, one signed agreement may cover the occurrences within the agreed term. Each occurrence still requires its own partner assignment, flight readiness review, report, and settlement. |
| BR-14 | Field sessions record normal completion or abort. An abort requires a reason and alerts `MANAGER` to reschedule, reassign, or cancel the inspection. The software record does not control or reverse a physical flight. |
| BR-15 | Inspection progress must distinguish scheduled, active field work, field completion, report review, completion, and cancellation. Flight readiness is an eligibility decision, not evidence of governmental clearance. |
| BR-16 | Aircraft operation and physical structural repair are real-world actions performed by qualified people. The service's session and workflow records do not actuate aircraft or perform repairs. |
| BR-17 | Inspection evidence retains its identity, upload time, and available capture information. Missing location or camera metadata is identified rather than invented. |
| BR-18 | Duplicate evidence within the same inspection is identified and prevented from being treated as a separate independent capture without review. |
| BR-19 | Missing GPS or camera metadata does not automatically invalidate otherwise suitable visual or video evidence; the missing information must remain apparent to reviewers. |
| BR-20 | AI-generated defect suggestions remain advisory until the assigned `INSPECTOR` reviews them. Only human-confirmed findings become official inspection findings. |
| BR-21 | Rejected and unconfirmed AI suggestions are excluded from official defect reporting, inspection reports, and maintenance scope. |
| BR-22 | Inspectors may record manual findings supported by inspection evidence. If automated analysis is unavailable, manual evidence review and findings confirmation remain possible. |
| BR-23 | After confirming the findings baseline, the report author prepares and explicitly submits the inspection report for review. Visiting a report screen alone does not submit it. |
| BR-24 | A `MANAGER` or `ADMIN` distinct from the report author independently reviews the submitted report, approves or returns it with reasons, and publishes the official report. An `INSPECTOR` cannot review or publish their own report. |
| BR-25 | Customers may follow in-progress inspection status but cannot access internal field records, unconfirmed findings, or unpublished reports as official deliverables. |
| BR-26 | Published inspection reports are preserved. Any correction is issued as a new version, with prior versions retained for reference. Publication does not imply governmental or professional certification. |
| BR-27 | Commercial, reporting, and engineering approvals require explicit, attributable human decisions. Silence or passage of time is not approval. |
| BR-28 | Returning an inspection or maintenance report requires review reasons, preserves the prior version, and returns the work to the responsible author for revision. |
| BR-29 | `ADMIN` and `MANAGER` govern platform operations, partner onboarding, commercial agreements, and inspection report publication. They do not approve a Customer's internal maintenance budget or change request. |
| BR-30 | Service workflow approvals are auditable business decisions; they do not constitute statutory engineering seals or governmental aviation authorizations. |
| BR-31 | A maintenance work order must refer to a confirmed defect from a published inspection report belonging to the same customer organization. |
| BR-32 | Cost guidance is advisory. The `MAINTENANCE_ENGINEER` preparing an estimate and the `CUSTOMER` approving it remain accountable for the final budget. |
| BR-33 | When a Customer accepts a published inspection report, the applicable service fee becomes due. The official deliverable is made available according to the agreed payment rule after payment is confirmed. Partner settlement is separately tracked. |
| BR-34 | Any increase in repair scope, cost, or schedule requires prior Customer approval through a change request. The approved estimate baseline remains available for comparison, and work cannot be declared complete while a change request is pending. |
| BR-35 | Maintenance work records include relevant task outcomes, before-and-after repair evidence, and test readings. The completion report is prepared from these records and reviewed by its author before submission. |
| BR-36 | Inspection service fees are settled per occurrence under the agreed commercial terms. Maintenance estimates and actual expenditures are recorded as the Customer organization's maintenance costs. |
| BR-37 | When a Customer requests re-inspection, the resulting verification is linked to the relevant work order, source inspection, report, and target findings. An additional session within the original inspection is distinguished from a separate maintenance re-inspection. |
| BR-38 | Important onboarding, quote acceptance, agreement recording, partner assignment, field abort, findings confirmation, report publication, payment, budget, re-inspection, and work-order decisions are recorded with the responsible actor. |
| BR-39 | A direct link, notification, or document reference does not grant access. Role, organization, assignment, and payment conditions apply to every attempt to view or act on a record. |
| BR-40 | Password changes, role updates, account changes, and session revocations take effect for active access without removing historical attribution. |
| BR-41 | Partner admission does not require drone ownership. After partner account provisioning, an Inspector may register an owned drone by providing `REGISTRATION`, `OWNERSHIP`, and `INSPECTION` documents. `ADMIN` or `MANAGER` reviews the drone registration before the drone is used for a quotation or mission. In the current service, platform staff provision Inspector accounts; self-service Inspector applications are not available. |
| BR-42 | Infrastructure asset registration is subject to the No-Fly Zone screening rule and identifies relevant inspection checkpoints for future work on that asset. |
| BR-43 | For each target defect in a re-inspection, the Inspector compares the prior defect, repair evidence, and new inspection evidence, and records `RESOLVED`, `UNRESOLVED`, or `INCONCLUSIVE`. |
| BR-44 | Inspection reports follow submission, return, approval, publication, and supersession outcomes. Publishing a re-inspection report links it to the related work order so the Customer can complete acceptance review. |
| BR-45 | Each maintenance work order designates a Team Lead, a Report Author, an independent Customer Budget Approver, and an independent Customer Accepting Reviewer. An executing repair team member cannot approve the budget or accept the work. |
| BR-46 | Repair tasks are assigned to approved team members. A designated Team Lead verifies submitted work records before the work order can be declared complete. |
| BR-47 | Quotations, taxes or fees, maintenance estimates, change requests, and actual costs state their currency and are calculated consistently without avoidable rounding error. Current service quotations are stated in VND. |
| BR-48 | AI report summaries and maintenance guidance use verified findings, field readings, or relevant reference material as applicable. They remain advisory and require human review; any fallback must not fabricate verification or approval. |
| BR-49 | A maintenance work order may be closed only after an independent `CUSTOMER` reviewer records acceptance, including review of the re-inspection report where required, and actual costs have been reconciled against the approved baseline and changes. |

### 5.2 Common Requirements

- **Form Validation**: Forms explain required information and reject incomplete, invalid, out-of-range, or inconsistent information before a business decision is recorded.
- **Role, Organization, and Assignment Checks**: Every business action is limited by the user's role, organization, partnership, and explicit assignment. Access to a screen does not imply authority to act.
- **Date, Time, and Timezone Display**: Dates and times are displayed clearly in the relevant organization's or service schedule's timezone. The time of each important decision remains attributable.
- **Currency and Financial Precision**: Service quotations use VND. Applicable service fees, taxes, platform charges, maintenance estimates, changes, and actual costs state their currency and are calculated consistently.
- **Evidence and Document Handling**: Inspection media, agreements, qualification records, and reports are checked for suitability before acceptance and shown only to authorized users. File limits and supported formats are communicated to users.
- **Idempotent User Actions**: Repeated submissions or external notifications must not create duplicate occurrences, evidence records, payments, work verifications, or lifecycle notices.
- **Document Integrity and Version History**: Signed service agreements, published inspection reports, and accepted maintenance completion records are protected against unauthorized alteration. A change to an issued record must be attributable, preserve its history, and be available as a distinct version; no particular checksum method is prescribed.

### 5.3 Application Messages List

The service provides clear user-facing messages for common results, validation needs, and workflow decisions. These examples describe intended service communication and do not claim current implementation.

| # | Message code | Message Type | Context | Content |
| --- | --- | --- | --- | --- |
| 1 | MSG01 | Inline | Search has no authorized records | No results found. |
| 2 | MSG02 | Under field | Required field empty | This field is required. |
| 3 | MSG03 | Under field | Configured length exceeded | Must not exceed {maxLength} characters. |
| 4 | MSG04 | Under field | Invalid email | Enter a valid email address. |
| 5 | MSG05 | Toast | Record created | Created successfully. |
| 6 | MSG06 | Toast | Record updated | Updated successfully. |
| 7 | MSG07 | Dialog | Irreversible or versioned action | Confirm this action and the version you are acting on. |
| 8 | MSG08 | Inline | Sign-in failed | Email or password is incorrect. |
| 9 | MSG09 | Inline | Disabled or suspended account | Unable to sign in. Contact your administrator. |
| 10 | MSG10 | Inline | Expired or revoked access | Your session has expired. Sign in again. |
| 11 | MSG11 | Under field | Password policy failure | Password does not meet the security requirements. |
| 12 | MSG12 | Toast | Inspection dispatched | Inspection scheduled with its asset and assigned partner. |
| 13 | MSG13 | Inline | Newer quotation or report version available | A newer version is available. Refresh and review it before continuing. |
| 14 | MSG14 | Toast | Quote or assignment accepted | Accepted successfully. |
| 15 | MSG15 | Under field | Rejection or abort lacks reason | Enter a reason before submitting. |
| 16 | MSG16 | Inline | Unsupported, damaged, or oversized file | This file cannot be uploaded. Check its type and size. |
| 17 | MSG17 | Inline | Duplicate evidence | This evidence file has already been provided for this inspection. |
| 18 | MSG18 | Toast | Evidence received | Evidence is available for review. |
| 19 | MSG19 | Inline | Automated advisory unavailable | Automated guidance is unavailable. Continue with the applicable human review process. |
| 20 | MSG20 | Toast | Inspection report submitted | Inspection report submitted for independent review. |
| 21 | MSG21 | Inline | Candidate findings remain unreviewed | Review all suggested findings before confirming the findings baseline. |
| 22 | MSG22 | Toast | Inspection report published | Approved inspection report published and available to the Customer. |
| 23 | MSG23 | Toast | Repair change request submitted | Scope, cost, or schedule change submitted to the Customer for approval. |
| 24 | MSG24 | Inline | Additional work not approved | Additional work requires Customer approval before it proceeds. |
| 25 | MSG25 | Toast | Work order closed | Accepted and cost-reconciled work order closed; its history is preserved. |
| 26 | MSG26 | Inline | Required qualification or document missing | Provide all required qualification and supporting documents. |
| 27 | MSG27 | Toast | Compliance document recorded | Document review recorded. Internal review does not replace statutory authorization. |
| 28 | MSG28 | Inline | Airspace alert | Location is within a prohibited area or requires review before proceeding. |
| 29 | MSG29 | Toast | Request or quotation recorded | Service request or quotation saved. |
| 30 | MSG30 | Toast | Report or estimate returned | Returned to the author with review reasons. |
| 31 | MSG31 | Inline | Independent reviewer missing | Assign a reviewer who is not the author or a member of the executing team. |
| 32 | MSG32 | Under field | Pre-flight safety note incomplete | Enter the required safety note before starting the field session. |
| 33 | MSG33 | Inline | Findings changed after report preparation | Confirm the findings and review the report before submitting it. |
| 34 | MSG34 | Toast | Budget approved | Repair scope and estimate approved by the Customer. The original baseline is preserved. |
| 35 | MSG35 | Toast | Signed agreement recorded | Signed service agreement recorded. |
| 36 | MSG36 | Inline | Partner or drone cannot be assigned | Select an eligible Inspector and an owned, approved, available drone. |
| 37 | MSG37 | Inline | Permit or current qualification missing | Cannot start field work. Provide the mission permit and current pilot credentials. |
| 38 | MSG38 | Toast | Findings baseline confirmed | Findings baseline confirmed. Prepare and submit the report for review. |
| 39 | MSG39 | Inline | Advisory summary unavailable | Automated summary is unavailable. Review the confirmed findings directly. |
| 40 | MSG40 | Inline | Maintenance responsibility missing | Assign a Team Lead and Report Author before repair work begins. |
| 41 | MSG41 | Inline | Invalid cost information | Enter valid quantities, rates, and currency. |
| 42 | MSG42 | Toast | Work records verified and repair completed | Submitted work records were verified and repair work was declared complete. |
| 43 | MSG43 | Inline | Unverified work or pending change request | Verify submitted work records and resolve pending changes before declaring work complete. |
| 44 | MSG44 | Inline | Self-approval or self-acceptance blocked | Authors and executing repair team members cannot approve their own budgets or accept their own work. |
| 45 | MSG45 | Inline | Cost reconciliation required | Reconcile actual costs against the approved budget and changes before closing the work order. |
| 46 | MSG46 | Toast | Completion report submitted | Maintenance completion report submitted to the Customer for acceptance review. |
| 47 | MSG47 | Toast | Payment confirmed | Inspection service payment confirmed. |
| 48 | MSG48 | Inline | Payment required for deliverable | Accept the published report and complete the required service payment to access the official deliverable. |

### 5.4 Other Requirements

#### 5.4.1 Scope and Operational Constraints

- **Role and Organization Separation**: Platform responsibilities (`ADMIN`, `MANAGER`), customer organization responsibilities (`CUSTOMER`, `MAINTENANCE_ENGINEER`), and partner Inspector responsibilities (`INSPECTOR`) are separated by role, organization ownership, and explicit assignment.
- **No Direct Drone Flight Control**: The service governs agreements, compliance documents, field-session records, evidence, analysis, inspection reports, and maintenance work orders. Licensed partner pilots perform physical aircraft operation using their own flight equipment.
- **Human Review of AI and Guidance**: Automated defect suggestions, report summaries, repair-scope and cost recommendations, and compliance guidance are advisory. Official findings, published reports, budgets, and acceptance decisions require explicit human confirmation.
- **Qualification and Legal Authority**: A service status or recorded document does not prove professional qualification or government flight clearance. Users and organizations remain responsible for obtaining any required external authorization.

#### 5.4.2 Feature and Flow Traceability

This traceability matrix maps the eight product features (`FE-01` to `FE-08`) to business responsibilities and use cases.

| Product Feature | Feature Name | Operational Responsibility | Supported Use Cases |
| :---: | --- | --- | --- |
| `FE-01` | Customer Registration, Sign-in and Account Access | Customer onboarding with initial asset screening; account security and role-appropriate access | UC-01, UC-02, UC-03, UC-28 |
| `FE-02` | Partner Onboarding, Workforce, Assets and Drone Registration | Inspector applications and qualifications; Customer workforce; asset screening; Inspector-owned drone documentation and review | UC-02, UC-04, UC-05, UC-06 |
| `FE-03` | Recurring Service Requests, Occurrences and Notifications | One-time and recurring requests, agreed occurrence coordination, and notices | UC-07, UC-08, UC-20 |
| `FE-04` | Service Requests, VND Quotations, Agreements and Dispatch | Request negotiation, VND quotations, signed agreement, partner assignment, and dispatch changes | UC-07, UC-08, UC-09, UC-13 |
| `FE-05` | Flight Readiness, Field Sessions and Progress | Permit and qualification checks, field-session records, schedules, and Customer progress | UC-10, UC-11, UC-12, UC-13, UC-20 |
| `FE-06` | Evidence, Findings, Reporting and Payment | Evidence intake, human-confirmed findings, explicit report preparation, independent publication, Customer acceptance, and service payment | UC-14, UC-15, UC-16, UC-17, UC-18, UC-19 |
| `FE-07` | Maintenance Work Orders, Estimates and Repair Execution | Corrective work orders, advisory scope and estimates, Customer budget/change approval, assigned repair work and verification | UC-21, UC-22, UC-23, UC-24 |
| `FE-08` | Completion, Re-inspection and Work-Order Closeout | Completion reporting, re-inspection, independent Customer acceptance, cost reconciliation, and closure | UC-25, UC-26, UC-27, UC-28 |

#### 5.4.3 Research Basis and References

- **Inspection Reporting and Nondestructive Testing**: Requirements reflect established guidance on reproducible inspection methods, disclosure of relevant evidence, and attributable technical reporting.
- **Maintenance Lifecycle and Work-Order Governance**: Maintenance requirements distinguish physical task completion from formal acceptance and financial closeout.
- **Cost Estimation and Engineering Change Control**: Repair estimates and changes preserve a reviewable baseline and require independent Customer approval before additional work.
- **Artificial Intelligence Governance**: AI defect suggestions, summaries, and maintenance guidance remain advisory, grounded in relevant source information, and subject to human review.
- **Civil Aviation Responsibilities**: Airspace and permit records support planning and readiness review but do not grant flight authorization or replace applicable pilot qualifications and approvals.
