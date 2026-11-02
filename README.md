# SmartDroneInspection Documentation

Project documentation for the SmartDroneInspection target: a platform-managed infrastructure inspection and corrective maintenance service.

The target lifecycle covers Customer and asset onboarding, partner Inspector/Drone registry (`MF1`), one-time/recurring service requests, versioned VND/USD quotation requirements, order chat, signed paper contracts and cross-organization occurrence dispatch (`MF2`), inspection evidence/reports and PayOS VietQR (`MF3`), and corrective maintenance (`MF4`). This is requirements scope, not an implementation-completion statement. Report 5 is the dated source for tested coverage; its 02 Nov 2026 audit records V25 Testcontainers verification as Pending.

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

## Roles (5 canonical login roles; descriptions summarize target responsibilities)

- **`ADMIN`** (`ActorZone.PLATFORM`) - platform-scoped technical administration, internal accounts, configuration, and audit responsibilities.
- **`MANAGER`** (`ActorZone.PLATFORM`) - platform-scoped service operations, partner coordination, quote/contract workflow, dispatch, report review, and payout responsibilities. Current persisted quote schema is VND-only; VND/USD remains a target requirement.
- **`CUSTOMER`** (`ActorZone.CUSTOMER_ORGANIZATION`) - customer organization owner/manager: airspace-checked onboarding with initial asset, asset & checkpoint registry, maintenance engineer account provisioning, service requests, quote acceptance, 5-stage inspection progress tracking, published report acceptance, PayOS VietQR payment, maintenance work order creation, budget/Change Order approval, re-inspection requests, and independent maintenance acceptance/closure.
- **`INSPECTOR`** (`ActorZone.INSPECTOR_PARTNER`) - partner Inspector responsibilities in the target, including profile/license, owned-drone records, assigned field sessions, evidence and findings.
- **`MAINTENANCE_ENGINEER`** (`ActorZone.CUSTOMER_ORGANIZATION`) - customer-side repair engineer (`Team Lead`, `Report Author`, `Team Member`): RAG-assisted repair scope planning, 1-click task creation, RAG norm-based cost estimation, Change Order requests, field repair work logs with before/after proof, batch log verification, and auto-drafted maintenance completion reports.

The target authorization model combines role checks with `ActorZone`, organization, ownership/assignment and separation-of-duties. Use Report 5 and executable contracts as evidence of current implementation; role/UI visibility alone does not prove authorization or workflow completion.

## Folder layout

```text
development/             # Git/PR rules and implementation plans
diagrams/                # Canonical Mermaid (.mmd) and Draw.io diagram sources
project-reference/       # Project reference and error-prevention guides
reports/                 # Self-contained formal report folders (Reports 1-5)
tools/                   # Report export and verification tooling
```
