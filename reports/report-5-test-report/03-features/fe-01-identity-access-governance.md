# FE-01: Identity and Access Governance

## Scope baseline

Client self-registration creates one active customer organization and its first Client account. JWT-based authentication, role- and scope-based authorization, organization and assignment scope, profile management, and audit logs enforce access on the server. Self-registration cannot create platform or service-workforce roles.

## Supporting verification

The checks below support FE-01 but are not additional WFx functional cases and are excluded from the 15-case workbook totals.

### W3 authentication and migration foundation gate

Jira SCRUM-58/T001 under SCRUM-108 covers the W3 smoke check for existing authentication and migrations V1–V9. It is owned by Bách and remains a delivery prerequisite for the test environment; it is not counted as an additional functional case in this workbook.

Automated execution on 2026-09-22: Passed. WorkflowBaselineTest verified Flyway versions V1–V9 on a clean PostgreSQL Testcontainers database, and generated credentials authenticated all five role fixtures: ADMIN, CLIENT, SERVICE_MANAGER, INSPECTOR, and MAINTENANCE_ENGINEER. No fixture uses a default password or committed secret. MinIO/evidence storage is tracked separately under FE-04/WF3 (T025/SCRUM-85) and is not part of the FE-01 gate.

### Role-aware portal and navigation

- Preconditions: The canonical five role codes and Report 3 section 3.1.3 screen-access matrix are available to the frontend policy.
- Procedure: Run npm test in the frontend repository; assert access-policy decisions for every workspace/section/role combination, single- and multi-workspace entry targets, legacy-path redirect targets, and the no-access fallback.
- Expected result: Policy decisions match the SRS matrix; a user with multiple workspaces is sent to the chooser; an unavailable section resolves to the access-denied path.
- Round 1: Passed on 2026-09-24; tester: Codex (automated).
- Evidence: src/app/permissions/accessPolicy.test.ts — 19 tests passed.

### Browser authentication flow

- Preconditions: The versioned browser auth endpoints and canonical role contract are available; frontend tests use a mocked HTTP transport.
- Procedure: Run npm.cmd test in frontend; verify form validation, fetching /auth/csrf and sending its declared header before auth mutations, sign-in request/response mapping, cookie-backed refresh, Client registration, first-password setup and logout, plus role-aware return routing and rejection of external/unauthorized return paths.
- Expected result: Access tokens are returned to in-memory session state only; browser refresh credentials are not read from or stored in web storage; registration submits only the Client onboarding contract; assigned backend roles determine the destination; rejected refresh clears the local session.
- Round 1: Passed on 2026-09-24; tester: Codex (automated).
- Evidence: src/shared/api/client.test.ts, src/features/auth/api/authApi.test.ts, src/features/auth/schemas/authSchemas.test.ts, src/features/auth/utils/authRedirect.test.ts, and src/features/auth/api/sessionBootstrap.test.ts — 26 auth-flow tests passed; the full frontend suite at that auth-flow run passed 45/45, including the 19 portal-policy tests. The later complete run passed 52/52 after adding shared-envelope tests and WF3 inspection/report page tests.
- Scope note: The transport is mocked in these frontend tests. A live browser-to-Spring-auth-API end-to-end run was not part of this verification. These results are not an end-to-end test claim.

### Client self-registration persistence gate

