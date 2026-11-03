---
title: "Report 4 - Detailed Design"
document_type: report4-sdd-section
weight: 35
source: "report4-software-design-document.docx"
---

## 3. Detailed Design

### 3.1 FE-01 Customer Registration, Sign-In and Account Access

#### 3.1.1 Class Diagram

```mermaid
%% title: FE-01 Customer Registration, Sign-In and Account Access Class Diagram
classDiagram
  class BrowserAuthController {
    +register(req) ApiResponse
    +sendRegistrationOtp(req) ApiResponse
    +login(req) ApiResponse
    +verifyLoginOtp(req) ApiResponse
    +sendPasswordResetOtp(req) ApiResponse
    +confirmPasswordReset(req) ApiResponse
    +refresh() ApiResponse
  }
  class OAuth2Controller {
    +authorizeGoogle(clientType) void
    +googleCallback(code, state) void
  }
  class UserProfileController {
    +getMe() CurrentUserResponse
    +updateProfile(req) CurrentUserResponse
    +updatePilotLicense(req) CurrentUserResponse
  }
  class AuthService {
    +registerCustomer(req) RegistrationResult
    +login(email, password) LoginResult
    +loginWithGoogle(profile) LoginResult
  }
  class User {
    -UUID id
    -UUID organizationId
    -String email
    -String fullName
    -UserStatus status
    -ActorZone actorZone
    -String roles
  }
  class OtpChallenge {
    -UUID id
    -OtpChallengePurpose purpose
    -UUID userId
    -String destination
    -Instant expiresAt
    -Instant consumedAt
  }
  class ProspectiveCustomerRegistration {
    -UUID id
    -UUID userId
    -String organizationName
    -String assetName
    -BigDecimal latitude
    -BigDecimal longitude
    -String airspaceClassification
    -String status
  }
  BrowserAuthController --> AuthService
  BrowserAuthController --> OtpChallenge
  OAuth2Controller --> AuthService
  UserProfileController --> AuthService
  AuthService --> User
  AuthService --> ProspectiveCustomerRegistration
```

**Class Specifications**

| No | Class | Description |
| :---: | :--- | :--- |
| 01 | `BrowserAuthController` & `MobileAuthController` | Handle customer registration, email and password sign-in, one-time verification code delivery and confirmation, password reset, and session token refresh for web and mobile clients. |
| 02 | `OAuth2Controller` | Handles federated Google OAuth 2.0 sign-in and callback redirection for web browsers and mobile deep links. |
| 03 | `UserProfileController` | Allows signed-in users to view and update their personal account profile, change their password, and maintain pilot license details. |
| 04 | `AuthService` | Coordinates credential verification, account lockout after repeated failed attempts, airspace screening during customer onboarding, and JWT session issuance. |
| 05 | `User` & `OtpChallenge` | Domain entities representing user accounts across the five system roles and time-limited verification challenges for sign-in, registration, and password reset. |
| 06 | `ProspectiveCustomerRegistration` | Domain entity recording a customer organization and initial asset registration request along with its airspace classification result. |

#### 3.1.2 Customer Registration and User Sign-In Sequence Diagram

```mermaid
%% title: FE-01 Customer Registration and User Sign-In Sequence Diagram
sequenceDiagram
  autonumber
  actor User as Customer or User
  participant App as Client Application
  participant Auth as Authentication Service
  participant Airspace as Airspace Screening Service
  participant DB as Database

  User->>App: Submit organization and initial asset registration
  App->>Auth: Request customer registration with asset coordinates
  Auth->>Airspace: Evaluate asset location against airspace zones
  alt Prohibited No-Fly Zone
    Airspace-->>Auth: Prohibited zone detected
    Auth-->>App: Reject registration with airspace reason
  else Restricted or Clear Zone
    Airspace-->>Auth: Eligible or pending review
    Auth->>DB: Save organization, customer account, and registration record
    Auth-->>App: Confirm registration status
  end

  User->>App: Sign in with email and password (or Google OAuth 2.0)
  App->>Auth: Submit sign-in credentials
  Auth->>DB: Verify account status and create login verification challenge
  Auth-->>App: Prompt for one-time verification code
  User->>App: Enter one-time verification code
  App->>Auth: Verify code and complete sign-in
  Auth->>DB: Mark code consumed and create active session
  Auth-->>App: Return access token and role workspace
```

---

### 3.2 FE-02 Partner Qualification, Workforce, Assets and Drone Registration

#### 3.2.1 Class Diagram

