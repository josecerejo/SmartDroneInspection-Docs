#!/usr/bin/env python3
"""Build self-contained HTML files (with embedded PNG diagrams & university styles) for Chromium PDF export."""
from __future__ import annotations

import base64
import html
import json
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from export_common import REPORTS, project_metadata
import export_report1
import export_report2
import export_report3
import export_report4
import export_report5_doc
from report_ooxml import parse_markdown, plain, sha256

CSS = """
@page { size: A4; margin: 20mm 18mm 20mm 18mm; }
body { font-family: 'Calibri', 'Segoe UI', Arial, sans-serif; font-size: 11pt; line-height: 1.45; color: #111827; margin: 0; }
.cover { text-align: center; padding: 36px 0 28px 0; border-bottom: 2px solid #C00000; margin-bottom: 24px; }
.cover-uni { font-size: 13pt; font-weight: bold; letter-spacing: 0.08em; color: #1F4D78; margin-bottom: 8px; }
.cover-type { font-size: 18pt; font-weight: bold; color: #C00000; margin: 6px 0; }
.cover-title { font-size: 20pt; font-weight: bold; color: #C00000; margin: 10px 0; }
.cover-project { font-size: 13pt; font-weight: bold; color: #111827; margin: 8px 0; }
.cover-loc { font-size: 11pt; font-style: italic; color: #374151; margin-top: 10px; }
h1 { font-family: 'Calibri Light', 'Calibri', sans-serif; font-size: 16pt; font-weight: bold; color: #C00000; margin: 22px 0 8px 0; page-break-after: avoid; }
h2 { font-family: 'Calibri Light', 'Calibri', sans-serif; font-size: 13pt; font-weight: bold; color: #111827; margin: 18px 0 6px 0; page-break-after: avoid; }
h3 { font-family: 'Calibri Light', 'Calibri', sans-serif; font-size: 12pt; font-weight: bold; color: #1F4D78; margin: 14px 0 6px 0; page-break-after: avoid; }
h4 { font-family: 'Calibri Light', 'Calibri', sans-serif; font-size: 11pt; font-weight: bold; font-style: italic; color: #111827; margin: 12px 0 4px 0; page-break-after: avoid; }
p { margin: 6px 0; text-align: justify; }
ul { margin: 4px 0 8px 22px; padding: 0; }
li { margin: 3px 0; }
table { width: 100%; border-collapse: collapse; margin: 10px 0 14px 0; font-size: 9.5pt; page-break-inside: auto; }
tr { page-break-inside: avoid; page-break-after: auto; }
th { background-color: #FFE8E1; color: #6E2500; font-family: 'Tahoma', 'Calibri', sans-serif; font-weight: bold; border: 1px solid #4b5563; padding: 6px 7px; text-align: left; vertical-align: top; }
td { border: 1px solid #6b7280; padding: 5px 7px; vertical-align: top; word-break: break-word; }
.diagram { text-align: center; margin: 14px 0; page-break-inside: avoid; }
.diagram img { max-width: 100%; max-height: 210mm; height: auto; border: 1px solid #d1d5db; border-radius: 4px; }
.caption { font-size: 9.5pt; font-weight: bold; color: #44546A; text-align: center; margin-top: 5px; }
pre { background: #f8fafc; border: 1px solid #cbd5e1; padding: 8px 10px; font-size: 9pt; white-space: pre-wrap; word-break: break-word; border-radius: 4px; }
code { font-family: 'Consolas', monospace; font-size: 9.5pt; background: #f1f5f9; padding: 1px 4px; border-radius: 3px; }
"""


def format_inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"&lt;br\s*/?&gt;", "<br/>", escaped, flags=re.I)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    return escaped


