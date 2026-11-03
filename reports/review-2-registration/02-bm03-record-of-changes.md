---
title: "SWP490 Review 2 - BM03 Record of Changes for Registration Form"
document_type: review2-bm03
version: "2.0"
date: "2026-11-03"
project_code: "GFA26SE139"
group_name: "FA26SE112"
---

# II. BM03 – Record of Changes (Registration Form v1.0 to v2.0)

| Project Code | Project Name | Group | Current Version | Proposed Final Version | Date |
| :---: | --- | :---: | :---: | :---: | :---: |
| `GFA26SE139` | SmartDroneInspection: AI-powered Infrastructure Inspection Management Platform | `FA26SE112` | `1.0 (19/08/2026)` | `2.0 (03/11/2026)` | `2026-11-03` |

## 1. Summary of Scope Conservation &Targeted Refinements
The Registration Form v2.0 **preserves 100% of the approved project name (`3.1`), problem context (`3.2.a`), `SmartDroneHub` consumer integration model, 5 Core Subsystems, 3 focused AI services (`DroneVisionAI`, `LLM Summarization`, `DroneKnowledgeAI`), and 5 Work Packages (`WP1`–`WP5`)**, while updating only the items that evolved during full-stack implementation:
1. **Human Actors (`§3.2.b`)**: Replaced the passive `Viewer` role with the active **`Customer`** role (`CUSTOMER` — manages organization assets and internal engineers, submits service requests, accepts quotations and published reports, settles inspection fees via `PayOS`, and approves/accepts maintenance work orders).
2. **Commercial Request, Contract & Payment Workflow (`§3.2.b`, `§3.2.c`)**: Expanded `Inspection Request Management` to include two-way Order Chat, versioned quotations, signed service contract upload, airspace & 3-document drone registration gates, and online payment settlement via **PayOS (VietQR)**.
3. **SmartDroneHub Video & Interactive Evidence (`§3.2.b`, `§3.2.c`)**: Extended `SmartDroneHub` mission integration to persist telemetry, GPS flight traces, flight reports, and high-resolution `video/mp4` recordings, with interactive video frame cropping and 1-click `YOLO11` video defect detection.
4. **Corrective Maintenance Work Orders & 3-Way Re-inspection (`§3.2.c`)**: Refined `Maintenance Ticket Management` into `Maintenance Work Order Management` with `pgvector` RAG repair scope/cost norms advisory and a 3-way re-inspection defect verification loop (`Prior Defect` vs. `Repair Proof` vs. `Drone Re-capture`).
5. **Backend Technology Stack (`§3.2.d`, `§3.2.e`)**: Updated the backend implementation stack from `ASP.NET Core Web API, Entity Framework Core, SignalR` to **`Java 21, Spring Boot, Spring Modulith, Spring Data JPA / Hibernate, Flyway`**, with REST telemetry polling and Transactional Outbox notifications.

## 2. Detailed Record of Changes Table (BM03)

*Legend: `A` = Added, `M` = Modified, `D` = Deleted*

| No. | Section in Registration | A / M / D | Content in v1.0 (19/08/2026) | Revised Content in v2.0 (03/11/2026) | Reason for Change & Traceability |
| :---: | --- | :---: | --- | --- | --- |
| 01 | `§3.1 Project Name & §3.2.a Context` | — | **Kept 100% unchanged** (`SmartDroneInspection: AI-powered Infrastructure Inspection Management Platform`, `SmartDroneHub` separation of concerns, AiTA Lab hardware note). | **Kept 100% unchanged**. | Original context and `SmartDroneHub` consumer boundary match the implemented architecture (`FE-05`, `FE-06`). |
| 02 | `§3.2.b Human Actors` | `M` | 5 actors: `Administrator`, `Inspection Manager`, `Inspector`, `Maintenance Engineer`, `Viewer`. | 5 actors: `Administrator (Admin)`, `Inspection Manager (Manager)`, `Customer` *(replacing `Viewer`)*, `Inspector`, `Maintenance Engineer`. | Upgraded `Viewer` to active `Customer` to participate in service requests, quotation/report acceptance, PayOS payment, and maintenance budget/completion approval (`SRS §2.1`). |
| 03 | `§3.2.b & §3.2.c Asset, Request & Planning` | `M` | Basic asset management and internal inspection request approval. | Added Vietnam airspace zone check, 3-document Inspector drone registration, Order Chat, versioned quotations, signed contract upload, Flight Permit gate, and `PayOS` online settlement. | Aligns request/planning workflow with commercial B2B inspection service operations (`FE-02`, `FE-03`, `FE-04`, `FE-05`, `FE-06`). |
| 04 | `§3.2.b & §3.2.c Drone Mission & Evidence` | `M` | Retrieve mission status, telemetry, inspection images, and flight reports from `SmartDroneHub`. | Kept `SmartDroneHub` Mission API integration and added GPS flight trace persistence (`V28`), `video/mp4` flight recording sync, interactive video frame cropping, and 1-click `YOLO11` video auto-detection. | Enhances field session evidence intake for high-resolution drone flight videos (`FE-05`, `FE-06`). |
| 05 | `§3.2.c Maintenance & AI Services` | `M` | Maintenance Ticket Management + `DroneVisionAI`, `LLM Summarization`, `DroneKnowledgeAI`. | Kept all 3 AI services (mapped to `YOLO11 + Vision fallback`, `LLM`, and `pgvector RAG`) and refined tickets into Maintenance Work Orders with RAG scope/cost norms and 3-way Re-inspection verification. | Connects confirmed report defects to engineering remediation and post-repair drone verification (`FE-07`, `FE-08`). |
| 06 | `§3.2.d Non-Functional & §3.2.e Technologies` | `M` | Backend: `ASP.NET Core Web API, Entity Framework Core, SignalR`. | Backend: `Java 21, Spring Boot, Spring Modulith, Spring Data JPA / Hibernate, Flyway`; REST telemetry polling & Transactional Outbox notifications instead of `SignalR`. | Standardized backend on Java 21 / Spring Boot Modular Monolith while keeping ReactJS + Material UI, Flutter, PostgreSQL, MinIO, and Docker unchanged (`SDD §1`). |
