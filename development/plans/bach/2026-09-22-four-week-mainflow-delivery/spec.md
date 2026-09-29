# Feature Specification: Four-Week Main-Flow Delivery

**Feature Branch**: `docs/four-week-mainflow-jira`
**Created**: 2026-09-22
**Status**: Planning baseline
**Input**: Deliver all four SmartDroneInspection main flows in four weeks with four members, one flow owner each, and a Jira-importable task breakdown.

> **Amended 2026-09-25: schedule proposals.** WF1 no longer lets a Client create an
> inspection schedule directly. A Client registers an asset in `PENDING_REVIEW`, the Service
> Manager approves it, the platform generates one schedule proposal per Admin-configured
> suggested frequency, the Manager reviews the proposals, and the Client selects exactly one to
> create the active schedule. See [the WF1 schedule-proposal spec](../hieu/2026-09-25-wf1-schedule-proposal-flow/spec.md).


## User Scenarios & Testing

### User Story 1 - Register assets and schedule inspections (Priority: P1)

A Client registers an asset in their organization, attaches a document, and activates a periodic
inspection schedule based on an Admin-managed category and checklist. When due, the system creates
one periodic request for that cycle.

**Independent Test**: Use an active Client and seeded Admin catalog. Create an asset and due
schedule, trigger the due cycle twice, and observe one request. The handoff can be checked without
completing WF2.

**Acceptance Scenarios**:

1. Given a valid category and checklist, when the Client creates an asset and schedule, then both
   are visible only to that organization.
2. Given a due active schedule, when due processing is retried, then exactly one periodic request
   exists for the asset, schedule, and due cycle.
3. Given an inactive asset or unavailable checklist, when due processing runs, then it does not
   create an executable request and exposes a recoverable review state.

### User Story 2 - Convert a request into accepted field work (Priority: P1)

A Client submits an ad hoc or periodic request. A Service Manager reviews it, prepares a versioned
quotation and order, and assigns an Inspector after Client approval. The Inspector accepts or
rejects; a rejection returns the work for reassignment.

**Independent Test**: Start with a seeded authorized asset or a WF1 periodic request and finish
with a confirmed order and accepted assignment. No inspection execution is required to verify WF2.

**Acceptance Scenarios**:

1. Given a submitted request, when the Service Manager quotes it and the Client approves the
   current version, then the order can be confirmed and an Inspector can be assigned.
2. Given a request for quotation revision, when the manager submits a new version, then earlier
   versions remain visible and cannot be silently overwritten.
3. Given a rejected assignment with a reason, when the manager reassigns it and another Inspector
   accepts, then the job becomes ready for inspection.

### User Story 3 - Inspect, verify findings, and deliver a report (Priority: P1)

The assigned Inspector performs the inspection, completes the checklist, uploads evidence, reviews
candidate findings or adds findings manually, and submits a report. A different Inspector performs
technical peer review. The Service Manager releases the approved report and the Client accepts it
or requests a revision.

**Independent Test**: Start from a seeded accepted WF2 assignment, complete an inspection and
report, and verify author/reviewer separation, customer visibility, and immutable acceptance.

**Acceptance Scenarios**:

1. Given an accepted assignment, when the Inspector uploads valid evidence and completes the
   checklist, then only that Inspector can change the inspection record.
2. Given an AI candidate or manual observation, when the Inspector confirms, modifies, rejects,
   or adds a finding, then only verified findings appear in official report content.
3. Given a submitted report, when its author attempts peer approval, then the action is denied.
4. Given technical approval and manager release, when the Client accepts, then the accepted report
   version cannot be edited; a correction creates a new version.

### User Story 4 - Assess, execute, and resolve maintenance (Priority: P1)

A Client creates a ticket from a verified finding in an accepted report. A Maintenance Engineer
assesses the work, the Service Manager prepares a quotation, the Client approves it, and an assigned
Engineer executes the work. The Service Manager releases the result; the Client accepts, requests
rework, or requests a linked re-inspection.

**Independent Test**: Start from a seeded accepted report and finding. Complete one ticket and
verify its linked history, evidence, authorization, and resolution decision without running WF1–WF3.

**Acceptance Scenarios**:

1. Given an accepted report, when the Client selects its verified finding, then a ticket is created
   in the same organization and cannot be created from a different organization's finding.