```mermaid
%% title: FE-02 Partner Qualification, Workforce, Assets and Drone Registration Class Diagram
classDiagram
  class PlatformUserController {
    +listUsers(page, size, query) PagedResponse
    +createUser(req) ApiResponse
    +updateRoles(userId, req) ApiResponse
    +updateStatus(userId, req) ApiResponse
  }
  class InspectorProfileController {
    +listInspectors() List~InspectorProfileResponse~
    +updateProfile(userId, req) InspectorProfileResponse
    +uploadLicenseScan(userId, file) InspectorProfileResponse
    +recordFlightLog(userId, req) InspectorFlightLogResponse
  }
  class WorkforceController {
    +createWorkforceUser(req) ApiResponse
    +listWorkforceUsers(page, size, query) PagedResponse
  }
  class AssetController {
    +createAsset(req) ApiResponse
    +listAssets(page, size, query) PagedResponse
    +updateAsset(assetId, req) AssetView
    +retireAsset(assetId) AssetView
  }
  class DroneRegistrationApplicationController {
    +uploadEvidence(docType, file) UploadedKeyResponse
    +submit(req) ApiResponse
    +listPending() List~DroneRegistrationResponse~
    +approve(appId, req) DroneRegistrationResponse
    +reject(appId, req) DroneRegistrationResponse
  }
  class InspectorProfile {
    -UUID userId
    -String pilotLicenseNumber
    -String pilotLicenseClass
    -Instant pilotLicenseExpiresAt
    -BigDecimal priorFlightHours
  }
  class DroneRegistrationApplication {
    -UUID id
    -UUID inspectorUserId
    -String serialNumber
    -String registrationFileKey
    -String ownershipFileKey
    -String inspectionFileKey
    -String status
  }
  class Drone {
    -UUID id
    -UUID inspectorOwnerId
    -String serialNumber
    -String model
    -DroneServiceability serviceability
  }
  class Asset {
    -UUID id
    -UUID organizationId
    -String assetCode
    -String name
    -BigDecimal latitude
    -BigDecimal longitude
    -AssetStatus status
  }
  PlatformUserController --> InspectorProfile
  InspectorProfileController --> InspectorProfile
  DroneRegistrationApplicationController --> DroneRegistrationApplication
  DroneRegistrationApplication --> Drone
  AssetController --> Asset
```

**Class Specifications**

| No | Class | Description |
| :---: | :--- | :--- |
| 01 | `PlatformUserController` & `InspectorProfileController` | Allow platform administrators and managers to provision Inspector accounts, maintain pilot license credentials, upload license scans, and record flight logs. |
| 02 | `WorkforceController` | Allows a Customer organization manager to provision and manage Maintenance Engineer accounts within that customer organization. |
| 03 | `AssetController` & `AssetDocumentController` | Manage customer infrastructure assets, structural inspection checkpoints, and engineering reference documents, blocking asset creation inside prohibited No-Fly Zones. |
| 04 | `DroneRegistrationApplicationController` | Handles Inspector drone registration submissions with three required documents (registration, ownership, and technical inspection) and platform review decisions. |
| 05 | `InspectorProfile`, `Drone` & `Asset` | Domain entities representing Inspector qualifications, approved Inspector-owned drones, and customer infrastructure assets. |

#### 3.2.2 Partner Provisioning and Customer Workforce Sequence Diagram

```mermaid
%% title: FE-02 Inspector Provisioning and Customer Workforce Sequence Diagram
sequenceDiagram
  autonumber
  actor Admin as Admin or Manager
  actor Cust as Customer
  actor Insp as Inspector
  participant UserSvc as Account & Profile Service
  participant DB as Database

  Admin->>UserSvc: Provision Inspector account
  UserSvc->>DB: Create Inspector account and qualification profile
  DB-->>Admin: Confirm provisioned Inspector account

  Admin->>UserSvc: Record pilot license details and upload license scan
  UserSvc->>DB: Update Inspector profile and license expiration date
  Insp->>UserSvc: View own profile and flight log history
  UserSvc->>DB: Load Inspector profile and flight logs

  Cust->>UserSvc: Create Maintenance Engineer account for organization
  UserSvc->>DB: Save Maintenance Engineer scoped to Customer organization
  DB-->>Cust: Confirm Maintenance Engineer account ready
```

#### 3.2.3 Inspector-Owned Drone Registration Sequence Diagram

```mermaid
%% title: FE-02 Inspector-Owned Drone Registration and Review Sequence Diagram
sequenceDiagram
  autonumber
  actor Insp as Inspector
  actor Admin as Admin or Manager
  participant DroneSvc as Drone Registration Service
  participant Storage as Object Storage (MinIO)
  participant DB as Database

  Insp->>DroneSvc: Upload registration, ownership, and inspection documents
  DroneSvc->>Storage: Store three supporting document files
  Storage-->>DroneSvc: Return stored document keys

  Insp->>DroneSvc: Submit drone registration application (serial number, model, documents)
  DroneSvc->>DB: Verify unique serial number and save pending application
  DB-->>Insp: Confirm application submitted for review

  Admin->>DroneSvc: Review uploaded documents and approve application
  DroneSvc->>DB: Create active Drone owned by Inspector and mark application approved
  DB-->>Admin: Confirm drone registered and eligible for dispatch
```

#### 3.2.4 WF-01 Onboarding, Asset and Drone Registry Activity Diagram

