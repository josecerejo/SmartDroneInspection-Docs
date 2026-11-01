# SmartDroneInspection Documentation

Documentation for the SmartDroneInspection platform-managed infrastructure inspection and corrective maintenance service platform.

SmartDroneInspection connects customer asset registration (with no-fly zone guards) and partner inspector/drone onboarding (`MF1`), service requests, VND/USD quotations, order chat, offline paper contracts, and cross-organization mission dispatch (`MF2`), flight permits, on-site field sessions, photo/MP4 video evidence, YOLO11 defect detection, auto-compiled reporting with AI executive summaries, manager publication, and PayOS VietQR settlement (`MF3`), and pgvector RAG-assisted maintenance work orders, 3-way re-inspection defect verification, and cost reconciliation (`MF4`).

## Start here

- [Documentation home](_index.md) - the current documentation map.
- [5-Role & 8-Feature Mainflows Reference](bao-cao-thay-doi-mainflows-5-roles.md) - complete `MF1`–`MF4` and `FE-01`–`FE-08` reference.
- [Project reference](project-reference/) - error-prevention and reference guides.
- [Reports](reports/) - formal project deliverables (Reports 1–5), including [Report 3 SRS](reports/report-3-software-requirement-specification/), [Report 4 SDD](reports/report-4-software-design-document/), and [Report 5 Test Report](reports/report-5-test-report/).
- [Development guide](development/) - Git/pull-request rules and feature plans.
- [Tools](tools/) - Office report exporters and automated test suites.

Repository-specific setup commands and architecture rules are documented in the `AGENTS.md` and `README.md` files of `SmartDroneInspection-backend/`, `SmartDroneInspection-frontend/`, and `SmartDroneInspection-mobile/`.

## Repositories

| Repository | Stack | Scope |
| --- | --- | --- |
| `SmartDroneInspection-backend/` | Java 21, Spring Boot 4.1, Spring Modulith, PostgreSQL 17 (`pgvector`), MinIO | Modular monolith API, 5-role RBAC, contracts & PayOS, inspections, maintenance, and AI/RAG adapters |
| `SmartDroneInspection-frontend/` | React 19, strict TypeScript, Vite, Material UI | Web portals (`/admin`, `/client`, `/operations`) for platform management, customer service orders, and field/maintenance operations |
| `SmartDroneInspection-mobile/` | Flutter, Dart, Riverpod, GoRouter, Dio | Field workflows for partner inspectors and maintenance engineers (Google OAuth2 deep-link, streaming photo/MP4 evidence upload) |
| `SmartDroneInspection-docs/` | Markdown, Hugo, Python OOXML tools | Formal project reports (Reports 1–5), Mermaid diagrams, and export verification tooling |

## Current roles (5 canonical login roles)

- **`ADMIN`** (`ActorZone.PLATFORM`) - platform technical administration, internal accounts, standard asset categories, airspace/partner/drone onboarding review queues, finance settings, and audit logs.
- **`MANAGER`** (`ActorZone.PLATFORM`) - platform service & partner operations: partner inspector and drone review, service request negotiation/chat, VND/USD quote issuance, signed paper contract upload, cross-org partner dispatch, abort reschedule/reassignment, independent inspection report review/publication, and partner payout recording.
- **`CUSTOMER`** (`ActorZone.CUSTOMER_ORGANIZATION`) - customer organization owner/manager: airspace-checked onboarding with initial asset, asset & checkpoint registry, maintenance engineer account provisioning, service requests, quote acceptance, 5-stage inspection progress tracking, published report acceptance, PayOS VietQR payment, maintenance work order creation, budget/Change Order approval, re-inspection requests, and independent maintenance acceptance/closure.
- **`INSPECTOR`** (`ActorZone.INSPECTOR_PARTNER`) - third-party partner pilot: partner application with pilot license (drone optional at signup), inspector-owned drone registration (registration, ownership, and inspection documents), mission flight permit upload, field session execution (`Start`, `Complete`, `Abort`), photo/MP4 evidence upload, YOLO11/manual finding confirmation, auto-compiled report submission, and 3-way re-inspection defect verification.
- **`MAINTENANCE_ENGINEER`** (`ActorZone.CUSTOMER_ORGANIZATION`) - customer-side repair engineer (`Team Lead`, `Report Author`, `Team Member`): RAG-assisted repair scope planning, 1-click task creation, RAG norm-based cost estimation, Change Order requests, field repair work logs with before/after proof, batch log verification, and auto-drafted maintenance completion reports.

The platform uses deny-by-default authorization. Resource ownership, `ActorZone`, organization scope, partner assignment scope, and separation-of-duties are enforced in backend application services in addition to role checks.

## Folder layout

```text
development/             # Git/PR rules and implementation plans
diagrams/                # Canonical Mermaid (.mmd) and Draw.io diagram sources
project-reference/       # Project reference and error-prevention guides
reports/                 # Self-contained formal report folders (Reports 1-5)
tools/                   # Report export and verification tooling
```