2. Given an accepted assessment assignment, when the Engineer submits an estimate, then the manager
   can quote it; execution cannot start before the Client approves the order.
3. Given a material change, when the Engineer requests additional scope, then that work remains
   blocked until the Client approves a new order version.
4. Given completed work with before/after evidence, when the Client accepts, then the ticket closes
   and a post-service invoice status is recorded. Rework and re-inspection take their documented paths.

### Edge Cases

- Duplicate due-cycle processing, duplicate evidence, and repeated acceptance requests do not
  create duplicate business records.
- An inactive or unassigned user cannot execute an assignment.
- Unavailable AI does not discard evidence or prevent manual finding review.
- Customer users never see internal report drafts or peer-review comments.
- A rejected quotation, assignment, or change request retains its history and permits the next
  authorized action.
- A re-inspection decision creates a linked ad hoc request for WF2 without closing the traceability
  chain.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST support the WF1–WF4 paths and role responsibilities in the current
  Report 3 and business-flow reference.
- **FR-002**: Every Client action MUST be scoped to its organization; every Inspector and
  Maintenance Engineer action MUST be scoped to an accepted assignment or authorized peer review.
- **FR-003**: The system MUST preserve quotation, order, report, and approval versions and decisions.
- **FR-004**: The system MUST expose one unambiguous handoff at each flow boundary: due request,
  accepted Inspector assignment, accepted report, and linked re-inspection request.
- **FR-005**: The system MUST support manual finding entry when AI is unavailable; AI output MUST
  remain a candidate until Inspector verification.
- **FR-006**: Inspection and maintenance MUST each record a separate post-service billing milestone
  and invoice/payment status. The release does not process online payments.
- **FR-007**: Browser workflows MUST cover Client, Service Manager, and Admin actions; mobile MUST
  cover focused assigned Inspector and Maintenance Engineer actions.
- **FR-008**: Every flow MUST have automated tests for its main path and critical authorization,
  versioning, and retry boundaries, plus a cross-flow demonstration.

### Key Entities

- **Asset, Checklist Template, Schedule**: WF1-owned customer asset and periodic planning records.
- **Inspection Request, Quotation, Service Order, Assignment**: WF2-owned commercial and staffing
  records.
- **Inspection, Evidence, Candidate, Verified Finding, Report Version, Peer Review**: WF3-owned
  execution and report records.
- **Maintenance Ticket, Assessment, Order, Assignment, Work Log, Change Request**: WF4-owned work
  and resolution records.
- **Invoice**: Post-service payment-status record associated with the accepted inspection or
  maintenance milestone.

## Success Criteria

### Measurable Outcomes

- **SC-001**: By the end of Week 4, a five-role demonstration completes all four flows from an
  organization asset to an accepted maintenance result in one environment.
- **SC-002**: Each flow can be demonstrated independently from a documented input fixture and
  produces the next flow's documented output.
- **SC-003**: All 14 critical acceptance scenarios above pass in automated or explicitly recorded
  manual verification; cross-organization and unassigned access attempts are denied.
- **SC-004**: Retrying due-cycle generation, evidence upload, and final decisions produces no
  duplicate request, evidence, or invoice record in the demonstration.
- **SC-005**: The Week 4 demo shows both normal closure and one rework or re-inspection branch,
  with the linked history visible to authorized users.

## Assumptions

- Four members work approximately 20 development days each over four consecutive Jira weeks
  beginning 2026-09-28 (Jira Week 3 after the current Week 2 sprint). One member owns each flow
  across backend, web, focused mobile work, tests, and docs.
- The existing authentication runtime, database migrations V1–V9, and feature-owned entities and
  repositories are reused after verification. They are a starting point, not proof that flows work.
- The four-flow goal covers the main path and named critical branches above. Extensive dashboard
  analytics, email delivery, AI model training, drone control, online payment, and advanced offline
  mobile operation are outside this four-week release.
- Uploaded evidence is available through the existing authorized file store. AI inference depends
  on a configured service; manual findings keep the business flow usable when it is unavailable.
- Jira assignee account IDs are not known from the repository. The import file identifies an owner
  slot per flow through labels; a Jira administrator maps those slots to real accounts after import.
