---
title: "SmartDroneInspection Documentation"
type: "docs"
---

# SmartDroneInspection

SmartDroneInspection is a platform-managed infrastructure inspection and corrective maintenance service platform covering the complete lifecycle (`MF1`–`MF4`) across 8 product features (`FE-01`–`FE-08`).

## Architecture at a glance

- Java 21 and Spring Boot 4.1 modular monolith with Spring Modulith.
- PostgreSQL 17 (`pgvector`) is the source of truth; MinIO stores inspection evidence (photos & MP4 videos), permits, signed contracts, and immutable PDF reports.
- React 19 web portal (`/admin`, `/client`, `/operations`) and Flutter mobile app share the versioned REST API and Google OAuth2 / JWT authentication.
- Online VietQR settlement via PayOS after Customer report acceptance.
- Authorization combines 5-role checks (`ADMIN`, `MANAGER`, `CUSTOMER`, `INSPECTOR`, `MAINTENANCE_ENGINEER`) with `ActorZone`, organization, assignment, and separation-of-duties scope.

## Roles

- `ADMIN` (Platform Admin — `ActorZone.PLATFORM`)
- `MANAGER` (Platform Manager — `ActorZone.PLATFORM`)
- `CUSTOMER` (Customer Organization Owner/Manager — `ActorZone.CUSTOMER_ORGANIZATION`)
- `INSPECTOR` (Partner Drone Inspector — `ActorZone.INSPECTOR_PARTNER`)
- `MAINTENANCE_ENGINEER` (Customer Maintenance Engineer — `ActorZone.CUSTOMER_ORGANIZATION`)

## Documentation map

- [Project reference](project-reference/): workflows, error-prevention checks, and mainflow references.
- [Mainflows & 5-Role Architecture](bao-cao-thay-doi-mainflows-5-roles.md): synchronized 5-role & 8-feature (`FE-01`–`FE-08`) reference across `MF1`–`MF4`.
- [Diagram assignments](phan-cong-ve-so-do.md): 35-diagram ownership map across the 8 features.
- [Formal reports](reports/):
  - [Report 1 — Project Introduction](reports/report-1-project-introduction/)
  - [Report 2 — Project Management Plan](reports/report-2-project-management-plan/)
  - [Report 3 — Software Requirement Specification (SRS)](reports/report-3-software-requirement-specification/)
  - [Report 4 — Software Design Document (SDD)](reports/report-4-software-design-document/)
  - [Report 5 — Software Test Report](reports/report-5-test-report/)
- [Development guide](development/): Git/PR rules and implementation plans.
- [Export & verification tools](tools/): Python OOXML exporters and verification suites.

Repository-specific setup commands are maintained in the `README.md` and `AGENTS.md` files of the backend, frontend, and mobile repositories.
