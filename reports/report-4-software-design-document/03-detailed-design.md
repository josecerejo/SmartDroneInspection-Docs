---
title: "Report 4 - Detailed Design"
document_type: report4-sdd-section
weight: 35
source: "report4-software-design-document.docx"
---

## 3. Detailed Design

### 3.1 FE-01 Authentication, Google OAuth2 & 5-Role Access Control

#### 3.1.1 Class Diagram

```mermaid
%% title: Identity, OAuth2 and 5-Role Access Control Class Diagram
classDiagram
  class BrowserAuthController {
    +csrf(CsrfToken) Map
    +register(OrganizationRegistrationRequest) ResponseEntity~ApiResponse~
    +login(LoginRequest, HttpServletRequest, HttpServletResponse) ResponseEntity~ApiResponse~
    +setupInitialPassword(InitialPasswordSetupRequest) ResponseEntity~ApiResponse~
    +refresh(HttpServletRequest, HttpServletResponse) ResponseEntity~ApiResponse~
  }
  class OAuth2Controller {
    +authorizeGoogle(String, HttpServletResponse) void
    +googleCallback(String, String, String, HttpServletRequest, HttpServletResponse) void
  }
  class UserProfileController {
    +getMe(Jwt) ApiResponse~CurrentUserResponse~
    +updateProfile(Jwt, UpdateUserProfileRequest) ApiResponse~CurrentUserResponse~
    +updatePilotLicense(Jwt, UpdatePilotLicenseRequest) ApiResponse~CurrentUserResponse~
  }
  class PlatformUserController {
    +listUsers(int, int, String) ApiResponse~PagedResponse~
    +createUser(Jwt, CreatePlatformUserRequest) ResponseEntity~ApiResponse~
    +updateRoles(Jwt, UUID, UpdatePlatformUserRolesRequest) ApiResponse
    +updateStatus(Jwt, UUID, UpdateUserStatusRequest) ApiResponse
  }
  class AuthService {
    +registerCustomerWithFirstAsset(OrganizationRegistrationRequest) RegistrationResult
    +login(String, String, String, String) LoginResult
    +loginWithGoogle(GoogleUserProfile, ClientType, String, String) LoginResult
  }
  class User {
    -UUID id
    -UUID organizationId
    -String normalizedEmail
    -UserStatus status
    -ActorZone actorZone
    -String roles
    -String pilotLicenseNumber
    -Instant pilotLicenseExpiresAt
  }
  class ProspectiveCustomerRegistration {
    -UUID id
    -UUID userId
    -String organizationCode
    -String assetCode
    -BigDecimal latitude
    -BigDecimal longitude
    -String airspaceClassification
    -String status
  }
  BrowserAuthController --> AuthService
  OAuth2Controller --> AuthService
  UserProfileController --> User
  PlatformUserController --> User
  AuthService --> User
  AuthService --> ProspectiveCustomerRegistration
```

**Class Specifications**

- **BrowserAuthController, MobileAuthController & OAuth2Controller**: Expose web (`/api/v1/auth`), native mobile (`/api/v1/mobile/auth`), and Google OAuth 2.0 (`/api/v1/auth/oauth2/authorize/google`, `/callback/google` with `smartdrone://auth` mobile deep-link redirect) authentication endpoints, enforcing `AuthRateLimitFilter` (`10` req/60s per IP), Argon2id password verification, `HS256` JWT issuance (`15m` TTL), and `HmacSHA256` refresh session rotation (`auth_sessions`, `7d` TTL).
- **UserProfileController & PlatformUserController**: Decouple self-service profile and pilot license updates (`/api/v1/users/me`) from authentication routes (`7cc2534`), and govern 5-role accounts (`ADMIN`, `MANAGER`, `CUSTOMER`, `INSPECTOR`, `MAINTENANCE_ENGINEER`) across `ActorZone` boundaries (`PLATFORM`, `CUSTOMER_ORGANIZATION`, `INSPECTOR_PARTNER`, `PROSPECT_CUSTOMER`).

#### 3.1.2 User Authentication, Google OAuth2 & Airspace Registration Sequence Diagram

```mermaid
%% title: User Authentication, Google OAuth2 and Airspace Registration Sequence Diagram
sequenceDiagram
  autonumber
  actor User as Customer / System User
  participant Client as Web Portal / Flutter Mobile
  participant AuthCtrl as BrowserAuthController / OAuth2Controller
  participant AuthSvc as AuthService
  participant Airspace as CustomerAirspacePolicyAdapter
  participant DB as PostgreSQL (users, organizations, auth_sessions)

  User->>Client: Submit Customer & First Asset Registration (lat, lng)
  Client->>AuthCtrl: POST /api/v1/auth/register (OrganizationRegistrationRequest)
  AuthCtrl->>AuthSvc: register(request)
  AuthSvc->>Airspace: evaluateAirspace(latitude, longitude)
  alt NO_FLY_ZONE (Decision 18/2020/QD-TTg)
    Airspace-->>AuthSvc: NO_FLY_ZONE
    AuthSvc-->>Client: 403 Forbidden (ASSET_IN_NO_FLY_ZONE)
  else CLEAR_ZONE
    Airspace-->>AuthSvc: CLEAR_ZONE
    AuthSvc->>DB: insertOrganization + insertActiveCustomerUser + emitCustomerRegistrationEvent(firstAsset)
    AuthSvc-->>Client: 201 Created
  end

  User->>Client: Sign In via Email/Password or Google OAuth2
  Client->>AuthCtrl: POST /api/v1/auth/login (or GET /api/v1/auth/oauth2/authorize/google)
  AuthCtrl->>AuthSvc: verifyCredentialsOrGoogleCode()
  AuthSvc->>DB: verifyStatusAndLockout & insertAuthSession(HmacSHA256, 7d TTL)
  AuthSvc-->>Client: 200 OK (HS256 JWT AccessToken + Refresh Token / smartdrone://auth)
```

---

### 3.2 FE-02 Partner Onboarding, Workforce, Asset & Inspector Drone Registry

#### 3.2.1 Class Diagram

