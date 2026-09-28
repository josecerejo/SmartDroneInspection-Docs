# Feature Specification: Docker Deployment for Backend and Web

**Created**: 2026-09-28
**Status**: Draft — awaiting spec review
**Owner**: Bách
**Input**: User request: "làm docker cho cả 3, chuyên nghiệp" (make Docker for all three, professional grade)
**Related references**: [Report 2 §241](../../../../reports/report-2-project-management-plan/report2-project-management-plan.md), [AGENTS.md](../../../../../AGENTS.md), [Backend CLAUDE.md](../../../../../SmartDroneInspection-backend/CLAUDE.md)

## Summary

The workspace currently uses Docker for **infrastructure only**: a single
`docker-compose.yml` in the backend repository starts PostgreSQL (pgvector) and MinIO, while the
backend, web, and mobile applications all run on the host developer machine. Report 2 §241 states
the deployment target is "Docker Compose on an approved development/test server", so the current
setup cannot satisfy the documented deployment model.

This change containerizes the **backend** and **web** applications so that a single
`docker compose up -d` on a test server yields a working stack. Mobile remains outside Docker and
continues to run from a developer machine or emulator against the host backend, because a Flutter
mobile application is not a deployable server component.

## Scope

### In scope

- A multi-stage `Dockerfile` for `SmartDroneInspection-backend` producing a runnable JRE image.
- A multi-stage `Dockerfile` for `SmartDroneInspection-frontend` producing an nginx-served static bundle.
- `nginx.conf` providing SPA history fallback and same-origin `/api/` reverse proxying.
- `.dockerignore` for both repositories.
- Extension of the existing `docker-compose.yml` with `backend` and `web` services, health checks,
  ordered startup, and host-binding hardening.
- `.env.example` documenting every required variable, including secret generation instructions.
- Runbook documentation for build, start, verify, and teardown.

### Out of scope

- **Mobile containerization.** Decided against; see Decision Log D2.
- **Flutter Web.** Decided against; see Decision Log D3.
- **YOLO inference service and LLM report-draft service.** Neither is implemented as a deployable
  component in this workspace; both remain disabled-by-default external URLs.
- **TLS termination.** Decided against for this iteration; see Decision Log D4.
- **CI pipeline changes.** No CI configuration exists in these repositories today.
- **Kubernetes or any orchestration beyond Compose.**
- **Application code changes.** This change adds build and runtime packaging only. If a container
  build surfaces an application defect, that defect is reported, not silently fixed here.

## Architecture

```
                        Docker network: smartdroneinspection
                     ┌──────────────────────────────────────────┐
   Browser ──:80──►  │  web  (nginx)                            │
                     │    ├── /          → static SPA bundle    │
                     │    └── /api/  ──────► backend:8080       │
                     │                          │               │
                     │                          ├──► postgres:5432
                     │                          └──► minio:9000  │
                     └──────────────────────────────────────────┘
```

**Same-origin by construction.** The browser loads the SPA and calls the API on one origin, because
nginx proxies `/api/` to the backend over the internal network. Two consequences make this the
central design decision rather than a convenience:

1. **CORS is not needed.** The backend's `AuthProperties.allowedOrigins` default
   (`http://localhost:3000`) never matches a deployed origin, so without a proxy the deployment
   would require `AUTH_ALLOWED_ORIGINS` to be set correctly or every browser API call would fail
   preflight. Proxying removes that failure mode entirely.
2. **The refresh-token cookie works.** The frontend keeps access tokens in memory and relies on an
   HttpOnly refresh cookie
   ([client.ts](../../../../../SmartDroneInspection-frontend/src/shared/api/client.ts)). Cookies are
   origin-scoped, so a cross-origin API host would force `SameSite=None` and a wider CORS surface.
   A single origin keeps the cookie's default behavior intact.

**Exposure surface.** Only `web` publishes a port to the outside. `backend`, `postgres`, and `minio`
are reachable only inside the Docker network. Development access to PostgreSQL and MinIO remains
available by binding those ports to `127.0.0.1` rather than all interfaces, so a test server does
not expose a database and an object store to its network.

## Component design

### Backend image

Two stages. The build stage separates dependency resolution from source compilation so that editing
application code does not invalidate the dependency layer:

| Stage | Base | Purpose |
| --- | --- | --- |
| `build` | `maven:3.9-eclipse-temurin-21` | `mvn dependency:go-offline`, then `mvn -DskipTests package` |
| runtime | `eclipse-temurin:21-jre-alpine` | Copy the fat jar, run as a non-root user |

Requirements:

- The runtime image **must not run as root**. A dedicated unprivileged account is created and used.
- JVM memory is bounded relative to the container limit (`-XX:MaxRAMPercentage`) so the container
  does not exceed its allocation before the orchestrator can react.