```mermaid
%% title: WF-01 Activity Diagram - Onboarding, Asset and Drone Registry
flowchart TD
  subgraph CU1["Customer"]
    A1(["Start: Submit Organization & Initial Asset Registration"])
    A5["Register Infrastructure Assets & Inspection Checkpoints"]
    A6["Provision Maintenance Engineer Accounts"]
  end

  subgraph IN1["Inspector"]
    A7["Maintain Pilot License Credentials & Flight History"]
    A9["Submit Owned Drone Registration with Three Supporting Documents"]
  end

  subgraph ADM1["Admin or Manager"]
    A3["Review Restricted-Airspace Customer Registration"]
    A8["Provision Inspector Account & Verify Credentials"]
    A10["Review Three Drone Documents & Approve Drone"]
  end

  subgraph SYS1["Automated Airspace Check"]
    A2{"Screen Initial Asset\nAirspace Zone"}
    A4["Reject Registration (Prohibited No-Fly Zone)"]
    A11(["End: Customer Assets & Partner Drones Ready for Inspection Requests"])
  end

  A1 --> A2
  A2 -->|"Prohibited Zone"| A4
  A2 -->|"Restricted Zone"| A3 --> A5
  A2 -->|"Clear Zone"| A5 --> A6 --> A11
  A7 --> A8 --> A9 --> A10 --> A11
```

---

### 3.3 FE-03 Recurring Service Requests, Occurrences and Notifications

#### 3.3.1 Class Diagram

```mermaid
%% title: FE-03 Recurring Occurrences and Notification Inbox Class Diagram
classDiagram
  class NotificationController {
    +listNotifications(page, size, unreadOnly) PagedResponse
    +getUnreadCount() UnreadCountResponse
    +markRead(notificationId) NotificationItemResponse
  }
  class NotificationService {
    +createInAppNotification(orgId, userId, type, title, body, key) void
    +markAsRead(orgId, userId, notificationId) Notification
  }
  class InspectionNotificationListener {
    +onInspectionAssigned(event) void
    +onFieldSessionAborted(event) void
  }
  class MaintenanceNotificationListener {
    +onWorkOrderAssigned(event) void
    +onEstimateApproved(event) void
    +onAcceptanceRecorded(event) void
    +onWorkOrderClosed(event) void
  }
  class Notification {
    -UUID id
    -UUID organizationId
    -UUID recipientUserId
    -String eventType
    -String title
    -NotificationStatus status
    -String deduplicationKey
  }
  NotificationController --> NotificationService
  InspectionNotificationListener --> NotificationService
  MaintenanceNotificationListener --> NotificationService
  NotificationService --> Notification
```

**Class Specifications**

| No | Class | Description |
| :---: | :--- | :--- |
| 01 | `ContractWorkflowService` | Expands accepted one-time and recurring service requests into individual inspection occurrences based on the agreed recurrence interval and schedule window. |
| 02 | `NotificationController` & `NotificationService` | Provide the in-app notification inbox, unread notification counter, and read-status updates for signed-in users. |
| 03 | `InspectionNotificationListener` & `MaintenanceNotificationListener` | Consume transactional domain events (such as mission assignment, aborted field sessions, estimate approval, and work order closure) to create deduplicated in-app notifications. |
| 04 | `Notification` | Domain entity representing a user notification scoped by organization and deduplication key. |

#### 3.3.2 Recurring Occurrences and Notification Sequence Diagram

```mermaid
%% title: FE-03 Recurring Occurrences and Notification Sequence Diagram
sequenceDiagram
  autonumber
  actor User as Customer or User
  participant ContractSvc as Contract Service
  participant NotifSvc as Notification Service
  participant DB as Database

  User->>ContractSvc: Accept quotation for recurring service request
  ContractSvc->>DB: Generate planned inspection occurrences
  ContractSvc->>NotifSvc: Publish domain event for request update
  NotifSvc->>DB: Save deduplicated in-app notification

  User->>NotifSvc: Open notification inbox
  NotifSvc->>DB: Query user notifications and unread count
  DB-->>User: Return notification list and unread count

  User->>NotifSvc: Mark notification as read
  NotifSvc->>DB: Update notification read status
```

---

### 3.4 FE-04 Service Requests, Quotations, Contracts, Dispatch and Airspace Map

#### 3.4.1 Class Diagram

```mermaid
%% title: FE-04 Service Request, Quotation, Signed Contract and Dispatch Class Diagram
classDiagram
  class ContractWorkflowController {
    +list() List~ServiceRequestResponse~
    +create(req) ServiceRequestResponse
    +postMessage(reqId, msg) ServiceRequestResponse
    +issueQuote(reqId, quoteReq) ServiceRequestResponse
    +acceptQuote(reqId, versionNo) ServiceRequestResponse
    +uploadSignedContract(reqId, file) ServiceRequestResponse
    +downloadSignedContract(reqId) InputStreamResource
    +assignOccurrence(reqId, occId, assignReq) ServiceRequestResponse
  }
  class ContractWorkflowService {
    +create(actorId, req) ServiceRequestResponse
    +issueQuote(actorId, reqId, quoteReq) ServiceRequestResponse
    +acceptQuote(actorId, reqId, versionNo) ServiceRequestResponse
    +uploadSignedContract(actorId, reqId, file) ServiceRequestResponse
    +assignOccurrence(actorId, reqId, occId, assignReq) ServiceRequestResponse
  }
  class Mf2InspectionAssignmentAdapter {
    +assignPartnerInspection(command) UUID
  }
  class ServiceRequest {
    -UUID id
    -UUID organizationId
    -UUID assetId
    -RequestType requestType
    -ServiceRequestStatus status
    -Integer acceptedQuoteVersion
    -String contractObjectKey
  }
  class ServiceRequestQuote {
    -UUID id
    -UUID requestId
    -int versionNo
    -UUID inspectorId
    -UUID droneId
    -BigDecimal pricePerOccurrenceVnd
  }
  class ServiceRequestOccurrence {
    -UUID id
    -UUID requestId
    -UUID inspectionId
    -OccurrenceStatus status
    -OccurrencePaymentStatus paymentStatus
    -Long payosOrderCode
  }
  ContractWorkflowController --> ContractWorkflowService
  ContractWorkflowService --> ServiceRequest
  ContractWorkflowService --> ServiceRequestQuote
  ContractWorkflowService --> ServiceRequestOccurrence
  ContractWorkflowService --> Mf2InspectionAssignmentAdapter
```