```mermaid
%% title: Partner Onboarding, Asset Registry and Inspector-Owned Drone Class Diagram
classDiagram
  class InspectorPartnerApplicationController {
    +listPending(Jwt) ApiResponse~List~
    +downloadLicenseDocument(Jwt, UUID) ResponseEntity~InputStreamResource~
    +approve(Jwt, UUID, ApprovePartnerRequest) ApiResponse~PartnerApplicationResponse~
    +reject(Jwt, UUID, RejectApplicationRequest) ApiResponse~PartnerApplicationResponse~
  }
  class AirspaceReviewController {
    +listPending(Jwt) ApiResponse~List~
    +approve(Jwt, UUID, ReviewNoteRequest) ApiResponse
    +reject(Jwt, UUID, ReviewNoteRequest) ApiResponse
  }
  class WorkforceController {
    +createWorkforceUser(Jwt, CreateWorkforceUserRequest) ResponseEntity~ApiResponse~
    +listWorkforceUsers(Jwt, int, int, String) ApiResponse~PagedResponse~
  }
  class AssetController {
    +createAsset(Jwt, CreateAssetRequest) ResponseEntity~ApiResponse~
    +listAssets(Jwt, int, int, String) ApiResponse~PagedResponse~
    +updateAsset(Jwt, UUID, UpdateAssetRequest) ApiResponse~AssetView~
    +retireAsset(Jwt, UUID) ApiResponse~AssetView~
  }
  class DroneRegistrationApplicationController {
    +uploadEvidence(Jwt, String, MultipartFile) ApiResponse~UploadedKeyResponse~
    +submit(Jwt, CreateDroneRegistrationRequest) ResponseEntity~ApiResponse~
    +listMine(Jwt) ApiResponse~List~
    +listPending(Jwt) ApiResponse~List~
    +approve(Jwt, UUID, ReviewNoteRequest) ApiResponse~DroneRegistrationResponse~
    +reject(Jwt, UUID, ReviewNoteRequest) ApiResponse~DroneRegistrationResponse~
  }
  class InspectorPartnerApplication {
    -UUID id
    -String normalizedEmail
    -String pilotLicenseNumber
    -String pilotLicenseFileKey
    -String partnerContractFileKey
    -String status
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
    -UUID organizationId
    -String serialNumber
    -DroneServiceability serviceability
  }
  class Asset {
    -UUID id
    -UUID organizationId
    -String assetCode
    -BigDecimal latitude
    -BigDecimal longitude
    -AssetStatus status
  }
  InspectorPartnerApplicationController --> InspectorPartnerApplication
  DroneRegistrationApplicationController --> DroneRegistrationApplication
  DroneRegistrationApplication --> Drone
  AssetController --> Asset
```

**Class Specifications**

- **InspectorPartnerApplicationController, AirspaceReviewController & WorkforceController**: Govern `MF1` onboarding review queues (`/admin/onboarding-reviews`) for restricted-airspace customers and partner Inspectors (requiring `partnerContractFileKey` proof of the executed offline partner contract), and allow `CUSTOMER` users to provision `MAINTENANCE_ENGINEER` accounts.
- **AssetController, AssetDocumentController & DroneRegistrationApplicationController**: Manage customer infrastructure assets (`assets`, `asset_documents`) with No-Fly Zone guards and platform-wide `ADMIN`/`MANAGER` read visibility (`92fb490`), and govern 3-document inspector-owned drone registrations (`REGISTRATION`, `OWNERSHIP`, `INSPECTION` $\rightarrow$ `drones.inspector_owner_id`).

#### 3.2.2 Partner Inspector Application & Customer Workforce Provisioning Sequence Diagram

```mermaid
%% title: Partner Inspector Onboarding and Customer Workforce Sequence Diagram
sequenceDiagram
  autonumber
  actor Admin as Platform Admin / Manager
  actor Cust as Customer (CUSTOMER)
  actor Insp as Partner Inspector (INSPECTOR)
  participant PartCtrl as InspectorPartnerApplicationController
  participant WfCtrl as WorkforceController
  participant ProfCtrl as UserProfileController
  participant DB as PostgreSQL (inspector_partner_applications, users)

  Admin->>PartCtrl: GET /api/v1/inspector-partner-applications/pending
  PartCtrl->>DB: findByStatus(PENDING)
  DB-->>Admin: Pending Partner Applications (pilotLicenseFileKey)
  Admin->>PartCtrl: POST /api/v1/inspector-partner-applications/{id}/approve (partnerContractFileKey)
  PartCtrl->>DB: markApplicationApproved & provisionPartnerInspectorUser(ActorZone.INSPECTOR_PARTNER, 0 drones required)
  DB-->>Admin: 200 OK (Approved Partner Inspector Account)

  Cust->>WfCtrl: POST /api/v1/workforce/users (role=MAINTENANCE_ENGINEER)
  WfCtrl->>DB: insertUser(orgId, ActorZone.CUSTOMER_ORGANIZATION, role=MAINTENANCE_ENGINEER)
  DB-->>Cust: 201 Created (WorkforceUserCreatedResponse)

  Insp->>ProfCtrl: PUT /api/v1/users/me/pilot-license (number, class, expiresAt, fileKey)
  ProfCtrl->>DB: updatePilotLicenseCredentials(inspectorUserId)
  DB-->>Insp: 200 OK (CurrentUserResponse)
```

#### 3.2.3 Inspector-Owned Drone 3-Document Registration & Review Sequence Diagram

```mermaid
%% title: Inspector-Owned Drone 3-Document Registration and Review Sequence Diagram
sequenceDiagram
  autonumber
  actor Insp as Partner Inspector (INSPECTOR)
  actor Admin as Platform Admin / Manager
  participant DroneAppCtrl as DroneRegistrationApplicationController
  participant MinIO as MinIO Object Storage
  participant DB as PostgreSQL (drone_registration_applications, drones)

  Insp->>DroneAppCtrl: POST /api/v1/drone-registration-applications/evidence?type=REGISTRATION|OWNERSHIP|INSPECTION
  DroneAppCtrl->>MinIO: putObject(drone-registration-applications/{inspectorId}/evidence/{type})
  MinIO-->>Insp: Uploaded Object Keys (registrationKey, ownershipKey, inspectionKey)

  Insp->>DroneAppCtrl: POST /api/v1/drone-registration-applications (serialNumber, model, 3 fileKeys)
  DroneAppCtrl->>DB: verifyUniquePendingSerial & insertApplication(status=PENDING)
  DB-->>Insp: 201 Created (DroneRegistrationResponse status=PENDING)

  Admin->>DroneAppCtrl: GET /api/v1/drone-registration-applications/{id}/evidence/{type}
  DroneAppCtrl->>MinIO: streamDocumentForReview()
  Admin->>DroneAppCtrl: POST /api/v1/drone-registration-applications/{id}/approve
  DroneAppCtrl->>DB: insertDrone(inspectorOwnerId, status=AVAILABLE, serviceability=ACTIVE) & markApproved(droneId)
  DB-->>Admin: 200 OK (Provisioned Partner Drone)
```

#### 3.2.4 WF-01 Activity Diagram — Customer Airspace & Partner Onboarding, Asset & Drone Registry

```mermaid
%% title: WF-01 Activity Diagram - Customer Airspace and Partner Onboarding, Asset and Drone Registry
flowchart TD
  subgraph CU1["Customer (CUSTOMER)"]
    A1(["Start: Submit Customer & First Asset Registration"])
    A5["Register Additional Assets (Checkpoints & SHA-256 Documents)"]
    A6["Provision Maintenance Engineer Workforce Accounts"]
  end

  subgraph IN1["Partner Inspector (INSPECTOR)"]
    A7["Verify Pilot License & Sign Offline Partner Contract (No Drone Required at Signup)"]
    A9["Submit Owned Drone Application + 3 Documents (Registration, Ownership, Inspection)"]
  end

  subgraph ADM1["Platform Admin / Manager (ADMIN / MANAGER)"]
    A3["Review Restricted-Zone Registration / Partner Application (partnerContractFileKey)"]
    A8["Approve Partner Inspector Account (ActorZone.INSPECTOR_PARTNER)"]
    A10["Verify 3 Drone Documents & Approve Inspector-Owned Drone (ACTIVE)"]
  end

  subgraph SYS1["Automated System (AirspaceAdvisoryService)"]
    A2{"Evaluate First Asset\nAirspace Zone?"}
    A4["Reject Registration (403 NO_FLY_ZONE)"]
    A11(["End: Customer Assets & Partner Inspector/Drone Pool Ready for MF2"])
  end

  A1 --> A2
  A2 -->|"NO_FLY_ZONE"| A4
  A2 -->|"RESTRICTED_ZONE"| A3 --> A5
  A2 -->|"CLEAR_ZONE"| A5 --> A6 --> A11
  A7 --> A8 --> A9 --> A10 --> A11
```

