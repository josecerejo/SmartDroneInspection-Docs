#!/usr/bin/env python3
"""Export the official Capstone Project Registration Form Word document using the official FPT University template."""
import sys
from pathlib import Path
import docx
from docx.shared import Pt, Inches

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from export_common import OFFICIAL, REPORTS

TEMPLATE_NAME = "Bản sao của FA26SE112_SMARTDRONEINSPECTION_AI_POWERED_INFRASTR_tripm14.docx"


def export_registration_doc(output_path: Path):
    template_path = Path(OFFICIAL) / TEMPLATE_NAME
    if not template_path.exists():
        raise FileNotFoundError(f"Official template not found at: {template_path}")

    doc = docx.Document(template_path)

    # 1. Keep Student Table (Table 1) exactly aligned with original registration
    student_table = doc.tables[1]
    students_data = [
        ("1", "Trần Hoàng Trung Hiếu", "SE184212", "0963832382", "hieuthtse184212@fpt.edu.vn", "Leader"),
        ("2", "Phùng Trung Quốc", "SE170027", "0896986551", "quocptse170027@fpt.edu.vn", "Member"),
        ("3", "Trương Thái Như", "SE180082", "0328416716", "nhuttse180082@fpt.edu.vn", "Member"),
        ("4", "Trần Tùng Bách", "SE180220", "0378351050", "bachttse180220@fpt.edu.vn", "Member"),
    ]
    for i, s_data in enumerate(students_data, start=1):
        if i < len(student_table.rows):
            row = student_table.rows[i]
            for col_idx, text_val in enumerate(s_data):
                row.cells[col_idx].text = text_val
                for p in row.cells[col_idx].paragraphs:
                    p.paragraph_format.line_spacing = 1.15
                    for run in p.runs:
                        run.font.name = "Times New Roman"
                        run.font.size = Pt(11)

    # 2. Keep original English & Vietnamese project names in 3.1
    for p in doc.paragraphs:
        if "3.1.1. English:" in p.text:
            p.text = "3.1.1. English: SmartDroneInspection: AI-powered Infrastructure Inspection Management Platform"
            p.runs[0].font.name = "Times New Roman"
            p.runs[0].font.size = Pt(12)
        elif "3.1.2. Vietnamese:" in p.text:
            p.text = "3.1.2. Vietnamese: SmartDroneInspection: Nền tảng Quản lý Kiểm tra Hạ tầng bằng Drone tích hợp AI"
            p.runs[0].font.name = "Times New Roman"
            p.runs[0].font.size = Pt(12)

    # 3. Locate the index of paragraph ("a) Context:") and ("4. Other comments")
    idx_context = -1
    idx_other = -1
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if t.startswith("a) Context:"):
            idx_context = i
        elif t.startswith("4. Other comments"):
            idx_other = i

    if idx_context == -1 or idx_other == -1:
        raise ValueError(f"Could not locate context ({idx_context}) or other comments ({idx_other}) in doc")

    for i in range(idx_context, idx_other):
        doc.paragraphs[i].text = ""

    content_sections = [
        ("heading", "a) Context:"),
        ("body", "Infrastructure assets such as buildings, bridges, roads, transmission towers, solar farms, industrial facilities, and telecommunication stations require regular inspections to ensure operational safety and maintenance planning. Traditional inspection processes are often manual, labor-intensive, time-consuming, and potentially hazardous for inspectors."),
        ("body", "The increasing adoption of drones enables organizations to capture high-quality aerial images and videos efficiently. However, many organizations still lack a centralized platform for managing inspection requests, schedules, reports, detected defects, maintenance tickets, and historical inspection records."),
        ("body", "Furthermore, drone operation should be separated from business applications. Drone missions, telemetry, and flight operations should be managed by a common drone platform (SmartDroneHub), while inspection applications should focus on asset management and inspection workflows."),
        ("body", "This project proposes SmartDroneInspection, an AI-powered Infrastructure Inspection Management Platform that manages the complete inspection lifecycle while integrating with SmartDroneHub through standardized APIs for drone mission execution."),
        ("body", "Note: All required hardware components (if any) will be supported and provided by AiTA Lab to facilitate development, testing, and demonstration of the system."),

        ("heading", "b) Proposed Solutions:"),
        ("body", "SmartDroneInspection is designed as a business-oriented inspection management platform rather than a drone control system. The system manages infrastructure assets, inspection service requests, quotations and contracts, inspection planning, reports, defect tracking, and maintenance work orders - while consuming drone operation services from SmartDroneHub through standardized APIs."),
        ("subheading", "Human Actors"),
        ("bullet", "Administrator (Admin) - manages users, organizations, airspace/registration approvals, asset categories, and system configuration."),
        ("bullet", "Inspection Manager (Manager) - reviews service requests, issues quotations and contracts, creates inspection schedules, assigns inspectors and drones, and reviews/publishes reports."),
        ("bullet", "Customer (Customer) - manages organization assets and maintenance staff, submits inspection service requests, accepts quotations and published reports, processes online payments, and approves/accepts maintenance work orders."),
        ("bullet", "Inspector (Inspector) - reviews assigned inspections, uploads flight permits, executes field sessions with SmartDroneHub, uploads photo/video evidence, records and confirms findings, submits reports, and verifies re-inspections."),
        ("bullet", "Maintenance Engineer (Maintenance Engineer) - manages corrective maintenance work orders, updates repair tasks with photo proof, and tracks maintenance completion history."),

        ("subheading", "Five Core Subsystems"),
        ("numbered", "1. Asset & Fleet Management\n"
                     "Manage infrastructure assets, airspace zones, categories, specifications, locations, technical documents, registered inspector drones, lifecycle status, and inspection history."),
        ("numbered", "2. Inspection Planning, Request & Contract Management\n"
                     "Support one-time and recurring inspection service requests, quotation negotiation, signed contract records, inspection scheduling, frequency configuration, priority assignment, and conflict-checked inspector/drone allocation."),
        ("numbered", "3. Drone Mission Integration\n"
                     "Integrate with SmartDroneHub via REST API to create inspection missions, retrieve live telemetry, flight traces, drone images, flight videos (video/mp4), and flight reports. SmartDroneInspection acts as a consumer, not a drone controller."),
        ("numbered", "4. Inspection Report, Defect & Maintenance Management\n"
                     "Manage inspection reports, findings, photo and video evidence, online fee settlement (PayOS), defect classification, severity tracking, repair recommendations, and corrective maintenance work order & re-inspection lifecycle."),
        ("numbered", "5. AI-assisted Services\n"
                     "Three focused AI features integrated within the 15-week project scope:"),
        ("bullet", "Inspection Image & Video Analysis - detect potential defects from drone imagery and flight videos using DroneVisionAI (YOLO11 & Vision LLM fallback)."),
        ("bullet", "Inspection Report Summarization - generate concise executive summaries from inspection reports using an LLM."),
        ("bullet", "Historical Case & Engineering Recommendation - suggest repair scopes, cost norms, and compliance guidelines using DroneKnowledgeAI (pgvector RAG)."),

        ("heading", "c) Functional Requirements:"),
        ("subheading", "User Management"),
        ("bullet", "Authentication, Google OAuth2 login, authorization, 5-role access control (Admin, Manager, Customer, Inspector, Maintenance Engineer)"),
        ("bullet", "User profiles, partner inspector & customer workforce onboarding, audit logs"),

        ("subheading", "Asset Management"),
        ("bullet", "Create/update assets, manage asset categories, inspection checkpoints, and documents"),
        ("bullet", "Airspace zone validation (No-Fly / Restricted Zones), Inspector-owned drone registration (3-document verification), asset history, and lifecycle tracking"),

        ("subheading", "Inspection Planning"),
        ("bullet", "Create inspection plans, schedule one-time and recurring inspections, assign conflict-checked inspectors and drones"),
        ("bullet", "Manage inspection calendars, flight permit pre-flight gate, and inspection notifications"),

        ("subheading", "Inspection Request Management"),
        ("bullet", "Create, approve, track, and cancel inspection service requests"),
        ("bullet", "Order chat negotiation, versioned quotations, signed contract upload, online payment settlement (PayOS), and request history"),

        ("subheading", "Drone Mission Integration"),
        ("bullet", "Create and control inspection missions (Start, Abort, Complete) via SmartDroneHub Mission API"),
        ("bullet", "Retrieve mission status, live telemetry, GPS flight traces, inspection images, flight videos (video/mp4), and flight reports"),

        ("subheading", "Inspection Report Management"),
        ("bullet", "Upload photo and MP4 video evidence (with interactive video frame capture/cropping), record and confirm findings, auto-compile reports"),
        ("bullet", "Manager review, publish reports, and Customer report acceptance"),

        ("subheading", "Defect Management"),
        ("bullet", "Record and classify defects, assign severity"),
        ("bullet", "Track defect lifecycle, attach photo evidence and bounding-box annotations"),

        ("subheading", "Maintenance Work Order Management"),
        ("bullet", "Create and assign maintenance work orders from confirmed report defects, approve repair budgets and change orders"),
        ("bullet", "Update repair progress with before/after photo proof, conduct 3-way re-inspection defect verification, reconcile costs, close work orders, and maintain history"),

        ("subheading", "AI Services Integration"),
        ("bullet", "Inspection image and video defect analysis (DroneVisionAI — YOLO11 & Vision LLM fallback)"),
        ("bullet", "Inspection report summarization and maintenance completion report auto-drafting (LLM)"),
        ("bullet", "Engineering repair scope, cost norms, and compliance recommendation (DroneKnowledgeAI — pgvector RAG)"),

        ("subheading", "Dashboard & Analytics"),
        ("bullet", "Role-based inspection statistics, defect analytics, maintenance KPIs"),
        ("bullet", "Asset utilization, inspection KPIs, operational reports"),

        ("heading", "d) Non-Functional Requirements:"),
        ("bullet", "Responsive Web Application"),
        ("bullet", "Cross-platform Mobile Application (Flutter)"),
        ("bullet", "Modular Monolith & RESTful API Architecture"),
        ("bullet", "JWT Authentication & Google OAuth2"),
        ("bullet", "Role-Based Access Control (RBAC) with Multi-tenant Zone Isolation"),
        ("bullet", "Integration with SmartDroneHub via standardized REST APIs"),
        ("bullet", "PostgreSQL Database with pgvector extension"),
        ("bullet", "MinIO Object Storage for photo/MP4 video evidence and inspection documents"),
        ("bullet", "Docker Containerization, Cloud-ready Deployment"),
        ("bullet", "Real-time telemetry polling and asynchronous Transactional Outbox notifications"),
        ("bullet", "Online Payment Gateway integration (PayOS VietQR with HMAC-SHA256 webhook verification)"),
        ("bullet", "Audit Logging, Secure File Storage, Scalable and High Availability Architecture"),

        ("heading", "e) Theory & Practical:"),
        ("subheading", "Applied Theory"),
        ("bullet", "Software Engineering: SDLC, Object-Oriented Analysis and Design, Modular Monolith Software Architecture"),
        ("bullet", "Business Process Modeling, Workflow Management, Relational & Vector Database Design"),
        ("bullet", "RESTful API Design, External System Integration (SmartDroneHub, PayOS, OAuth2)"),
        ("bullet", "Mobile Computing, Asynchronous Event-Driven Notification & Telemetry Integration"),
        ("bullet", "AI Integration: Computer Vision (YOLO11), LLM-based summarization, and Retrieval-Augmented Generation (RAG)"),
        ("bullet", "Software Testing, Automated Verification, Cloud Deployment"),

        ("subheading", "Technologies"),
        ("bullet", "Backend: Java 21, Spring Boot, Spring Modulith, Spring Security, Spring Data JPA / Hibernate, Flyway"),
        ("bullet", "Frontend: ReactJS (React 19, TypeScript), Material UI"),
        ("bullet", "Mobile: Flutter (Dart, Riverpod, GoRouter, Dio)"),
        ("bullet", "Database: PostgreSQL 17 (with pgvector)"),
        ("bullet", "Storage: MinIO Object Storage"),
        ("bullet", "AI: DroneVisionAI (Python FastAPI, YOLO11 & Vision LLM fallback), DroneKnowledgeAI (pgvector RAG), LLM-based summarization"),
        ("bullet", "Payment & Auth: PayOS (VietQR), Google OAuth2"),
        ("bullet", "Deployment: Docker, Docker Compose, GitHub Actions CI/CD, Cloud Deployment"),

        ("heading", "f) Products (Expected Deliverables):"),
        ("bullet", "SmartDroneInspection Web Portal (ReactJS + Material UI)"),
        ("bullet", "Flutter Mobile Application (Inspector + Maintenance Engineer)"),
        ("bullet", "Asset & Drone Fleet Management Module"),
        ("bullet", "Inspection Planning & Airspace Gate Module"),
        ("bullet", "Inspection Service Request, Quotation, Contract & PayOS Payment Module"),
        ("bullet", "Drone Mission Integration Module (SmartDroneHub API)"),
        ("bullet", "Inspection Report & Evidence Module"),
        ("bullet", "Defect Management Module"),
        ("bullet", "Corrective Maintenance Work Order & 3-Way Re-inspection Module"),
        ("bullet", "AI Services: Image & Video Analysis (YOLO11), Report Summarization (LLM), Engineering & Case Recommendation (pgvector RAG)"),
        ("bullet", "Dashboard & Analytics"),
        ("bullet", "RESTful APIs"),
        ("bullet", "Docker Deployment Package"),
        ("bullet", "Software Documentation (Reports 1–5)"),

        ("heading", "g) Proposed Tasks:"),
        ("subheading", "Work Package 1 - Requirement Analysis & System Design"),
        ("bullet", "Requirement analysis, business workflow analysis (MF1–MF4, FE-01–FE-08)"),
        ("bullet", "Software architecture design (Spring Modulith), PostgreSQL & pgvector database design"),
        ("bullet", "REST API specification, UI/UX design"),

        ("subheading", "Work Package 2 - Asset, Fleet & Inspection Planning"),
        ("bullet", "User management, 5-role RBAC, partner/customer onboarding, and airspace zone validation"),
        ("bullet", "Asset management and Inspector-owned drone registry module"),
        ("bullet", "Service request, quotation, contract management, inspection scheduling, and notification services"),

        ("subheading", "Work Package 3 - Mission Integration, Report & Maintenance Management"),
        ("bullet", "Flight permit pre-flight gate and SmartDroneHub Mission API integration (telemetry, flight trace, MP4 video & flight report)"),
        ("bullet", "Inspection report management, defect management, and PayOS online payment settlement"),
        ("bullet", "Corrective maintenance work order management, 3-way re-inspection verification, and dashboard"),

        ("subheading", "Work Package 4 - Mobile Application & AI Integration"),
        ("bullet", "Flutter mobile application (Inspector + Maintenance Engineer)"),
        ("bullet", "Photo and MP4 video evidence management (with interactive frame capture/cropping)"),
        ("bullet", "AI services: image & video defect analysis (YOLO11), report summarization (LLM), engineering & case recommendation (pgvector RAG)"),

        ("subheading", "Work Package 5 - Testing & Deployment"),
        ("bullet", "Unit testing, system integration testing, performance testing, security testing"),
        ("bullet", "Docker containerization and cloud staging deployment"),
        ("bullet", "Software documentation (Reports 1–5), deployment guide"),
    ]

    ref_p = doc.paragraphs[idx_other]

    for kind, text in content_sections:
        new_p = ref_p.insert_paragraph_before()
        new_p.paragraph_format.line_spacing = 1.15
        new_p.paragraph_format.space_after = Pt(4)

        if kind == "heading":
            new_p.paragraph_format.space_before = Pt(8)
            new_p.paragraph_format.space_after = Pt(4)
            run = new_p.add_run(text)
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
        elif kind == "subheading":
            new_p.paragraph_format.space_before = Pt(4)
            new_p.paragraph_format.space_after = Pt(2)
            run = new_p.add_run(text)
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)
        elif kind == "bullet":
            new_p.paragraph_format.left_indent = Inches(0.25)
            run = new_p.add_run("● " + text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)
        elif kind == "numbered":
            new_p.paragraph_format.left_indent = Inches(0.2)
            run = new_p.add_run(text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)
        else:
            run = new_p.add_run(text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
    print(f"Successfully exported registration document to: {output_path}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    out_dir = REPORTS / "generated" / "registration"
    out_file = out_dir / "FA26SE112_SMARTDRONEINSPECTION_AI_POWERED_INFRASTR_tripm14.docx"
    export_registration_doc(out_file)

    pack_dir = REPORTS / "generated" / "review-2-pack"
    pack_file = pack_dir / "FA26SE112_Registration_Form.docx"
    export_registration_doc(pack_file)


if __name__ == "__main__":
    main()