**Class Specifications**

| No | Class | Description |
| :---: | :--- | :--- |
| 01 | `ContractWorkflowController` & `ContractWorkflowService` | Manage customer inspection service requests, order chat messages, versioned VND quotations, quote acceptance, signed paper agreement uploads, and occurrence dispatch. |
| 02 | `Mf2InspectionAssignmentAdapter` | Validates Inspector pilot license status, drone ownership, and schedule availability across customer organizations before creating a scheduled inspection mission. |
| 03 | `ServiceRequest`, `ServiceRequestQuote` & `ServiceRequestOccurrence` | Domain entities representing the customer request, each proposed VND quotation version, and the individual inspection occurrences generated upon quote acceptance. |

#### 3.4.2 Service Request, Quotation, Signed Contract and Dispatch Sequence Diagram

```mermaid
%% title: FE-04 Service Request, Quotation, Signed Contract and Dispatch Sequence Diagram
sequenceDiagram
  autonumber
  actor Cust as Customer
  actor Mgr as Manager
  participant ContractSvc as Contract Service
  participant DB as Database

  Cust->>ContractSvc: Submit one-time or recurring service request
  ContractSvc->>DB: Save open service request

  Mgr->>ContractSvc: Select Inspector and drone, then issue VND quotation
  ContractSvc->>DB: Save quotation version and update request status

  Cust->>ContractSvc: Exchange order chat messages and accept quotation
  ContractSvc->>DB: Create inspection occurrences and record accepted quote

  Mgr->>ContractSvc: Upload signed offline service agreement scan
  ContractSvc->>DB: Store agreement file and mark contract signed

  Mgr->>ContractSvc: Assign Inspector and drone to occurrence
  ContractSvc->>DB: Verify license and schedule availability, then create scheduled Inspection
```

#### 3.4.3 WF-02 Service Request, Quotation, Contract and Dispatch Activity Diagram

```mermaid
%% title: WF-02 Activity Diagram - Service Request, Quotation, Signed Contract and Dispatch
flowchart TD
  subgraph CU2["Customer"]
    B1(["Start: Create Service Request (One-Time or Recurring)"])
    B4{"Review Quotation"}
    B5["Discuss Adjustments in Order Chat"]
    B6["Accept Quotation Version (Occurrences Created)"]
  end

  subgraph MG2["Manager"]
    B2["Select Qualified Inspector & Owned Drone"]
    B3["Issue VND Quotation"]
    B7["Upload Signed Paper Service Agreement Scan"]
    B8["Assign Inspector & Drone to Occurrence"]
  end

  subgraph SYS2["Automated Dispatch Check"]
    B9{"Verify License Validity &\nSchedule Availability"}
    B10["Create Scheduled Inspection Mission & Link to Occurrence"]
    B11(["End: Notify Assigned Inspector for Field Execution"])
  end

  B1 --> B2 --> B3 --> B4
  B4 -->|"Request Change"| B5 --> B2
  B4 -->|"Accept"| B6 --> B7 --> B8 --> B9
  B9 -->|"Schedule Conflict"| B2
  B9 -->|"Eligible"| B10 --> B11
```

---

### 3.5 FE-05 Flight Permit Gate and Field Inspection Execution

#### 3.5.1 Class Diagram