- Preconditions: The versioned browser auth endpoints are available; the backend integration environment provisions PostgreSQL through Testcontainers with Flyway migrations V1–V10 applied.
- Procedure: Run `.\mvnw.cmd test -Dtest=ClientRegistrationApiIntegrationTest` in SmartDroneInspection-backend; POST `/api/v1/auth/register` through MockMvc with a CSRF token; assert 201 Created, the normalized organization code, the `CLIENT` role on the created user, and a `CLIENT_REGISTRATION`/`SUCCESS` row in `security_audit_events` whose `subject_user_id` references the created user.
- Expected result: Registration persists the organization, user, role assignment, and security audit event in one transaction without violating the `security_audit_events.subject_user_id` foreign key.
- Round 1: Passed on 2026-09-28; tester: Codex (automated).
- Evidence: Backend `src/test/java/com/smartdroneinspection/users/ClientRegistrationApiIntegrationTest.java` plus the updated `ClientRegistrationServiceTest`; full `.\mvnw.cmd verify` passed 165/165 tests with the JaCoCo and Spring Modulith gates.
- Defect note: Before this round, `POST /api/v1/auth/register` returned 500 because `ClientRegistrationService` passed the generated user id to `SecurityAuditService.record` (raw `JdbcTemplate` SQL) before Hibernate flushed the `users` insert, so the audit insert failed the foreign key introduced in `V3__authentication.sql` (present since commit 46baa59). The fix flushes the saved user before the audit write.
- Scope note: This is an API-level integration test against a real database, not a live browser end-to-end run.

### Admin user creation persistence gate

- Preconditions: An ADMIN account exists; the backend integration environment provisions PostgreSQL through Testcontainers with Flyway migrations V1-V10 applied.
- Procedure: Run `.\mvnw.cmd test -Dtest=AdminUserApiIntegrationTest` in SmartDroneInspection-backend; POST `/api/v1/platform/users` through MockMvc as an ADMIN JWT with a CSRF token; assert 201 Created, the `MAINTENANCE_ENGINEER` role on the created user, a non-empty temporary password, and a `USER_CREATED`/`SUCCESS` row in `security_audit_events` whose `actor_user_id` is the admin and whose `subject_user_id` references the created user.
- Expected result: Creation persists the user, role assignment, and security audit event in one transaction without violating the `security_audit_events.subject_user_id` foreign key.
- Round 1: Passed on 2026-09-28; tester: Claude Code (automated).
- Evidence: Backend `src/test/java/com/smartdroneinspection/users/AdminUserApiIntegrationTest.java` plus `AdminUserServiceTest`; full `.\mvnw.cmd verify` passed 167/167 tests with the JaCoCo and Spring Modulith gates.
- Defect note: Before this round, `POST /api/v1/platform/users` returned 500 for the same cause as the client-registration defect above: `AdminUserService.create` passed the generated user id to `SecurityAuditService.record` (raw `JdbcTemplate` SQL) before Hibernate flushed the `users` insert. The fix uses `saveAndFlush` before the audit write. Verified RED first: the new integration test failed with 500 instead of 201 on the unfixed code, then passed after the one-line fix.
- Scope note: This is an API-level integration test against a real database, not a live browser end-to-end run.

### Cross-cutting successful API response-envelope verification

This is a shared API contract check recorded here for traceability. It is not an FE-01-only acceptance case or an additional workbook row.

- Preconditions: The backend and first-party clients use the same versioned response contract; Docker-backed backend integration tests are available.
- Procedure: Run .\mvnw.cmd verify in backend, npm.cmd test in frontend, and flutter test plus flutter analyze in mobile; inspect server/client adapter assertions for success envelopes, Problem Details, and bodyless logout behavior.
- Expected result: Successful JSON bodies expose success, message, and data; web/mobile callers receive the inner typed payload; error responses remain Problem Details; 204 No Content remains bodyless. Binary streaming controllers are intentionally not wrapped by the JSON envelope.
- Round 1: Passed on 2026-09-24; tester: Codex (automated).
- Evidence: Backend ApiResponseTest and WorkflowBaselineTest; frontend src/shared/api/apiResponse.test.ts; mobile test/core/network/api_response_interceptor_test.dart. Full verification commands and results are listed in the delivery hand-off.

## Coverage boundary

The recorded gates verify authentication/migration setup, role-to-screen policy, browser-auth contracts, client-registration persistence and its audit record, and the shared API envelope. They do not by themselves establish complete profile-management or audit-log acceptance coverage, nor a live browser end-to-end registration/login run. Those requirements remain in the FE-01 scope baseline.