- The build **must pass `-DskipTests`.** The backend test suite depends on Testcontainers
  ([pom.xml:127](../../../../../SmartDroneInspection-backend/pom.xml)), which requires a Docker
  daemon that is not available inside `docker build`. `./mvnw verify` remains the authoritative
  test and quality gate and continues to run on the host or in CI.
- The image is a deployment artifact, **not** evidence that tests passed. The runbook and Report 5
  must keep this distinction explicit.

### Frontend image

Two stages:

| Stage | Base | Purpose |
| --- | --- | --- |
| `build` | `node:24-alpine` | `npm ci`, then `npm run build` |
| runtime | `nginx:1.27-alpine` | Serve `/dist` plus the proxy configuration |

Requirements:

- Node major version **must satisfy the lockfile's engine constraint**
  (`^22.22.2 || ^24.15.0 || >=26.0.0`). Node 24 is selected because it matches the version in local
  use (v24.19.0), keeping the container build aligned with the version developers test against.
- `npm ci` is used, not `npm install`, so the lockfile fully determines the dependency tree.
- `VITE_API_URL` is deliberately **not** set at build time. The client falls back to the relative
  path `/api/v1`, which is what allows one image to run behind any hostname without rebuilding.
  Setting it would bake a hostname into the bundle and defeat the proxy design.
- nginx must provide SPA history fallback (`try_files ... /index.html`). The application uses
  React Router with routes such as `/login` and `/inspections`; without fallback, a browser refresh
  on any non-root route returns 404.
- Static assets are served with long-lived cache headers; `index.html` is served no-cache so a
  redeploy is picked up without a hard refresh.

### Compose

The existing file keeps its two infrastructure services and gains two application services.

| Service | Change | Release | Health check |
| --- | --- | --- | --- |
| `postgres` | port bound to loopback | unchanged | existing `pg_isready` |
| `minio` | port bound to loopback | unchanged | existing HTTP probe |
| `backend` | **new** | `prod` Spring profile | `/actuator/health` |
| `web` | **new** | — | HTTP probe on `/` |

Requirements:

- Startup is **ordered by health, not by start**: `backend` waits for `postgres` to be healthy;
  `web` waits for `backend` to be healthy. Waiting only for container start would let the backend
  begin its Flyway migration before PostgreSQL accepts connections.
- All four services use `restart: unless-stopped` so a test server recovers from a reboot.
- `web` publishes `${WEB_PORT:-80}:80`. All other ports bind to `127.0.0.1`.
- The Compose file remains in `SmartDroneInspection-backend/`, with the frontend build context
  referenced as `../SmartDroneInspection-frontend`. This is the least disruptive placement;
  the trade-off (Compose requires both repositories checked out side by side) is accepted and
  documented.

## Configuration and secrets

The backend runs under the `prod` profile
([application-prod.yml](../../../../../SmartDroneInspection-backend/src/main/resources/application-prod.yml)),
which changes three behaviors that the Compose environment must satisfy.