---

### 3.3 FE-03 Recurring Schedules, Contract Occurrences & Outbox Notifications

#### 3.3.1 Class Diagram

```mermaid
%% title: Notification Inbox and Event Listeners Class Diagram
classDiagram
  class NotificationController {
    +listNotifications(Jwt, int, int, boolean) ApiResponse~PagedResponse~
    +getUnreadCount(Jwt) ApiResponse~UnreadCountResponse~
    +markRead(Jwt, UUID) ApiResponse~NotificationItemResponse~
  }
  class NotificationService {
    +createInAppNotification(UUID orgId, UUID recipientId, String eventType, String title, String body, String targetPath, String deduplicationKey) void
    +markAsRead(UUID orgId, UUID recipientId, UUID notificationId) Notification
  }
  class InspectionNotificationListener {
    +onInspectionAssigned(InspectionAssignedEvent) void
    +onFieldSessionAborted(FieldSessionAbortedEvent) void
    +onInspectionReminderDue(InspectionReminderDueEvent) void
  }
  class MaintenanceNotificationListener {
    +onWorkOrderAssigned(WorkOrderAssignedEvent) void
    +onEstimateApproved(EstimateApprovedEvent) void
    +onAcceptanceRecorded(AcceptanceRecordedEvent) void
    +onWorkOrderClosed(WorkOrderClosedEvent) void
  }
  class Notification {
    -UUID id
    -UUID organizationId
    -UUID recipientUserId
    -NotificationStatus status
    -String deduplicationKey
    -String targetPath
  }
  NotificationController --> NotificationService
  InspectionNotificationListener --> NotificationService
  MaintenanceNotificationListener --> NotificationService
  NotificationService --> Notification
```

**Class Specifications**

- **InspectionScheduleController, RecurringInspectionScheduleService & ContractWorkflowService (Occurrences)**: Manage timezone-anchored recurring schedules (`recurring_inspection_schedules`, `schedule_occurrences`) and multi-occurrence contract cycles (`service_request_occurrences`) that automatically inherit the parent signed paper contract (Decision D2, `92fb490`).
- **NotificationController & InspectionNotificationListener / MaintenanceNotificationListener**: Persist deduplicated in-app notifications (`uq_notifications_deduplication_key`) via Spring Modulith's `event_publication` outbox, including urgent manager alerts when a field session is aborted (`FieldSessionAbortedEvent`, `3792889`).

#### 3.3.2 Event-Driven Transactional Outbox Notification Sequence Diagram

```mermaid
%% title: Event-Driven Transactional Outbox Notification Sequence Diagram
sequenceDiagram
  autonumber
  participant DomainSvc as Contract / Inspection / Maintenance Service
  participant Outbox as Spring Modulith Outbox (event_publication)
  participant Listener as InspectionNotificationListener
  participant NotifSvc as NotificationService
  participant DB as PostgreSQL (notifications)
  actor User as Recipient User (ADMIN / MANAGER / CUSTOMER / INSPECTOR / ENGINEER)

  DomainSvc->>Outbox: publishEvent(InspectionAssignedEvent / FieldSessionAbortedEvent / WorkOrderAssignedEvent)
  Outbox->>Listener: @ApplicationModuleListener invoke on transaction commit
  Listener->>NotifSvc: createInAppNotification(orgId, recipientId, deduplicationKey, targetPath)
  NotifSvc->>DB: insertIgnoreOnConflict(deduplication_key, status=SENT)
  DB-->>NotifSvc: Persisted Notification

  User->>DB: GET /api/v1/notifications & GET /api/v1/notifications/unread-count
  DB-->>User: Scoped Notifications + Unread Count
  User->>DB: PATCH /api/v1/notifications/{id}/read
  DB-->>User: 200 OK (status=READ, readAt=now)
```

---

### 3.4 FE-04 Service Requests, Quotations, Contracts, Dispatch & Airspace Map

#### 3.4.1 Class Diagram