```mermaid
%% title: FE-05 Flight Permit Gate and Field Inspection Execution Class Diagram
classDiagram
  class InspectionController {
    +uploadFlightPermit(inspId, file) InspectionResponse
    +openFlightPermit(inspId) ResponseEntity
    +reschedule(inspId, req) InspectionResponse
    +reassign(inspId, req) InspectionResponse
    +cancel(inspId, req) InspectionResponse
  }
  class InspectionFieldSessionController {
    +listSessions(inspId) List~FieldSessionResponse~
    +start(inspId, req) FieldSessionResponse
    +complete(inspId, sessId, req) FieldSessionResponse
    +abort(inspId, sessId, req) FieldSessionResponse
  }
  class InspectionCreationService {
    +uploadFlightPermit(actorId, inspId, file) Inspection
    +reschedule(actorId, inspId, startAt, endAt) Inspection
    +reassign(actorId, inspId, inspectorId, droneId) Inspection
    +cancel(actorId, inspId, reason) Inspection
  }
  class InspectionFieldSessionService {
    +start(actorId, inspId, safetyNote) FieldSession
    +complete(actorId, inspId, sessId, notes) FieldSession
    +abort(actorId, inspId, sessId, reason) FieldSession
  }
  class Inspection {
    -UUID id
    -UUID organizationId
    -UUID assetId
    -UUID inspectorId
    -UUID droneId
    -InspectionStatus status
    -String flightPermitFileKey
    +hasFlightPermit() boolean
    +moveTo(nextStatus) void
    +reopenAfterSessionAbort() void
  }
  class FieldSession {
    -UUID id
    -UUID inspectionId
    -FieldSessionStatus status
    -Instant startedAt
    -Instant endedAt
    -String preFlightChecklistNote
    -String outcomeNotes
    -String abortReason
    +start(startedAt) void
    +complete(endedAt, notes) void
    +abort(endedAt, reason) void
  }
  InspectionController --> InspectionCreationService
  InspectionFieldSessionController --> InspectionFieldSessionService
  InspectionCreationService --> Inspection
  InspectionFieldSessionService --> Inspection
  InspectionFieldSessionService --> FieldSession
  Inspection "1" *-- "1..*" FieldSession : executes
```

**Class Specifications**

| No | Class | Description |
| :---: | :--- | :--- |
| 01 | `InspectionController` & `InspectionCreationService` | Handle mission flight permit uploads and provide Manager recovery actions (reschedule, reassign, or cancel) when an on-site field session is aborted. |
| 02 | `InspectionFieldSessionController` & `InspectionFieldSessionService` | Govern on-site field session execution, enforcing that a session can start only when the inspection is scheduled with a flight permit on file, and recording either normal completion or session abort. |
| 03 | `Inspection` | Aggregate root representing an inspection mission, its assigned Inspector and drone, flight permit reference, and six-state mission status. |
| 04 | `FieldSession` | Domain entity recording the start time, pre-flight safety note, end time, completion outcome notes, or abort reason of an on-site flight survey. |

#### 3.5.2 Flight Permit and Field Inspection Execution Sequence Diagram

```mermaid
%% title: FE-05 Flight Permit and Field Inspection Execution Sequence Diagram
sequenceDiagram
  autonumber
  actor Insp as Inspector
  actor Mgr as Manager
  participant Svc as Inspection Service
  participant DB as Database

  Insp->>Svc: Upload flight permit document
  Svc->>DB: Save flight permit and verify mission readiness

  Insp->>Svc: Start field session with pre-flight safety note
  Svc->>DB: Create active field session and mark mission in progress

  alt Field Session Aborted (Weather or Safety Issue)
    Insp->>Svc: Abort field session with reason
    Svc->>DB: Record aborted session and return mission to scheduled state
    Svc-->>Mgr: Notify Manager of aborted field session
    Mgr->>Svc: Reschedule, reassign, or cancel inspection
    Svc->>DB: Update inspection schedule or assignment
  else Field Session Completed Normally
    Insp->>Svc: Complete field session with outcome notes
    Svc->>DB: Record completed session and mark field work completed
    Svc-->>Insp: Confirm completion and unlock Evidence upload
  end
```

---

### 3.6 FE-06 Evidence Intake, AI Defect Detection, Inspection Report and Payment

#### 3.6.1 Defect Detection and Finding Confirmation Class Diagram

```mermaid
%% title: FE-06 Evidence Intake, AI Defect Detection and Finding Confirmation Class Diagram
classDiagram
  class EvidenceService {
    +upload(actorId, inspId, file) EvidenceResponse
    +listForInspection(actorId, inspId) EvidencePageResponse
    +openContent(actorId, inspId, evidId) EvidenceContent
    +retire(actorId, inspId, evidId) void
  }
  class FindingService {
    +analyzeEvidence(actorId, inspId, evidId) List~FindingResponse~
    +createManual(actorId, inspId, req) FindingResponse
    +review(actorId, inspId, findingId, decision) FindingResponse
    +confirmFindings(actorId, inspId, ack) void
  }
  class AiInferencePort {
    +predict(imageBytes, contentType) List~DetectedBox~
  }
  class YoloInferenceClient {
    +predict(imageBytes, contentType) List~DetectedBox~
  }
  class Evidence {
    -UUID id
    -UUID inspectionId
    -UUID fieldSessionId
    -String fileName
    -String contentType
    -String objectKey
    -BigDecimal latitude
    -BigDecimal longitude
    -boolean isDeleted
  }
  class Finding {
    -UUID id
    -UUID inspectionId
    -UUID evidenceId
    -String findingCode
    -String defectLabel
    -FindingSeverity severity
    -String boundingBox
    -FindingStatus status
    -BigDecimal confidence
  }
  EvidenceService --> Evidence
  FindingService --> Finding
  FindingService --> AiInferencePort
  YoloInferenceClient --|> AiInferencePort
  Evidence "1" o-- "0..*" Finding : locates
```

