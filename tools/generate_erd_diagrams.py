#!/usr/bin/env python3
"""Generate the Full 34-Table Mermaid ERD (V1-V17 Platform Inspection Service schema)
with standard SQL data types (uuid, varchar, timestamptz, boolean, etc.), PK, and FK.
Compatible with Mermaid 11 and Draw.io."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
ERD_OUT_DIR = ROOT / "diagrams" / "erd"
REPORT4_DB_MD = ROOT / "reports" / "report-4-software-design-document" / "02-database-design.md"


def extract_report4_erd(md_path: Path = REPORT4_DB_MD) -> str:
    txt = md_path.read_text(encoding="utf-8")
    marker = "%% title: Database Entity Relationship Diagram (ERD)"
    idx = txt.find(marker)
    if idx == -1:
        raise ValueError(f"ERD marker not found in {md_path}")
    end_fence = txt.find("```", idx)
    return txt[idx:end_fence].strip()


def build_renderer_html(code: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>body {{ margin: 0; padding: 16px; background: #fff; display: inline-block; }}</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
</head>
<body>
<div id="c"></div>
<script>
const code = {json.dumps(code)};
mermaid.initialize({{
  startOnLoad: false,
  theme: 'default',
  securityLevel: 'loose',
  maxTextSize: 500000,
  er: {{ useMaxWidth: false }}
}});
mermaid.render('erd_svg', code).then(({{ svg }}) => {{
  document.getElementById('c').innerHTML = svg;
  const svgEl = document.querySelector('#c svg');
  const cols = [
    ['organizations', 'users', 'auth_sessions', 'prospective_customer_registrations', 'inspector_partner_applications', 'contract_partner_inspectors'],
    ['drone_registration_applications', 'contract_partner_drones', 'drones', 'asset_categories', 'assets', 'asset_documents'],
    ['service_requests', 'service_request_messages', 'service_request_quotes', 'service_request_occurrences', 'inspection_finance_settings'],
    ['recurring_inspection_schedules', 'schedule_occurrences', 'inspections', 'field_sessions', 'evidence', 'findings'],
    ['inspection_reports', 'reinspection_defect_verifications', 'maintenance_work_orders', 'maintenance_team_members', 'maintenance_tasks', 'maintenance_estimate_versions'],
    ['maintenance_cost_lines', 'maintenance_change_orders', 'maintenance_work_logs', 'maintenance_reports', 'maintenance_acceptance_decisions', 'repair_knowledge_chunks', 'notifications', 'audit_events', 'event_publication'],
  ];
  const nodeMap = {{}};
  svgEl.querySelectorAll('g.node').forEach(n => {{
    const id = n.id || '';
    const m = id.match(/entity-([a-z0-9_]+)-\\d+$/);
    if (m) {{
      const outer = n.querySelector('g.outer-path path');
      const d = outer ? outer.getAttribute('d') : '';
      const dm = d.match(/^M([-\\d.]+)\\s+([-\\d.]+)\\s+L([-\\d.]+)\\s+([-\\d.]+)\\s+L([-\\d.]+)\\s+([-\\d.]+)/);
      const w = dm ? Math.abs(parseFloat(dm[3]) - parseFloat(dm[1])) : 320;
      const h = dm ? Math.abs(parseFloat(dm[6]) - parseFloat(dm[2])) : 200;
      nodeMap[m[1]] = {{ el: n, w, h }};
    }}
  }});
  let curX = 32, colGap = 56, rowGap = 32, maxH = 0;
  cols.forEach((colTables, cIdx) => {{
    const colW = Math.max(...colTables.map(t => nodeMap[t] ? nodeMap[t].w : 300));
    let curY = 32;
    colTables.forEach((t, rIdx) => {{
      const info = nodeMap[t];
      if (!info) return;
      const cx = curX + colW / 2, cy = curY + info.h / 2;
      Object.assign(info, {{ cx, cy, col: cIdx, row: rIdx, left: cx - info.w / 2, right: cx + info.w / 2, top: cy - info.h / 2, bottom: cy + info.h / 2 }});
      info.el.setAttribute('transform', 'translate(' + cx + ', ' + cy + ')');
      curY += info.h + rowGap;
    }});
    if (curY > maxH) maxH = curY;
    curX += colW + colGap;
  }});
  const totalW = Math.ceil(curX - colGap + 32), totalH = Math.ceil(maxH + 16);
  const edgeLabels = svgEl.querySelectorAll('g.edgeLabels g.edgeLabel');
  svgEl.querySelectorAll('g.edgePaths path.relationshipLine').forEach((p, idx) => {{
    const did = p.getAttribute('data-id') || p.id || '';
    const m = did.match(/entity-([a-z0-9_]+)-\\d+_entity-([a-z0-9_]+)-\\d+/);
    if (m && nodeMap[m[1]] && nodeMap[m[2]]) {{
      const a = nodeMap[m[1]], b = nodeMap[m[2]], offset = ((idx % 7) - 3) * 5;
      if (a.col === b.col) {{
        const x1 = a.cx + offset, x2 = b.cx + offset;
        const y1 = a.cy < b.cy ? a.bottom : a.top, y2 = a.cy < b.cy ? b.top : b.bottom;
        p.setAttribute('d', 'M' + x1 + ',' + y1 + ' L' + x2 + ',' + y2);
        if (edgeLabels[idx]) {{
          if (Math.abs(a.row - b.row) === 1) edgeLabels[idx].setAttribute('transform', 'translate(' + ((x1+x2)/2) + ', ' + ((y1+y2)/2) + ')');
          else edgeLabels[idx].style.display = 'none';
        }}
      }} else {{
        const dir = a.cx < b.cx ? 1 : -1;
        const x1 = dir > 0 ? a.right : a.left, y1 = a.cy + offset;
        const x2 = dir > 0 ? b.left : b.right, y2 = b.cy + offset;
        const mx = x1 + dir * (colGap / 2) + offset;
        p.setAttribute('d', 'M' + x1 + ',' + y1 + ' L' + mx + ',' + y1 + ' L' + mx + ',' + y2 + ' L' + x2 + ',' + y2);
        if (edgeLabels[idx]) edgeLabels[idx].style.display = 'none';
      }}
    }}
  }});
  svgEl.setAttribute('width', String(totalW));
  svgEl.setAttribute('height', String(totalH));
  svgEl.setAttribute('viewBox', '0 0 ' + totalW + ' ' + totalH);
  document.body.setAttribute('data-ready', '1');
}});
</script>
</body>
</html>"""


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    code = extract_report4_erd()
    digest = hashlib.sha256(code.encode("utf-8")).hexdigest()[:12]
    ERD_OUT_DIR.mkdir(parents=True, exist_ok=True)
    mmd_out = ERD_OUT_DIR / "full_database_erd_31_tables.mmd"
    mmd_out.write_text(code + "\n", encoding="utf-8")

    html_out = ERD_OUT_DIR / "render_mermaid_erd.html"
    html_out.write_text(build_renderer_html(code), encoding="utf-8")
    print(f"Updated {mmd_out.name} ({digest}) and wrote {html_out}")


if __name__ == "__main__":
    main()