```mermaid
%% title: Service Request, Quotation, Signed Contract and Partner Dispatch Class Diagram
classDiagram
  class ContractWorkflowController {
    +list(Jwt) ApiResponse~List~
    +create(Jwt, CreateServiceRequest) ApiResponse~ServiceRequestResponse~
    +postMessage(Jwt, UUID, PostServiceRequestMessage) ApiResponse~ServiceRequestResponse~
    +issueQuote(Jwt, UUID, IssueServiceQuoteRequest) ApiResponse~ServiceRequestResponse~
    +acceptQuote(Jwt, UUID, Integer) ApiResponse~ServiceRequestResponse~
    +uploadSignedContract(Jwt, UUID, MultipartFile) ApiResponse~ServiceRequestResponse~
    +downloadSignedContract(Jwt, UUID) ResponseEntity~InputStreamResource~
    +assignOccurrence(Jwt, UUID, UUID, AssignOccurrenceRequest) ApiResponse~ServiceRequestResponse~
  }
  class ContractWorkflowService {
    +create(UUID, CreateServiceRequest) ServiceRequestResponse
    +issueQuote(UUID, UUID, IssueServiceQuoteRequest) ServiceRequestResponse
    +acceptQuote(UUID, UUID, Integer) ServiceRequestResponse
    +uploadSignedContract(UUID, UUID, MultipartFile) ServiceRequestResponse
    +assignOccurrence(UUID, UUID, UUID, AssignOccurrenceRequest) ServiceRequestResponse
  }
  class Mf2InspectionAssignmentAdapter {
    +assignPartnerInspection(AssignCommand) UUID
  }
  class ServiceRequest {
    -UUID id
    -UUID organizationId
    -UUID assetId
    -RequestType requestType
    -ServiceRequestStatus status
    -Integer acceptedQuoteVersion
    -String contractObjectKey
    -String contractChecksumSha256
  }
  class ServiceRequestQuote {
    -UUID id
    -UUID requestId
    -int versionNo
    -UUID inspectorId
    -UUID droneId
    -String currency
    -BigDecimal pricePerOccurrenceVnd
    -BigDecimal pricePerOccurrenceUsd
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

- **ContractWorkflowController & ContractWorkflowService**: Implement the commercial `MF2` request-to-assignment vertical slice (`/api/v1/contracts/requests`), managing `ONE_TIME` and `RECURRING` service requests, in-context order chat (`service_request_messages` with author details), versioned `VND`/`USD` quotations, quote acceptance, and `SHA-256` signed paper contract storage (`PDF`, `DOCX`, `JPEG`, `PNG`).
- **Mf2InspectionAssignmentAdapter & InspectionCreationService**: Enforce partner Inspector license validity, inspector-owned drone ownership (`drone.inspectorOwnerId == inspectorId`), and cross-organization schedule conflict checks (`hasPlatformPartnerScheduleConflict`) before creating a `SCHEDULED` inspection mission, and expose manager dispatch endpoints (`PUT /schedule`, `PUT /assignment`, `POST /cancellation`) for aborted missions.

#### 3.4.2 Service Request Negotiation, Signed Contract & Cross-Org Partner Dispatch Sequence Diagram

```mermaid
%% title: Service Request Negotiation, Signed Contract and Cross-Org Partner Dispatch Sequence Diagram
sequenceDiagram
  autonumber
  actor Cust as Customer (CUSTOMER)
  actor Mgr as Platform Manager (MANAGER)
  participant Ctrl as ContractWorkflowController
  participant Svc as ContractWorkflowService
  participant Bridge as Mf2InspectionAssignmentAdapter
  participant MinIO as MinIO Object Storage
  participant DB as PostgreSQL (service_requests, quotes, occurrences, inspections)

  Cust->>Ctrl: POST /api/v1/contracts/requests (assetId, ONE_TIME/RECURRING, window)
  Ctrl->>Svc: create(customerId, request) -> status=OPEN
  Mgr->>Ctrl: POST /api/v1/contracts/requests/{id}/quotes (inspectorId, inspectorOwnedDroneId, VND/USD)
  Ctrl->>Svc: issueQuote() -> verifyDroneOwnedByInspector & saveQuote(versionNo) -> status=QUOTED
  Cust->>Ctrl: POST /api/v1/contracts/requests/{id}/messages (Order Chat negotiation)
  Cust->>Ctrl: POST /api/v1/contracts/requests/{id}/accept?versionNo={v}
  Ctrl->>Svc: acceptQuote() -> materializeOccurrences(PENDING_ASSIGNMENT) -> status=ACCEPTED

  Mgr->>Ctrl: POST /api/v1/contracts/requests/{id}/signed-contract (MultipartFile PDF/DOCX/Image)
  Ctrl->>Svc: uploadSignedContract()
  Svc->>MinIO: putObject(signedContractBytes, sha256)
  Svc->>DB: saveContractMetadata & inheritAcrossOccurrences() -> status=CONTRACT_SIGNED

  Mgr->>Ctrl: POST /api/v1/contracts/requests/{id}/occurrences/{occId}/assign
  Ctrl->>Svc: assignOccurrence(inspectorId, droneId, plannedStartAt, plannedEndAt)
  Svc->>Bridge: assignPartnerInspection()
  Bridge->>DB: verifyPilotLicense & verifyNoCrossOrgConflict(hasPlatformPartnerScheduleConflict)
  Bridge->>DB: insertInspection(status=SCHEDULED, partnerAssignment=true)
  Bridge-->>Svc: inspectionId -> Occurrence: ASSIGNED, ServiceRequest: ASSIGNED
```

#### 3.4.3 WF-02 Activity Diagram — Service Request, VND/USD Quote, Signed Contract & Cross-Org Partner Dispatch

```mermaid
%% title: WF-02 Activity Diagram - Service Request, Quote, Signed Contract and Partner Dispatch
flowchart TD
  subgraph CU2["Customer (CUSTOMER)"]
    B1(["Start: Create Service Request (ONE_TIME / RECURRING) -> OPEN"])
    B4{"Review Quote &\nNegotiate in Chat?"}
    B5["Post Message in Order Chat (service_request_messages)"]
    B6["Accept Latest Quote Version -> ACCEPTED (Occurrences Materialized)"]
  end

  subgraph MG2["Platform Manager (MANAGER)"]
    B2["Select Vetted Partner Inspector & Owned Drone (Check Availability)"]
    B3["Issue Versioned Quote (VND / USD) -> QUOTED"]
    B7["Sign Paper Contract Offline & Upload Scan (PDF/DOCX/JPEG/PNG + SHA-256) -> CONTRACT_SIGNED"]
    B8["Assign Partner Inspector & Owned Drone to Occurrence"]
  end

  subgraph SYS2["Automated System (Mf2InspectionAssignmentAdapter)"]
    B9{"License Valid & Cross-Org\nSchedule Conflict-Free?"}
    B10["Create Inspection (status=SCHEDULED, partnerAssignment=true) &\nLink Occurrence -> ASSIGNED"]
    B11(["End: Emit InspectionAssignedEvent -> Hand Off to MF3"])
  end

  B1 --> B2 --> B3 --> B4
  B4 -->|"Need Adjustment"| B5 --> B2
  B4 -->|"Agree"| B6 --> B7 --> B8 --> B9
  B9 -->|"Conflict / Expired"| B2
  B9 -->|"Valid"| B10 --> B11
```

---

### 3.5 FE-05 Flight Permit Gate, Field Execution, Dashboard & Calendar

#### 3.5.1 Class Diagram

```mermaid
%% title: Flight Permit Gate, Field Session and Abort Dispatch Class Diagram
classDiagram
  class InspectionFieldSessionController {
    +listSessions(Jwt, UUID) ApiResponse~List~
    +startSession(Jwt, UUID, StartFieldSessionRequest) ResponseEntity~ApiResponse~
    +completeSession(Jwt, UUID, UUID, EndFieldSessionRequest) ApiResponse~FieldSessionResponse~
    +abortSession(Jwt, UUID, UUID, AbortFieldSessionRequest) ApiResponse~FieldSessionResponse~
  }
  class InspectionController {
    +uploadFlightPermit(Jwt, UUID, MultipartFile) ApiResponse~InspectionResponse~
    +reschedule(Jwt, UUID, RescheduleInspectionRequest) ApiResponse~InspectionResponse~
    +reassign(Jwt, UUID, ReassignInspectionRequest) ApiResponse~InspectionResponse~
    +cancel(Jwt, UUID, CancelInspectionRequest) ApiResponse~InspectionResponse~
  }
  class FieldSession {
    -UUID id
    -UUID inspectionId
    -String status
    -String preFlightChecklistNote
    -String outcomeNotes
    -String abortReason
  }
  class Inspection {
    -UUID id
    -InspectionStatus status
    -String flightPermitFileKey
    +hasFlightPermit() boolean
    +startFieldSession() void
    +completeFieldSession() void
    +reopenAfterSessionAbort() void
  }
  class FieldSessionAbortedEvent {
    +UUID inspectionId
    +UUID sessionId
    +UUID inspectorId
    +String reason
  }
  InspectionFieldSessionController --> FieldSession
  InspectionFieldSessionController --> Inspection
  InspectionFieldSessionController --> FieldSessionAbortedEvent
  InspectionController --> Inspection