#### 3.6.2 Defect Detection and Finding Confirmation Sequence Diagram

```mermaid
%% title: FE-06 Defect Detection and Finding Confirmation Sequence Diagram
sequenceDiagram
  autonumber
  actor Insp as Inspector
  participant Svc as Evidence & Finding Service
  participant AI as YOLO11 & Vision AI
  participant DB as Database

  Insp->>Svc: Upload field photographs and MP4 videos
  Svc->>DB: Store media file and save Evidence metadata (GPS and capture time)

  Insp->>Svc: Request AI defect analysis on photograph
  Svc->>AI: Run YOLO11 detection (with Vision AI fallback if needed)
  AI-->>Svc: Return candidate bounding boxes, defect labels, and confidence scores
  Svc->>DB: Save pending candidate Findings
  Svc-->>Insp: Display candidate defects on photograph

  Insp->>Svc: Review candidates (confirm, edit severity, or remove)
  Svc->>DB: Save Inspector-confirmed Findings

  Insp->>Svc: Confirm official Findings baseline
  Svc->>DB: Verify zero pending candidates and lock Findings baseline
```

#### 3.6.3 Inspection Report, Publication and Online Payment Class Diagram

```mermaid
%% title: FE-06 Inspection Report, Publication and Online Payment Class Diagram
classDiagram
  class ReportService {
    +compileSubmittedReport(actorId, inspId) InspectionReportResponse
    +generateAiSummary(actorId, inspId, locale) ReportAiSummaryResponse
    +reviewVersion(actorId, inspId, verId, approve, reason) InspectionReportResponse
    +publishVersion(actorId, inspId, verId) ReportPublishedResponse
  }
  class PayOSPaymentService {
    +acceptPublishedReport(custId, inspId) OccurrenceResponse
    +createPaymentLink(custId, inspId) PayOSCheckoutResponse
    +handleWebhook(payload, signature) void
    +recordPayout(adminId, occId) OccurrenceResponse
  }
  class InspectionReport {
    -UUID id
    -UUID inspectionId
    -int versionNo
    -ReportStatus status
    -UUID reviewerUserId
    -String returnReason
    -Instant submittedAt
    -Instant publishedAt
    +submit() void
    +reviewBy(reviewerId, approve, reason) void
    +publish(publisherId, authorId) void
  }
  ReportService --> InspectionReport
  PayOSPaymentService --> InspectionReport
```

**Class Specifications**

| No | Class | Description |
| :---: | :--- | :--- |
| 01 | `EvidenceService` | Uploads, streams, and retires field photographs and MP4 videos associated with an inspection session. |
| 02 | `FindingService` & `YoloInferenceClient` | Invoke YOLO11 and Vision fallback defect detection on inspection photographs, manage manual and AI-suggested findings, and lock the confirmed findings baseline. |
| 03 | `ReportService` & `InspectionReport` | Compile structured inspection reports from confirmed findings, generate AI executive summaries, enforce independent Manager review, and publish official report versions. |
| 04 | `PayOSPaymentService` | Records Customer report acceptance, generates PayOS VietQR and VNPay online payment links in VND, verifies payment webhook callbacks, and updates customer payment and partner payout statuses. |

#### 3.6.4 Report Compilation, Publication and Payment Sequence Diagram

```mermaid
%% title: FE-06 Report Compilation, Publication and Online Payment Sequence Diagram
sequenceDiagram
  autonumber
  actor Insp as Inspector
  actor Mgr as Manager
  actor Cust as Customer
  participant Svc as Report & Payment Service
  participant Ext as AI & Payment Gateway
  participant DB as Database

  Insp->>Svc: Generate AI executive summary and submit Inspection Report
  Svc->>DB: Save submitted Inspection Report and mark mission under review

  alt Manager Returns Report for Revision
    Mgr->>Svc: Return report with revision feedback
    Svc->>DB: Record returned status and return mission to field-completed state
  else Manager Approves and Publishes Report
    Mgr->>Svc: Approve and publish official report
    Svc->>DB: Record published status and complete inspection
  end

  Cust->>Svc: Review published report and click Accept Report
  Svc->>DB: Mark occurrence payment due
  Cust->>Svc: Initiate online payment (PayOS VietQR or VNPay)
  Svc->>Ext: Create signed payment order and return checkout link
  Ext-->>Svc: Send verified payment confirmation webhook
  Svc->>DB: Record occurrence paid status and partner payout settlement
```

#### 3.6.5 WF-03 Inspection, Reporting and Payment Activity Diagram

