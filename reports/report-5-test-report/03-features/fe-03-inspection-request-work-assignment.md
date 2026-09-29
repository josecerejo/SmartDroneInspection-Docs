# FE-03: Inspection Request and Work Assignment

## Scope baseline

WF2 unifies PERIODIC and AD_HOC requests. Client request details and Service Manager review lead to a versioned quotation and service-order confirmation. The Client approves post-service payment terms before assignment; no upfront payment or online payment gateway is required.

## Current acceptance cases

These four cases map to FE-03 and WF2. WF2-001 and WF2-002 were in workbook Function B; WF2-003 and WF2-004 were in Function C.

| Test Case ID | Test Case Description | Test Case Procedure | Expected Results | Pre-conditions | Round 1 | Test date | Tester | Round 2 | Test date | Tester | Round 3 | Test date | Tester | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WF2-001 | Client creates an ad-hoc inspection request. | Sign in as Client; select an owned asset; enter scope, location, and preferred timing; submit. | Request is accepted with an auditable creator and organization; invalid scope is rejected. | Owned asset exists; client is active. | Pending |  |  | Pending |  |  | Pending |  |  |  |
| WF2-002 | Service Manager prepares and sends a quotation. | Sign in as Service Manager; open the request; add price, scope, and validity; save a version; send it. | A versioned quotation is stored and visible to the correct client; prior versions remain traceable. | Request is actionable; manager is active. | Pending |  |  | Pending |  |  | Pending |  |  |  |
| WF2-003 | Client approves a quotation and confirms the service order. | Sign in as Client; review the latest quotation; approve it; open the order and billing status. | The approved quotation becomes the confirmed order; the first service billing milestone is recorded. | Quotation is in an approvable state; client owns the request. | Pending |  |  | Pending |  |  | Pending |  |  |  |
| WF2-004 | Service Manager assigns an Inspector with assignment scope. | Sign in as Service Manager; assign an active Inspector; open the task as the Inspector; attempt an unrelated task. | Assigned Inspector can access only the assigned task; unassigned or conflicting access is denied. | Confirmed order exists; candidate Inspector is active. | Pending |  |  | Pending |  |  | Pending |  |  |  |




## WF1 schedule-proposal revision (2026-09-28)

The 2026-09-28 WF1 revision adds the due-cycle event, document-upload rules, and the negative scope sweep. These three cases map to FE-03 and WF1 on the `Feature 1` workbook sheet. `WF1-017` is a **producer-side** verification: it asserts event identity, payload, and per-cycle idempotency with an in-process listener standing in for the WF2 consumer. The consumer half (one `PERIODIC` request per replayed event) is pending T021.

| Test Case ID | Test Case Description | Test Case Procedure | Expected Results | Pre-conditions | Round 1 | Test date | Tester | Round 2 | Test date | Tester | Round 3 | Test date | Tester | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WF1-017 | The due-cycle publisher emits one event per cycle. | Force `next_due_at` into the past; run the publisher twice; inspect the published events. | Exactly one `InspectionScheduleDue` event carries the correct organization, asset, checklist template, and due cycle; a replayed run publishes nothing. | An `ACTIVE` schedule has `next_due_at` in the past. | Passed | 2026-09-28 | Hiếu | Passed | 2026-09-28 | Hiếu | Passed | 2026-09-28 | Hiếu | Automated evidence: `PeriodicRequestHandoffTest.publishesExactlyOneEventPerDueScheduleCycleAndReplayIsSilent`; `AssetWorkflowIntegrationTest.fullWf1FlowFromAssetCreationToDueEvent`. |
| WF1-018 | Asset document upload is validated and scoped. | Upload a png/jpeg/webp/pdf within 10 MB to an active asset; upload an unsupported type, an oversize file, and a document to a pending asset; list and stream as another organization. | Only supported types within the size limit reach storage; unsupported types and oversize files are rejected; a pending asset rejects upload; another organization cannot list or stream the document. | An active asset exists; type and size fixtures are available. | Passed | 2026-09-28 | Hiếu | Passed | 2026-09-28 | Hiếu | Passed | 2026-09-28 | Hiếu | Automated evidence: `AssetDocumentApiIntegrationTest.activeAssetDocumentUploadsAndListsForOwnOrgOnly`; `unsupportedTypeOversizeAndPendingAssetsAreRejected`; `returnsAssetOnlyForItsOrganization`. |
| WF1-019 | Negative scope sweep across every WF1 endpoint. | Exercise each WF1 endpoint across two organizations and the five roles, including unauthenticated access. | Role and organization scope are enforced on every endpoint; a Service Manager cannot create assets or manage the catalog; a Client cannot review assets; unauthenticated access returns a Problem Details 401. | Two organizations and the five role fixtures exist. | Passed | 2026-09-28 | Hiếu | Passed | 2026-09-28 | Hiếu | Passed | 2026-09-28 | Hiếu | Automated evidence: `AssetWorkflowIntegrationTest.negativeScopeSweepAcrossEveryWf1Endpoint`; `managerReviewQueueIsPlatformScopedAndClosedToOtherRoles`. |

## Coverage boundary

WF1-004 verifies periodic request generation, while WF2-001 verifies ad-hoc request creation. The current cases do not explicitly record one end-to-end periodic-request-to-quotation path.