```

**Class Specifications**

- **InspectionController (Flight Permit & Manager Dispatch)**: Stores uploaded mission flight permits in MinIO (`flight_permit_file_key`) while keeping the mission in `SCHEDULED` (`V15`), and provides `MANAGER` recovery endpoints (`PUT /schedule`, `PUT /assignment`, `POST /cancellation`) when a field session is aborted (`3792889`).
- **InspectionFieldSessionController & Inspection**: Enforce the 2-outcome field session lifecycle (`Complete` $\rightarrow$ `FIELD_COMPLETED` or `Abort` $\rightarrow$ `ABORTED`, reverting `Inspection` to `SCHEDULED` and emitting `FieldSessionAbortedEvent`).

#### 3.5.2 Field Flight Session, Abort Dispatch & Evidence Upload Sequence Diagram

```mermaid
%% title: Field Flight Session, Abort Dispatch and Evidence Upload Sequence Diagram
sequenceDiagram
  autonumber
  actor Inspector as Assigned Partner Inspector
  actor Manager as Platform Manager (MANAGER)
  participant Mobile as Flutter Mobile / Web Client
  participant InspCtrl as InspectionController
  participant SessCtrl as InspectionFieldSessionController
  participant MinIO as MinIO Object Storage
  participant DB as PostgreSQL (inspections, field_sessions, evidence)

  Inspector->>Mobile: Upload Flight Permit (PDF/PNG/JPG)
  Mobile->>InspCtrl: POST /api/v1/inspections/{id}/flight-permit
  InspCtrl->>MinIO: putObject(permitObjectKey, bytes)
  InspCtrl->>DB: saveFlightPermitKey(hasFlightPermit() == true, status remains SCHEDULED)

  Inspector->>Mobile: Enter Pre-Flight Checklist Note & Start Field Session
  Mobile->>SessCtrl: POST /api/v1/inspections/{id}/field-sessions
  SessCtrl->>DB: verifyPermitAndLicense & insertSession(IN_PROGRESS) & updateInspection(IN_PROGRESS)

  alt Adverse Weather / Equipment Issue (Session Aborted)
    Inspector->>Mobile: Click Abort Session (abortReason)
    Mobile->>SessCtrl: POST /api/v1/inspections/{id}/field-sessions/{sId}/abort
    SessCtrl->>DB: markSessionAborted(ABORTED) & revertInspectionStatus(SCHEDULED)
    SessCtrl->>Manager: emit FieldSessionAbortedEvent (Urgent Notification)
    Manager->>InspCtrl: PUT /api/v1/inspections/{id}/schedule (or PUT /assignment / POST /cancellation)
  else Survey Completed Normally
    Inspector->>Mobile: Click Complete Session (outcomeNotes)
    Mobile->>SessCtrl: POST /api/v1/inspections/{id}/field-sessions/{sId}/completion
    SessCtrl->>DB: completeSession(FIELD_COMPLETED) & updateInspection(FIELD_COMPLETED)
    Inspector->>Mobile: Upload Photo / Streaming MP4 Video (file_picker)
    Mobile->>InspCtrl: POST /api/v1/inspections/{id}/evidence (MultipartFile)
    InspCtrl->>MinIO: putObject(objectKey, mediaStream)
    InspCtrl->>DB: insertEvidence(contentType, captureTime, latitude, longitude)
  end
```

---

### 3.6 FE-06 Evidence Intake, YOLO11 Detection, Auto-Compiled Report & PayOS

#### 3.6.1 YOLO11 Defect Detection & Finding Verification Class Diagram

```mermaid
%% title: YOLO11 Defect Detection and Finding Verification Class Diagram
classDiagram
  class InspectionController {
    +uploadEvidence(Jwt, UUID, MultipartFile, UUID, Instant, BigDecimal, BigDecimal) ApiResponse~EvidenceResponse~
    +analyzeEvidence(Jwt, UUID, UUID, boolean) ApiResponse~EvidenceAnalysisResponse~
    +createManualFinding(Jwt, UUID, ManualFindingRequest) ApiResponse~FindingResponse~
    +updateFinding(Jwt, UUID, UUID, UpdateFindingRequest) ApiResponse~FindingResponse~
    +confirmFinding(Jwt, UUID, UUID, ReviewFindingRequest) ApiResponse~FindingResponse~
    +deleteFinding(Jwt, UUID, UUID) ApiResponse~Void~
    +confirmFindings(Jwt, UUID, ConfirmFindingsRequest) ApiResponse~Void~
  }
  class PrimaryWithFallbackInference {
    +analyze(byte[] imageBytes, String contentType, boolean allowFallback) InferenceResult
  }
  class YoloInferenceClient {
    +predict(byte[] imageBytes, String contentType) List~DetectedBox~
  }
  class OpenAiCompatibleInferenceClient {
    +predict(byte[] imageBytes, String contentType) List~DetectedBox~
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
    -boolean isDeleted
  }
  InspectionController --> PrimaryWithFallbackInference
  PrimaryWithFallbackInference --> YoloInferenceClient
  PrimaryWithFallbackInference --> OpenAiCompatibleInferenceClient
  InspectionController --> Finding
```

#### 3.6.2 YOLO11 Defect Detection, Vision Fallback & Finding Confirmation Sequence Diagram

```mermaid
%% title: YOLO11 Defect Detection, Vision Fallback and Finding Confirmation Sequence Diagram
sequenceDiagram
  autonumber
  actor Inspector as Assigned Partner Inspector
  participant Client as Web Portal
  participant InspCtrl as InspectionController
  participant Infer as PrimaryWithFallbackInference
  participant YoloSvc as FastAPI YOLO11 (/predict)
  participant VisionLLM as Vision LLM Fallback
  participant DB as PostgreSQL (findings, inspections)

  Inspector->>Client: Select Evidence Image & Click AI Analyze
  Client->>InspCtrl: POST /api/v1/inspections/{id}/evidence/{evidenceId}/analyze
  InspCtrl->>Infer: analyze(imageBytes, contentType)
  Infer->>YoloSvc: POST /predict (multipart image)
  YoloSvc-->>Infer: YOLO Detections
  opt YOLO returns empty detections (ac50d56)
    Infer->>VisionLLM: analyzeImageWithVisionModel(imageBytes)
    VisionLLM-->>Infer: Fallback Candidate Detections
  end
  InspCtrl->>DB: insertFindings(status=PENDING, confidence, boundingBox)
  InspCtrl-->>Client: 200 OK (Pending Candidates Rendered on Capture)

  Inspector->>Client: Review Preview Chips, Edit Severity & Confirm Finding
  Client->>InspCtrl: POST /api/v1/inspections/{id}/findings/{findingId}/confirmation
  InspCtrl->>DB: confirmFinding() -> status=CONFIRMED

  Inspector->>Client: Confirm Official Findings Baseline
  Client->>InspCtrl: POST /api/v1/inspections/{id}/findings/confirm
  InspCtrl->>DB: ensureNoPendingCandidates & saveSnapshotHash(findingsConfirmedAt, status remains FIELD_COMPLETED)
  InspCtrl-->>Client: 200 OK