```mermaid
%% title: WF-03 Activity Diagram - Field Session, AI Detection, Reporting and Payment
flowchart TD
  subgraph IN3["Inspector"]
    C1(["Start: Upload Mission Flight Permit"])
    C2["Start Field Session with Pre-Flight Safety Note"]
    C3{"Field Session Outcome"}
    C4["Abort Session with Reason"]
    C5["Complete Session & Upload Photograph and Video Evidence"]
    C6["Run AI Defect Detection & Confirm Findings Baseline"]
    C7["Compile & Submit Inspection Report"]
  end

  subgraph MG3["Manager"]
    C4M["Reschedule, Reassign, or Cancel Aborted Mission"]
    C8{"Review Submitted Report"}
    C9["Return Report with Feedback"]
    C10["Approve & Publish Official Report"]
  end

  subgraph CU3["Customer"]
    C11["Review Published Report & Executive Summary"]
    C12["Accept Report & Complete Online Payment (PayOS or VNPay)"]
    C13(["End: Obtain Report Copy & Initiate Maintenance if Needed"])
  end

  C1 --> C2 --> C3
  C3 -->|"Aborted"| C4 --> C4M --> C2
  C3 -->|"Completed"| C5 --> C6 --> C7 --> C8
  C8 -->|"Returned"| C9 --> C6
  C8 -->|"Published"| C10 --> C11 --> C12 --> C13
```

---

### 3.7 FE-07 Maintenance Work Orders, Repair Planning and Field Execution

#### 3.7.1 Class Diagram

```mermaid
%% title: FE-07 Maintenance Work Order, RAG Planning and Repair Execution Class Diagram
classDiagram
  class MaintenanceController {
    +suggestScope(req) SuggestScopeResponse
    +suggestEstimate(workOrderId) SuggestEstimateResponse
    +createWorkOrder(req) ApiResponse
    +assignTeam(workOrderId, req) List~TeamMemberView~
    +createTask(workOrderId, req) ApiResponse
    +createEstimateVersion(workOrderId, req) ApiResponse
    +submitEstimateVersion(workOrderId, verNo) EstimateVersionView
    +approveEstimateVersion(workOrderId, verNo) EstimateVersionView
  }
  class MaintenanceExecutionController {
    +releaseWorkOrder(workOrderId) WorkOrderView
    +startWorkOrder(workOrderId) WorkOrderView
    +createWorkLog(workOrderId, req) ApiResponse
    +submitWorkLog(workOrderId, logId) WorkLogView
    +batchVerifyWorkLogs(workOrderId) List~WorkLogView~
    +declareComplete(workOrderId) WorkOrderView
  }
  class MaintenanceScopeAdvisorService {
    +suggestScope(actorId, req) SuggestScopeResponse
    +suggestEstimate(actorId, workOrderId) SuggestEstimateResponse
  }
  class MaintenanceWorkOrder {
    -UUID id
    -UUID organizationId
    -UUID assetId
    -UUID sourceFindingId
    -WorkOrderStatus status
    -UUID budgetApproverUserId
    -UUID teamLeadUserId
    -UUID reportAuthorUserId
    -UUID acceptingReviewerUserId
  }
  MaintenanceController --> MaintenanceScopeAdvisorService
  MaintenanceController --> MaintenanceWorkOrder
  MaintenanceExecutionController --> MaintenanceWorkOrder
```

**Class Specifications**

| No | Class | Description |
| :---: | :--- | :--- |
| 01 | `MaintenanceController` | Manages corrective maintenance work order creation from confirmed defects, repair team allocation, task breakdown, and cost estimate submission and approval. |
| 02 | `MaintenanceScopeAdvisorService` | Queries engineering repair standards stored in the vector database to suggest repair scopes, initial repair tasks, and standard construction cost norms. |
| 03 | `MaintenanceExecutionController` | Governs field repair execution, change order requests, engineer work log submission, Team Lead batch verification, and work completion declaration. |
| 04 | `MaintenanceWorkOrder` | Aggregate root tracking the twelve-state maintenance lifecycle and enforcing separation of duties between the executing engineers and the Customer reviewers. |

#### 3.7.2 Work Order Planning, Cost Estimation and Repair Execution Sequence Diagram

```mermaid
%% title: FE-07 Work Order Planning, Cost Estimation and Repair Execution Sequence Diagram
sequenceDiagram
  autonumber
  actor Cust as Customer
  actor Lead as Maintenance Engineer (Team Lead)
  participant MaintSvc as Maintenance Service
  participant Advisor as RAG Scope & Cost Advisor
  participant DB as Database

  Cust->>MaintSvc: Request advisory repair scope for confirmed defect
  MaintSvc->>Advisor: Search engineering standards in vector store
  Advisor-->>Cust: Return recommended repair scope and initial tasks

  Cust->>MaintSvc: Create Work Order with initial tasks and assign repair team
  MaintSvc->>DB: Save draft Work Order and initial repair tasks

  Lead->>MaintSvc: Generate cost norm suggestions and submit cost estimate
  MaintSvc->>DB: Save Estimate Version and submit for Customer approval

  Cust->>MaintSvc: Review and approve cost estimate
  MaintSvc->>DB: Mark Estimate Version and Work Order approved

  Lead->>MaintSvc: Release and start Work Order, then submit field work logs
  Lead->>MaintSvc: Batch-verify submitted work logs and declare repair complete
  MaintSvc->>DB: Verify all logs approved and mark repair work completed
```

---

### 3.8 FE-08 Maintenance Completion Report, Re-inspection Verification and Closure

#### 3.8.1 Class Diagram