**Startup fails without secrets.** Under `prod`,
[AuthSecurityBeans.java:74](../../../../../SmartDroneInspection-backend/src/main/java/com/smartdroneinspection/users/security/AuthSecurityBeans.java#L74)
throws when `AUTH_JWT_SECRET` or `AUTH_REFRESH_TOKEN_PEPPER` is absent, and both must be Base64
decoding to at least 32 bytes. This fail-fast behavior is correct and is preserved; the runbook
must therefore require a populated `.env` *before* the first `up`, or the backend container will
crash-loop.

**Cookie security must match the transport.** `application-prod.yml` sets `secure-cookies: true`,
which instructs the browser to send refresh cookies over HTTPS only. A test server reached over
plain HTTP would authenticate and then fail to refresh. The Compose environment sets
`AUTH_SECURE_COOKIES=false` for internal-network use, with an inline comment stating that this must
be reverted to `true` once TLS is in place.

**MinIO is enabled and pointed at the service name.** The `prod` profile enables MinIO and requires
an endpoint. In Compose the endpoint is `http://minio:9000`, and the credentials must match the
`MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` values given to the MinIO service. No bucket-initialization
container is needed: the backend creates the bucket on first use
([MinioEvidenceObjectStore.java:55](../../../../../SmartDroneInspection-backend/src/main/java/com/smartdroneinspection/infrastructure/storage/MinioEvidenceObjectStore.java#L55)).

**Hostnames change from `localhost` to service names.** `POSTGRES_*` connection settings must target
the `postgres` service rather than `localhost`.

**Secret handling.** `.env` is already ignored by the backend repository. A committed `.env.example`
lists every variable with placeholder values and the exact command to generate compliant secrets.
No real secret is committed. Generated secrets are never printed into logs or documentation.

## Verification plan

Verification is performed on the host and the exact commands and output are recorded.

| # | Check | Command | Pass condition |
| --- | --- | --- | --- |
| 1 | Compose file is valid | `docker compose config` | Parses; all variables resolve |
| 2 | Images build | `docker compose build` | Both images build without error |
| 3 | Stack starts | `docker compose up -d` | Four containers running |
| 4 | Services report healthy | `docker compose ps` | `backend`, `postgres`, `minio` healthy |
| 5 | Backend is live | `curl -fsS localhost/api/v1/...` or actuator probe through the proxy | 200 with expected envelope |
| 6 | Migrations applied | Backend startup logs / Flyway history | No migration failure |
| 7 | SPA loads | `curl -fsS localhost/` | HTML bundle returned |
| 8 | SPA history fallback | `curl -fsS localhost/login` | `index.html`, not 404 |
| 9 | Proxy reaches API | `curl -i localhost/api/v1/...` | Proxied response, not 502 |
| 10 | Same-origin auth works | Log in through the browser | Token issued; refresh succeeds; no CORS error |
| 11 | Evidence upload works | Upload evidence | Object lands in MinIO; download succeeds |
| 12 | Restart resilience | `docker compose restart` | Stack returns to healthy |
| 13 | Backend suite still green | `./mvnw verify` on host | Passes (unchanged from baseline) |

**Docker-unavailable fallback.** If Docker is not available in the verification environment, checks
1–12 are reported as `Blocked`, never as `Passed`, consistent with the existing runbook rule.

## Documentation impact

| Document | Update |
| --- | --- |
| This spec and a companion `plan.md` | New |
| `SmartDroneInspection-backend/README.md` | Replace the infrastructure-only quickstart with the full stack runbook |
| `SmartDroneInspection-docs/backend/` deployment or getting-started guidance | Document the container path alongside the host path |
| `SmartDroneInspection-docs/project-reference/` (data model / configuration) | Record the container hostnames and new variables if configuration behavior is described there |
| Report 2 §241 | Reconcile with the implemented deployment shape |
| Report 5 | Record the executed verification, or `Blocked` if Docker was unavailable |

No Report 3 SRS change is anticipated: this is packaging and deployment, not product behavior.
If implementation reveals a requirement-level discrepancy, it is raised rather than silently
absorbed.

## Risks

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Secrets absent → crash loop on first start | High | `.env.example` plus a preflight check in the runbook; fail-fast behavior is intentional |
| `AUTH_SECURE_COOKIES=false` carried to a real production host | High | Inline comment in `.env.example` and an explicit step in the runbook to re-enable under TLS |
| Compose build context crosses repository boundaries | Medium | Both repositories must be checked out as siblings; documented in the runbook |
| `COPY . .` accidentally copies host `node_modules` or `target/` | Medium | `.dockerignore` added to both repositories |
| Image built with `-DskipTests` mistaken for a tested artifact | Medium | Stated in the runbook, the Dockerfiles, and the Report 5 entry |
| Base images drift over time | Low | Images pinned to explicit major/minor tags, not `latest` |
| Backend bound to a long migration on first start exceeds the health-check window | Low | Health check uses a start period and generous retries |

## Decision log

| ID | Decision | Rationale |
| --- | --- | --- |
| D1 | Target is a **deployable stack on a test server**, not a dev-only container setup | Matches Report 2 §241; chosen by the product owner |
| D2 | **Mobile is not containerized** | A Flutter mobile app is not a deployable server component. An emulator-in-container path is multi-gigabyte and requires KVM, which is disproportionate here |
| D3 | **Flutter Web is not used** | Three concrete objections: `image_picker` (the core WF3 field-evidence capture path) degrades to a file picker on web; `flutter_secure_storage` falls back to browser storage, contradicting the project's documented rule that refresh credentials live in HttpOnly cookies; and the repository has no `web/` platform folder, so it would add a new surface with no real user |
| D4 | **No TLS in this iteration** | The test server runs on an internal network. `AUTH_SECURE_COOKIES` is set to `false` with an explicit warning to revert under TLS |
| D5 | **Compose stays in the backend repository** | Least disruptive; the workspace root is deliberately not a Git repository, so a root-level Compose file would be unversioned |
| D6 | Build **skips tests** | Testcontainers requires a Docker daemon unavailable inside `docker build`; `./mvnw verify` remains the gate |
| D7 | Frontend image sets **no API URL** | The relative default plus the nginx proxy keeps one image hostname-independent |

## Open questions

None outstanding. All decisions above were confirmed with the product owner on 2026-09-28.