```

#### 3.6.3 Auto-Compiled Inspection Report, Review, PDF Publication & PayOS Class Diagram

```mermaid
%% title: Auto-Compiled Inspection Report, Review, PDF Publication and PayOS Class Diagram
classDiagram
  class InspectionController {
    +generateDraft(Jwt, UUID, HttpServletRequest) ApiResponse~InspectionReportResponse~
    +getAiSummary(Jwt, UUID, UUID, HttpServletRequest) ApiResponse~ReportAiSummaryResponse~
    +reviewVersion(Jwt, UUID, UUID, boolean, String) ApiResponse~InspectionReportResponse~
    +publishVersion(Jwt, UUID, UUID, HttpServletRequest) ApiResponse~ReportPublishedResponse~
    +acceptReport(Jwt, UUID, UUID) ApiResponse~Void~
    +createPayOSPaymentLink(Jwt, UUID) ApiResponse~PayOSCheckoutDetails~
    +getReportPaymentStatus(Jwt, UUID) ApiResponse~PaymentStatusDetails~
    +completeCorrectiveHandoff(Jwt, UUID, FindingHandoffRequest) ApiResponse~ReportPublishedResponse~
  }
  class ReportService {
    +generateDraft(UUID, UUID, Locale) InspectionReportResponse
    +getOrGenerateAiSummary(UUID, UUID, UUID, Locale) ReportAiSummaryResponse
    +reviewVersion(UUID, UUID, UUID, boolean, String) InspectionReportResponse
    +publish(UUID, UUID, UUID, Locale) ReportPublishedResponse
  }
  class PayOSPaymentGateway {
    +createPaymentLink(long orderCode, long amountVnd, String description) PayOSPaymentLink
    +verifyWebhookSignature(String payload, String signature) PayOSWebhookData
  }
  class PayOSWebhookController {
    +handleWebhook(Map) ResponseEntity~Map~
  }
  class InspectionReport {
    -UUID id
    -UUID inspectionId
    -int versionNo
    -ReportStatus status
    -UUID reviewerUserId
    -String artefactObjectKey
    -String artefactChecksumSha256
  }
  InspectionController --> ReportService
  ReportService --> InspectionReport
  InspectionController --> PayOSPaymentGateway
  PayOSWebhookController --> PayOSPaymentGateway
```

**Class Specifications**

- **ReportService & ReportDraftClient**: Auto-compile confirmed findings, evidence metadata, and field session records directly into a `SUBMITTED` `InspectionReport` (`V16`, `V17` — `DRAFT`, `AUTHOR_VERIFIED`, and `content_snapshot` eliminated), transition the mission to `UNDER_REVIEW`, generate the LLM Executive Summary (`ReportAiSummaryResponse`), enforce independent `MANAGER` review (`APPROVED` / `RETURNED`), and render the immutable `SHA-256` A4 PDF (`PUBLISHED`, moving the mission to `COMPLETED`).
- **ContractWorkflowService (InspectionReportAcceptancePort), PayOSPaymentGateway & PayOSWebhookController**: Transition occurrence `payment_status` to `PAYMENT_DUE` when the `CUSTOMER` accepts the published report, generate a VietQR checkout link (`/payos/create-payment-link`), verify HMAC-SHA256 webhook callbacks (`POST /api/v1/webhooks/payos`) to mark `payment_status = PAID` and `payout_status = ELIGIBLE`, and enforce the `402 Payment Required` download guard until paid.

#### 3.6.4 Report Auto-Compilation, Manager Publication & PayOS Settlement Sequence Diagram

```mermaid
%% title: Report Auto-Compilation, Manager Publication and PayOS Settlement Sequence Diagram
sequenceDiagram
  autonumber
  actor Inspector as Assigned Partner Inspector
  actor Manager as Platform Manager (MANAGER)
  actor Customer as Customer (CUSTOMER)
  participant Client as Web Portal
  participant InspCtrl as InspectionController
  participant PayOS as PayOS Gateway & Webhook
  participant MinIO as MinIO Object Storage
  participant DB as PostgreSQL (inspection_reports, inspections, occurrences)

  Inspector->>Client: Open Report Tab (InspectionDraftPage auto-triggers compilation)
  Client->>InspCtrl: POST /api/v1/inspections/{id}/report/draft
  InspCtrl->>DB: autoCompileFromConfirmedFindings() -> Report: SUBMITTED, Inspection: UNDER_REVIEW
  InspCtrl-->>Client: 200 OK (InspectionReportResponse status=SUBMITTED)

  Manager->>Client: View AI Summary (/ai-summary), Review & Publish Report
  Client->>InspCtrl: POST /api/v1/inspections/{id}/report/versions/{vId}/review?approve=true
  InspCtrl->>DB: reviewBy(managerId != inspectorId, approve=true) -> Report: APPROVED
  Client->>InspCtrl: POST /api/v1/inspections/{id}/report/versions/{vId}/publish
  InspCtrl->>MinIO: putObject(renderedPdfBytes, sha256)
  InspCtrl->>DB: publish() -> Report: PUBLISHED, Inspection: COMPLETED
  InspCtrl-->>Client: 200 OK (ReportPublishedResponse)

  Customer->>Client: Review Published Report & Click Accept Report
  Client->>InspCtrl: POST /api/v1/inspections/{id}/report/versions/{vId}/accept
  InspCtrl->>DB: markOccurrencePaymentDue(paymentStatus=PAYMENT_DUE)
  Customer->>Client: Click Proceed to VietQR Payment via PayOS
  Client->>InspCtrl: POST /api/v1/inspections/{id}/payos/create-payment-link
  InspCtrl->>PayOS: createPaymentLink(payosOrderCode, amountVnd)
  PayOS-->>Client: Redirect to checkoutUrl (VietQR)
  PayOS->>DB: POST /api/v1/webhooks/payos (HMAC-SHA256 verified) -> paymentStatus=PAID, payoutStatus=ELIGIBLE
  Customer->>InspCtrl: GET /api/v1/inspections/{id}/report/versions/{vId}/document (200 OK PDF Stream)
```

#### 3.6.5 WF-03 Activity Diagram — Flight Permit, Field Session, YOLO11, Auto-Compiled Report & PayOS Settlement

```mermaid
%% title: WF-03 Activity Diagram - Permit Gate, Field Session, YOLO11, Auto-Compiled Report and PayOS
flowchart TD
  subgraph IN3["Partner Inspector (INSPECTOR - Web / Mobile)"]
    C1(["Start: Receive SCHEDULED Inspection & Upload Flight Permit"])
    C2["Start FieldSession (Pre-Flight Note) -> IN_PROGRESS"]
    C3{"Session Outcome?"}
    C4["Abort Session (Reason) -> Inspection: SCHEDULED"]
    C5["Complete Session -> FIELD_COMPLETED & Upload Photo/MP4 Evidence"]
    C6["Run YOLO11 (+ Vision Fallback) & Confirm Findings Baseline"]
    C7["Visit Report Tab -> Auto-Compile & Submit Report (SUBMITTED, Inspection: UNDER_REVIEW)"]
  end

  subgraph MG3["Platform Manager (MANAGER)"]
    C4M["Reschedule / Reassign / Cancel Aborted Mission"]
    C8{"Review Submitted\nReport?"}
    C9["Return Report with Reason -> RETURNED (Inspection: FIELD_COMPLETED)"]
    C10["Approve (APPROVED) & Publish Immutable SHA-256 PDF -> PUBLISHED (Inspection: COMPLETED)"]
  end

  subgraph CU3["Customer (CUSTOMER) & PayOS VietQR"]
    C11["Track 5-Stage Progress -> Review Published Report & AI Executive Summary"]
    C12["Accept Report (PAYMENT_DUE) & Complete PayOS VietQR Checkout (PAID)"]
    C13(["End: Download Official PDF & Forward Defects to MF4 Maintenance"])
  end

  C1 --> C2 --> C3
  C3 -->|"Aborted"| C4 --> C4M --> C2
  C3 -->|"Completed"| C5 --> C6 --> C7 --> C8
  C8 -->|"Return"| C9 --> C6
  C8 -->|"Approve & Publish"| C10 --> C11 --> C12 --> C13