def blocks_to_html(blocks, report_title: str, metadata: dict, compact_brief: bool = False) -> str:
    css = CSS
    if compact_brief:
        css += "\n@page { size: A4; margin: 10mm 12mm 10mm 12mm; }\nbody { font-size: 8.4pt; line-height: 1.18; }\np, li { margin: 1.5px 0; }\nul { margin: 1.5px 0 3px 16px; }\ntable { font-size: 7.5pt; margin: 3px 0 5px 0; }\nth, td { padding: 2px 3.5px; }\nh1 { font-size: 11.5pt; margin: 4px 0 2px 0; }\nh2 { font-size: 9.8pt; margin: 4px 0 1.5px 0; }\nh3 { font-size: 9pt; margin: 3px 0 1.5px 0; }\n.page-break { page-break-before: always; }\n"
    out = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'/>",
        f"<title>{html.escape(report_title)}</title>",
        f"<style>{css}</style></head><body>",
    ]
    if not compact_brief:
        out.append(
            f"<div class='cover'>"
            f"<div class='cover-uni'>FPT UNIVERSITY – SWP490 CAPSTONE PROJECT</div>"
            f"<div class='cover-type'>CAPSTONE PROJECT REPORT</div>"
            f"<div class='cover-title'>{html.escape(report_title)}</div>"
            f"<div class='cover-project'>{html.escape(metadata['project'])} (Code: {html.escape(metadata['code'])} | Group: {html.escape(metadata['group'])})</div>"
            f"<div class='cover-loc'>{html.escape(metadata['location'])}</div>"
            f"</div>"
        )
    in_list = False
    for b in blocks:
        if b.kind != "list" and in_list:
            out.append("</ul>")
            in_list = False
        if b.kind == "heading":
            lvl = min(max(b.level, 1), 4)
            if compact_brief and lvl == 1 and "Appendix A" in b.text:
                out.append("<div class='page-break'></div>")
            out.append(f"<h{lvl}>{format_inline(b.text)}</h{lvl}>")
        elif b.kind == "paragraph":
            if b.text.strip() == "---":
                continue
            out.append(f"<p>{format_inline(b.text)}</p>")
        elif b.kind == "list":
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{format_inline(b.text)}</li>")
        elif b.kind == "table" and b.rows:
            out.append("<table><thead><tr>")
            for cell in b.rows[0]:
                out.append(f"<th>{format_inline(cell)}</th>")
            out.append("</tr></thead><tbody>")
            for row in b.rows[1:]:
                out.append("<tr>")
                for cell in row:
                    out.append(f"<td>{format_inline(cell)}</td>")
                out.append("</tr>")
            out.append("</tbody></table>")
        elif b.kind == "image" and b.source:
            img_path = b.source.parent / b.text
            if img_path.is_file():
                b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
                out.append(f"<div class='diagram'><img src='data:image/png;base64,{b64}'/><div class='caption'>{html.escape(b.language)}</div></div>")
        elif b.kind == "code":
            if b.language == "mermaid":
                title = "System Diagram"
                m = re.search(r"%%\s*title:\s*(.+)$", b.text, re.M | re.I)
                if m:
                    title = m.group(1).strip()
                digest = sha256(b.text.strip().encode("utf-8"))[:12]
                png_path = (b.source.parent / "assets" / "mermaid" / f"{digest}.png") if b.source else None
                if png_path and png_path.is_file():
                    b64 = base64.b64encode(png_path.read_bytes()).decode("ascii")
                    out.append(f"<div class='diagram'><img src='data:image/png;base64,{b64}'/><div class='caption'>Figure: {html.escape(title)}</div></div>")
            else:
                out.append(f"<pre>{html.escape(b.text)}</pre>")
    if in_list:
        out.append("</ul>")
    out.append("</body></html>")
    return "\n".join(out)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sub_dir = REPORTS / "generated" / "review-2-submission"
    pdf_dir = sub_dir / "pdf-submission"
    html_dir = sub_dir / "html-staging"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    html_dir.mkdir(parents=True, exist_ok=True)
    metadata = project_metadata(REPORTS)

    jobs = [
        ("SWP490_GFA26SE139_R2_Registration.pdf", "Registration Form (v2.0) & BM03 Record of Changes", False, [
            "review-2-registration/01-registration-form.md",
            "review-2-registration/02-bm03-record-of-changes.md",
        ]),
        ("SWP490_GFA26SE139_R2_Report1.pdf", "Report 1 – Project Introduction", False, export_report1.SOURCES),
        ("SWP490_GFA26SE139_R2_Report2.pdf", "Report 2 – Project Management Plan", False, export_report2.SOURCES),
        ("SWP490_GFA26SE139_R2_Report3.pdf", "Report 3 – Software Requirement Specification", False, export_report3.SOURCES),
        ("SWP490_GFA26SE139_R2_Report4.pdf", "Report 4 – Software Design Document", False, export_report4.SOURCES),
        ("SWP490_GFA26SE139_R2_Report5.pdf", "Report 5 – Software Test Documentation & Test Report (65 Cases)", False, list(export_report5_doc.SOURCES) + [
            "report-5-test-report/02-test-statistics/test-statistics.md",
            "report-5-test-report/01-test-cases/test-case-list.md",
            "report-5-test-report/03-features/fe-01-authentication-access-control.md",
            "report-5-test-report/03-features/fe-02-workforce-subscription-management.md",
            "report-5-test-report/03-features/fe-03-asset-drone-fleet-management.md",
            "report-5-test-report/03-features/fe-04-recurring-schedule-notifications.md",
            "report-5-test-report/03-features/fe-05-mission-dispatch-airspace-advisory.md",
            "report-5-test-report/03-features/fe-06-flight-readiness-field-execution.md",
            "report-5-test-report/03-features/fe-07-operational-dashboard-schedule-calendar.md",
            "report-5-test-report/03-features/fe-08-evidence-ai-defect-detection.md",
        ]),
        ("SWP490_GFA26SE139_R2_Report5_TestDocumentation.pdf", "Report 5 – Software Test Documentation", False, export_report5_doc.SOURCES),
        ("SWP490_GFA26SE139_R2_Report5_TestReport.pdf", "Report 5 – Software Test Report Workbook (65 Cases)", False, [
            "report-5-test-report/00-cover/cover.md",
            "report-5-test-report/02-test-statistics/test-statistics.md",
            "report-5-test-report/01-test-cases/test-case-list.md",
            "report-5-test-report/03-features/fe-01-authentication-access-control.md",
            "report-5-test-report/03-features/fe-02-workforce-subscription-management.md",
            "report-5-test-report/03-features/fe-03-asset-drone-fleet-management.md",
            "report-5-test-report/03-features/fe-04-recurring-schedule-notifications.md",
            "report-5-test-report/03-features/fe-05-mission-dispatch-airspace-advisory.md",
            "report-5-test-report/03-features/fe-06-flight-readiness-field-execution.md",
            "report-5-test-report/03-features/fe-07-operational-dashboard-schedule-calendar.md",
            "report-5-test-report/03-features/fe-08-evidence-ai-defect-detection.md",
        ]),
        ("SWP490_GFA26SE139_R2_ProjectTracking.pdf", "Report 3 – Project Tracking (WBS, Issues, Defects, Q&A)", False, [
            "project-tracking/project-tracking.md",
        ]),
        ("SWP490_GFA26SE139_R2_SelfReview.pdf", "BM02 – SRS/SDD Self-Review Report", False, [
            "review-2-self-review/01-bm02-self-review-report.md",
        ]),
        ("SWP490_GFA26SE139_R2_DesignBrief.pdf", "BM01 – Design Brief & Appendix A", True, [
            "review-2-design-brief/01-bm01-design-brief.md",
            "review-2-design-brief/02-appendix-a-and-bm04-commitment.md",
        ]),
        ("SWP490_GFA26SE139_R2_Commitment.pdf", "BM04 – Review 2 Commitment", False, [
            "review-2-registration/01-registration-form.md",
            "review-2-design-brief/01-bm01-design-brief.md",
            "review-2-design-brief/02-appendix-a-and-bm04-commitment.md",
        ]),
    ]

    manifest = []
    for pdf_name, title, compact, rel_sources in jobs:
        blocks = []
        for rel in rel_sources:
            blocks.extend(parse_markdown(REPORTS / rel, strict_tables=False))
        html_str = blocks_to_html(blocks, title, metadata, compact_brief=compact)
        html_path = html_dir / (Path(pdf_name).stem + ".html")
        pdf_path = pdf_dir / pdf_name
        html_path.write_text(html_str, encoding="utf-8")
        manifest.append({
            "pdf_name": pdf_name,
            "html_url": "file:///" + str(html_path.resolve()).replace("\\", "/"),
            "pdf_path": str(pdf_path.resolve()).replace("\\", "/"),
        })
    (html_dir / "pdf_jobs.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Prepared {len(manifest)} HTML files for PDF export in {html_dir}")


if __name__ == "__main__":
    main()
