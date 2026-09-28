# Implementation Plan: Docker Deployment for Backend and Web

**Feature Branch**:
- Backend: `feat/docker-deployment`
- Frontend: `feat/docker-deployment`
- Docs: `docs/docker-deployment`
**Created**: 2026-09-28
**Spec**: [spec.md](./spec.md)
**Owner**: Bách

## Proposed Changes

### Backend Repository (`SmartDroneInspection-backend/`)

- Add `Dockerfile`: multi-stage build using `maven:3.9-eclipse-temurin-21` and `eclipse-temurin:21-jre-alpine`.
  - Dependency caching with `mvn dependency:resolve dependency:resolve-plugins`.
  - Build fat jar with `mvn -DskipTests clean package`.
  - Runtime executes under non-root user `appuser`.
  - Healthcheck probes `http://localhost:8080/actuator/health`.
- Add `.dockerignore`: exclude `target/`, IDE files, `.git/`, `.env*`.
- Add `.env.example`: template with all required keys, generation commands, and security guidelines.
- Update `docker-compose.yml`:
  - Keep `postgres` (pgvector 17) and `minio` services; bind ports to `127.0.0.1` by default.
  - Add `backend` service with `depends_on` healthy postgres & minio, active profile `prod`.
  - Add `web` service (from frontend directory) with `depends_on` healthy backend.
  - Expose `web` on `${WEB_PORT:-80}`.
- Update `README.md`: document single-command full-stack deployment alongside host development workflow.

### Frontend Repository (`SmartDroneInspection-frontend/`)

- Add `Dockerfile`: multi-stage build using `node:22-alpine` and `nginx:1.27-alpine`.
  - `npm ci --legacy-peer-deps` for deterministic dependencies.
  - `npm run build` producing static assets.
  - Healthcheck probes `http://localhost:80/`.
- Add `nginx.conf`:
  - Reverse proxy `/api/` to `backend:8080` (same-origin, eliminates CORS, preserves HttpOnly refresh cookie).
  - SPA fallback: `try_files $uri $uri/ /index.html` with no-cache header on HTML.
  - Static asset caching (`1y`, immutable).
  - Gzip compression and standard security headers.
- Add `.dockerignore`: exclude `node_modules/`, `dist/`, `.git/`, IDE files.

### Docs Repository (`SmartDroneInspection-docs/`)

- Add `spec.md` and `plan.md` in `development/plans/bach/2026-09-28-docker-deployment/`.

## Verification Checklist

Executed 2026-09-28 on Windows 11, Docker Desktop 29.7.2 (Compose v5.4.0).

- [x] Frontend image builds cleanly: `docker compose build` produced `smartdroneinspection-web:latest` (79.6 MB).
- [x] Backend image builds cleanly: produced `smartdroneinspection-backend:latest` (642 MB).
- [x] Docker Compose configuration parses and validates: `docker compose config`.
- [x] Complete stack starts and reaches steady state: all four containers report `healthy`.
- [x] SPA serves at `http://localhost/` → 200.
- [x] SPA history fallback: `GET /login` and `GET /inspections` → 200 (not 404).
- [x] Static asset caching: `Cache-Control: public, immutable, max-age=31536000`.
- [x] API reverse proxy is same-origin: `GET /api/v1/auth/csrf` → 200 with `ApiResponse` envelope.
- [x] Flyway applied against the container database: "Successfully validated 10 migrations", schema at version 10.
- [x] MinIO console reachable at `http://localhost:9001/` → 200.
- [x] Host backend test suite green: `.\mvnw.cmd verify` → 164/164, BUILD SUCCESS.
- [ ] **End-to-end browser login: NOT VERIFIED.** Registration through the API fails; see below.

## Issues found during verification

### 1. Health checks failed due to IPv6 loopback resolution (fixed)

Both health checks probed `http://localhost:<port>/`. Alpine resolves `localhost` to IPv6 `::1`,
but nginx and Tomcat bind IPv4 only, so the probe was refused and the `web` container stayed
`unhealthy` indefinitely. Changed both probes to `127.0.0.1`. Compose-level `healthcheck` blocks
were also removed, because a compose health check silently overrides the image's own and had been
masking the Dockerfile definition.

### 2. Backend image build failed on dependency prefetch (fixed)

`mvn dependency:resolve` aborted the build when Maven Central metadata for some Testcontainers
artifacts was unreachable. Switched to `dependency:go-offline`, which stops at the first missing
optional file instead of failing the layer.

### 3. Spotless blocked the container build (fixed)

Spotless checks `.gitignore` and `*.yml`, and a Windows CRLF checkout fails that check on Linux,
so `package` aborted inside the image. The container build now passes `-Dspotless.check.skip=true`;
formatting remains gated by `.\mvnw.cmd verify` on the host.

### 4. Host port 5432 was already in use (worked around)

A native `postgresql-x64-17` Windows service owns 5432. The stack's published port moved to 5433
via `POSTGRES_PORT`; the container still listens on 5432 internally, so no application
configuration changed.

### 5. Client self-registration returns HTTP 500 (OPEN — application defect, not Docker)

**Not caused by this change.** Reproduced against the containerized stack, then traced to the
application layer.

`POST /api/v1/auth/register` fails with `INTERNAL_ERROR`. Backend log:

```
ERROR: insert or update on table "security_audit_events" violates foreign key constraint
       "security_audit_events_subject_user_id_fkey"
Detail: Key (subject_user_id)=(0bfcd208-3522-46fe-ac62-b85f9d46fd4b) is not present in table "users".
```

Mechanism: `User.id` is `@Id @GeneratedValue private UUID id`
([User.java:25](../../../../../SmartDroneInspection-backend/src/main/java/com/smartdroneinspection/users/domain/User.java#L25)),
so Hibernate assigns the identifier in memory and the `INSERT` is deferred until flush/commit.
`ClientRegistrationService.register` calls `users.save(client)` and then immediately passes
`client.getId()` to `SecurityAuditService.record`
([ClientRegistrationService.java:73-77](../../../../../SmartDroneInspection-backend/src/main/java/com/smartdroneinspection/users/service/ClientRegistrationService.java#L73-L77)).
That service writes through raw `JdbcTemplate`, which bypasses the Hibernate flush order, so the
audit row references a user row that does not exist yet. The `subject_user_id` foreign key has been
present since the auth module's original migration
(`V3__authentication.sql`, introduced in commit `46baa59`), so this defect is not a recent
regression — registration has failed this way for as long as the audit call has existed.

Corroborating evidence that registration has never worked end-to-end:

- The `security_audit_events` table contains **no** `CLIENT_REGISTRATION` row, while four other
  event types — including `AUTH_LOGIN` FAILURE rows — are present. The audit path itself is
  healthy; only registration fails.
- All five existing users share one `created_at` timestamp and there is no seed script in any
  repository, so they were inserted directly rather than through this endpoint.
- The existing test `ClientRegistrationServiceTest` mocks both `UserRepository` and
  `SecurityAuditService`, so it never reaches a database and cannot observe the constraint.
  The full `verify` suite passes 164/164 with the defect present.

The failed registration rolls back cleanly: user count stayed at 5, organization count at 1, and
no partial rows were written.

**This is out of scope for the Docker change** and is deliberately not fixed here — it is an
application-logic defect that requires its own test-first fix and a Report 5 case. Reported to the
product owner as a follow-up.