```

---

### 3.7 FE-07 Maintenance Work Orders, RAG Scope/Norms Advisor & Repair Execution

#### 3.7.1 Class Diagram

```mermaid
%% title: Maintenance Work Order, RAG Advisor and Cost Control Class Diagram
classDiagram
  class MaintenanceController {
    +suggestScope(Jwt, SuggestScopeRequest) ApiResponse~SuggestScopeResponse~
    +suggestEstimate(Jwt, UUID) ApiResponse~SuggestEstimateResponse~
    +createWorkOrder(Jwt, CreateWorkOrderRequest) ResponseEntity~ApiResponse~
    +assignTeam(Jwt, UUID, AssignTeamRequest) ApiResponse~List~
    +createTask(Jwt, UUID, CreateMaintenanceTaskRequest) ResponseEntity~ApiResponse~
    +createEstimateVersion(Jwt, UUID, CreateEstimateVersionRequest) ResponseEntity~ApiResponse~
    +submitEstimateVersion(Jwt, UUID, int) ApiResponse~EstimateVersionView~
    +approveEstimateVersion(Jwt, UUID, int) ApiResponse~EstimateVersionView~
  }
  class MaintenanceExecutionController {
    +releaseWorkOrder(Jwt, UUID) ApiResponse~WorkOrderView~
    +startWorkOrder(Jwt, UUID) ApiResponse~WorkOrderView~
    +createWorkLog(Jwt, UUID, CreateWorkLogRequest) ResponseEntity~ApiResponse~
    +submitWorkLog(Jwt, UUID, UUID) ApiResponse~WorkLogView~
    +verifyWorkLog(Jwt, UUID, UUID) ApiResponse~WorkLogView~
    +batchVerifyWorkLogs(Jwt, UUID) ApiResponse~List~
    +declareComplete(Jwt, UUID) ApiResponse~WorkOrderView~
  }
  class MaintenanceScopeAdvisorService {
    +suggestScope(UUID, SuggestScopeRequest) SuggestScopeResponse
    +suggestEstimateNorms(UUID, UUID) SuggestEstimateResponse
    +checkAcceptanceCompliance(UUID, UUID) AcceptanceComplianceResponse
  }
  class MaintenanceWorkOrder {
    -UUID id
    -WorkOrderStatus status
    -UUID reinspectionId
    -UUID reinspectionReportVersionId
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

- **MaintenanceController & MaintenanceScopeAdvisorService (`FE-07`)**: Query `repair_knowledge_chunks` (`pgvector`) to recommend corrective scope and acceptance criteria (`/suggest-scope`), provision `initialTasks` in 1 click inside `WorkOrderService.create` (`92fb490`), and generate standard Vietnamese engineering cost norm breakdowns (`LABOR`, `MATERIAL`, `EQUIPMENT`, `CONTINGENCY`) via `/suggest-estimate`.
- **MaintenanceExecutionController (`FE-07`)**: Governs repair execution (`READY` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `WORK_COMPLETED`), Change Orders, and 1-click Team Lead batch work log verification (`POST /work-orders/{id}/work-logs/batch-verify`), enforcing that no pending Change Orders or unverified work logs exist on `declareComplete()`.

#### 3.7.2 Work Order Planning, 1-Click RAG Tasks, Norm Estimation & Batch Log Verification Sequence Diagram

```mermaid
%% title: Work Order Planning, 1-Click RAG Tasks, Norm Estimation and Batch Log Verification Sequence Diagram
sequenceDiagram
  autonumber
  actor Cust as Customer (Budget Approver)
  actor Lead as Maintenance Engineer (TEAM_LEAD)
  participant MaintCtrl as MaintenanceController
  participant ExecCtrl as MaintenanceExecutionController
  participant Advisor as MaintenanceScopeAdvisorService
  participant DB as PostgreSQL (maintenance_* & repair_knowledge_chunks)

  Cust->>MaintCtrl: POST /api/v1/maintenance/suggest-scope (sourceFindingId)
  MaintCtrl->>Advisor: suggestScope() -> pgvector HNSW query (TCVN/EN/ISO)
  Advisor-->>Cust: SuggestedScope + SuggestedTasks
  Cust->>MaintCtrl: POST /api/v1/maintenance/work-orders (with initialTasks[] 1-click enabled)
  MaintCtrl->>DB: insertWorkOrder(DRAFT) & bulkInsertInitialTasks(Task #1..#N)

  Lead->>MaintCtrl: POST /api/v1/maintenance/work-orders/{id}/suggest-estimate
  MaintCtrl->>Advisor: suggestEstimateNorms(workOrderId)
  Advisor-->>Lead: SuggestEstimateResponse (LABOR, MATERIAL, EQUIPMENT, CONTINGENCY norms)
  Lead->>MaintCtrl: POST /estimate-versions & POST /submit -> WorkOrder: AWAITING_APPROVAL
  Cust->>MaintCtrl: POST /estimate-versions/1/approve (custId != Lead) -> WorkOrder: APPROVED

  Lead->>ExecCtrl: POST /release (READY) -> POST /start (IN_PROGRESS) -> POST /work-logs (SUBMITTED)
  Lead->>ExecCtrl: POST /api/v1/maintenance/work-orders/{id}/work-logs/batch-verify (1-Click Batch Verify)
  ExecCtrl->>DB: markAllSubmittedLogsVerified(VERIFIED)
  Lead->>ExecCtrl: POST /api/v1/maintenance/work-orders/{id}/declare-complete
  ExecCtrl->>DB: assertNoPendingChangeOrders & assertAllLogsVerified -> WorkOrder: WORK_COMPLETED
```

---

### 3.8 FE-08 Completion Report, 3-Way Re-inspection Verification & Cost Closure

#### 3.8.1 Class Diagram

```mermaid
%% title: Re-inspection 3-Way Verification, RAG Compliance Audit and Cost Closure Class Diagram
classDiagram
  class MaintenanceExecutionController {
    +getAutoDraftReport(Jwt, UUID) ApiResponse~AutoDraftReportResponse~
    +getAcceptanceCompliance(Jwt, UUID) ApiResponse~AcceptanceComplianceResponse~
    +recordAcceptanceDecision(Jwt, UUID, RecordAcceptanceRequest) ResponseEntity~ApiResponse~
    +reconcileCosts(Jwt, UUID, ReconcileCostsRequest) ApiResponse~CostReconciliationView~
    +closeWorkOrder(Jwt, UUID) ApiResponse~WorkOrderView~
  }
  class InspectionController {
    +getReinspectionVerifications(Jwt, UUID) ApiResponse~List~
    +updateReinspectionVerification(Jwt, UUID, UUID, UpdateDefectVerificationRequest) ApiResponse~ReinspectionVerificationResponse~
  }
  class ReinspectionVerificationService {
    +getVerifications(UUID, UUID) List~ReinspectionVerificationResponse~
    +updateVerification(UUID, UUID, UUID, UpdateDefectVerificationRequest) ReinspectionVerificationResponse
  }
  class InspectionReinspectionListener {
    +onReinspectionRequested(ReinspectionRequestedEvent) void
  }
  class WorkOrderReinspectionListener {
    +onReinspectionCreated(ReinspectionCreatedEvent) void
    +onReinspectionReportPublished(ReinspectionReportPublishedEvent) void
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
  InspectionController --> ReinspectionVerificationService
  ReinspectionVerificationService --> ReinspectionDefectVerification
  InspectionReinspectionListener --> ReinspectionDefectVerification
```

**Class Specifications**

- **MaintenanceExecutionController (`auto-draft` & `acceptance-compliance`)**: Synthesizes a 5-part completion report from completed tasks, verified hours, `testReadings`, `asLeftCondition`, and approved Change Orders (`GET /reports/auto-draft`), and evaluates quantitative field measurements against `TCVN` standards (`GET /acceptance-compliance`).
- **InspectionReinspectionListener, WorkOrderReinspectionListener & ReinspectionVerificationService**: Orchestrate the event-driven re-inspection loop (`ReinspectionRequestedEvent` $\rightarrow$ `Inspection` with `inspection_type = 'RE_INSPECTION'` + `ReinspectionDefectVerification` rows $\rightarrow$ `ReinspectionCreatedEvent` $\rightarrow$ 3-way verification `RESOLVED`/`UNRESOLVED`/`INCONCLUSIVE` $\rightarrow$ `ReinspectionReportPublishedEvent` reinstating the Work Order for final `CUSTOMER` acceptance).

#### 3.8.2 Auto-Draft Completion Report, RAG Compliance Audit, 3-Way Re-inspection & Cost Closure Sequence Diagram

```mermaid
%% title: Auto-Draft Completion Report, 3-Way Re-inspection and Cost Closure Sequence Diagram
sequenceDiagram
  autonumber
  actor Author as Maintenance Engineer (REPORT_AUTHOR)
  actor Cust as Customer (Accepting Reviewer)
  actor Insp as Partner Inspector (INSPECTOR)
  actor Mgr as Platform Manager (MANAGER)
  participant ExecCtrl as MaintenanceExecutionController
  participant InspCtrl as InspectionController
  participant Outbox as Spring Modulith Events
  participant DB as PostgreSQL (maintenance_*, inspections, reinspection_defect_verifications)

  Author->>ExecCtrl: GET /api/v1/maintenance/work-orders/{id}/reports/auto-draft
  ExecCtrl-->>Author: 5-Part Synthesized Markdown Draft
  Author->>ExecCtrl: POST /reports -> POST /verify -> POST /submit -> WorkOrder: SUBMITTED_FOR_ACCEPTANCE

  Cust->>ExecCtrl: GET /api/v1/maintenance/work-orders/{id}/acceptance-compliance (RAG Audit)
  ExecCtrl-->>Cust: AcceptanceComplianceResponse (complianceScore, status, checks)
  Cust->>ExecCtrl: POST /acceptance-decisions (decision=REINSPECTION_REQUIRED)
  ExecCtrl->>Outbox: publish ReinspectionRequestedEvent
  Outbox->>DB: createInspection(type=RE_INSPECTION) + createDefectVerifications(repairProofUrl, repairEngineerNotes)
  Outbox->>DB: emit ReinspectionCreatedEvent -> attach reinspectionId to WorkOrder

  Insp->>InspCtrl: Execute 3-Step Re-inspection & PUT /reinspection-verifications/{vId} (newEvidenceId, RESOLVED)
  Insp->>InspCtrl: Auto-Compile & Submit Re-inspection Report (SUBMITTED)
  Mgr->>InspCtrl: Review & Publish Re-inspection Report (PUBLISHED)
  InspCtrl->>Outbox: publish ReinspectionReportPublishedEvent
  Outbox->>DB: attach reinspectionReportVersionId & reinstate Completion Report to SUBMITTED

  Cust->>ExecCtrl: Review Published Re-inspection Report -> POST /acceptance-decisions (ACCEPTED)
  Cust->>ExecCtrl: Inherit Baseline Costs -> POST /cost-reconciliation (COST_RECONCILED) -> POST /close (CLOSED)
```

#### 3.8.3 WF-04 Activity Diagram — Maintenance Work Order, RAG Advisor, 3-Way Re-inspection & Cost Closure

```mermaid
%% title: WF-04 Activity Diagram - Maintenance Work Order, RAG Advisor, 3-Way Re-inspection and Closure
flowchart TD
  subgraph CU4["Customer (CUSTOMER - Budget Approver & Accepting Reviewer)"]
    D1(["Start: Create WorkOrder from Published Defect + 1-Click RAG Tasks -> DRAFT"])
    D4{"Approve RAG-Assisted\nCost Estimate?"}
    D5["Approve Estimate -> WorkOrder: APPROVED"]
    D9["Run RAG Acceptance Compliance Audit (/acceptance-compliance)"]
    D10{"Acceptance Decision?"}
    D11["Request Re-inspection (REINSPECTION_REQUIRED)"]
    D15["Record ACCEPTED -> Reconcile Actual Costs (COST_RECONCILED) -> Close WorkOrder (CLOSED)"]
    D16(["End: Closed Work Order with Full Audit & Re-inspection Traceability"])
  end

  subgraph ME4["Maintenance Engineer Team (TEAM_LEAD, REPORT_AUTHOR, MEMBER)"]
    D2["Generate RAG Cost Norms (/suggest-estimate) & Submit Estimate -> AWAITING_APPROVAL"]
    D6["Execute Repairs, Upload Repair Proof & 1-Click Batch Verify Work Logs -> WORK_COMPLETED"]
    D8["Auto-Draft (/reports/auto-draft), Verify & Submit Completion Report -> SUBMITTED_FOR_ACCEPTANCE"]
  end

  subgraph RI4["Partner Inspector & Platform Manager (3-Step Re-inspection Loop)"]
    D12["Auto-Create Linked RE_INSPECTION Mission & 3-Way Verification Cards"]
    D13["Inspector Captures New Drone Proof & Marks RESOLVED / UNRESOLVED / INCONCLUSIVE"]
    D14["Manager Reviews & Publishes Re-inspection Report -> Reinstates WorkOrder"]
  end

  D1 --> D2 --> D4
  D4 -->|"Reject"| D2
  D4 -->|"Approve"| D5 --> D6 --> D8 --> D9 --> D10
  D10 -->|"REWORK_REQUIRED"| D6
  D10 -->|"REINSPECTION_REQUIRED"| D11 --> D12 --> D13 --> D14 --> D9
  D10 -->|"ACCEPTED"| D15 --> D16
```