```mermaid
%% title: FE-08 Completion Report, Re-inspection Verification and Cost Closure Class Diagram
classDiagram
  class MaintenanceExecutionController {
    +getAutoDraftReport(workOrderId) AutoDraftReportResponse
    +getAcceptanceCompliance(workOrderId) AcceptanceComplianceResponse
    +recordAcceptanceDecision(workOrderId, req) ApiResponse
    +reconcileCosts(workOrderId, req) CostReconciliationView
    +closeWorkOrder(workOrderId) WorkOrderView
  }
  class ReinspectionVerificationService {
    +getVerifications(actorId, reinspId) List~ReinspectionVerificationResponse~
    +updateVerification(actorId, reinspId, verId, req) ReinspectionVerificationResponse
  }
  class InspectionReinspectionListener {
    +onReinspectionRequested(event) void
  }
  class WorkOrderReinspectionListener {
    +onReinspectionCreated(event) void
    +onReinspectionReportPublished(event) void
  }
  class ReinspectionDefectVerification {
    -UUID id
    -UUID reinspectionId
    -UUID sourceFindingId
    -UUID newEvidenceId
    -String repairProofUrl
    -String repairEngineerNotes
    -String resolutionStatus
    -String inspectorNotes
  }
  MaintenanceExecutionController --> WorkOrderReinspectionListener
  ReinspectionVerificationService --> ReinspectionDefectVerification
  InspectionReinspectionListener --> ReinspectionDefectVerification
```

**Class Specifications**

| No | Class | Description |
| :---: | :--- | :--- |
| 01 | `MaintenanceExecutionController` | Supports auto-drafting the maintenance completion report, running the acceptance compliance check, recording the Customer acceptance decision, reconciling actual costs, and closing the work order. |
| 02 | `ReinspectionVerificationService` & `ReinspectionDefectVerification` | Manage three-way defect verification during a drone re-inspection mission, comparing the original defect, the engineer repair proof, and the newly captured drone evidence. |
| 03 | `InspectionReinspectionListener` & `WorkOrderReinspectionListener` | Coordinate the event-driven re-inspection loop between the maintenance module and the inspection module when a Customer requests drone re-inspection. |

#### 3.8.2 Completion Report, Three-Way Re-inspection and Closure Sequence Diagram

```mermaid
%% title: FE-08 Completion Report, Three-Way Re-inspection and Closure Sequence Diagram
sequenceDiagram
  autonumber
  actor Author as Maintenance Engineer (Report Author)
  actor Cust as Customer (Accepting Reviewer)
  actor Insp as Inspector
  actor Mgr as Manager
  participant MaintSvc as Maintenance Service
  participant InspSvc as Inspection Service
  participant DB as Database

  Author->>MaintSvc: Auto-draft and submit Maintenance Completion Report
  MaintSvc->>DB: Save completion report and submit Work Order for acceptance

  Cust->>MaintSvc: Review compliance summary and request Drone Re-inspection
  MaintSvc->>InspSvc: Publish re-inspection request event
  InspSvc->>DB: Create linked Re-inspection Mission and 3-way verification records

  Insp->>InspSvc: Capture new drone evidence and record 3-way verification result
  Insp->>InspSvc: Submit Re-inspection Report
  Mgr->>InspSvc: Review and publish Re-inspection Report
  InspSvc->>MaintSvc: Attach published re-inspection report to Work Order

  Cust->>MaintSvc: Review re-inspection result and accept completed repair
  MaintSvc->>DB: Mark Work Order accepted
  Cust->>MaintSvc: Reconcile actual costs and close Work Order
  MaintSvc->>DB: Save final cost lines and close Work Order
```

#### 3.8.3 WF-04 Maintenance, Re-inspection and Closure Activity Diagram

```mermaid
%% title: WF-04 Activity Diagram - Maintenance Work Order, Re-inspection and Closure
flowchart TD
  subgraph CU4["Customer"]
    D1(["Start: Create Work Order from Confirmed Defect"])
    D4{"Review Cost Estimate"}
    D5["Approve Cost Estimate"]
    D9["Review Completion Report & Compliance Check"]
    D10{"Acceptance Decision"}
    D11["Request Drone Re-inspection"]
    D15["Accept Repair, Reconcile Actual Costs & Close Work Order"]
    D16(["End: Closed Work Order with Complete Audit Trail"])
  end

  subgraph ME4["Maintenance Engineer Team"]
    D2["Prepare Cost Estimate Using Standard Norms"]
    D6["Execute Repair Tasks, Record Work Logs & Batch Verify"]
    D8["Compile & Submit Maintenance Completion Report"]
  end

  subgraph RI4["Inspector & Manager"]
    D12["Dispatch Linked Re-inspection Mission"]
    D13["Compare Original Defect, Repair Proof & New Drone Evidence"]
    D14["Publish Re-inspection Report & Return to Customer Review"]
  end

  D1 --> D2 --> D4
  D4 -->|"Reject"| D2
  D4 -->|"Approve"| D5 --> D6 --> D8 --> D9 --> D10
  D10 -->|"Rework Required"| D6
  D10 -->|"Re-inspection Required"| D11 --> D12 --> D13 --> D14 --> D9
  D10 -->|"Accepted"| D15 --> D16
```
