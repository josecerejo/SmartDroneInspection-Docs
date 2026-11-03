"""Read Markdown and fill original Office packages without recreating styles.

Only Python's standard library is required. Unchanged ZIP members are copied
verbatim; content elements inherit properties from the official template.
"""
from __future__ import annotations

import copy
import hashlib
import html
import math
import re
import struct
from dataclasses import dataclass
from pathlib import Path
from xml.dom import Node, minidom
from zipfile import ZipFile

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_R = "http://schemas.openxmlformats.org/package/2006/relationships"
XML = "http://www.w3.org/XML/1998/namespace"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def children(node, local=None):
    return [n for n in node.childNodes if n.nodeType == Node.ELEMENT_NODE
            and (local is None or n.localName == local)]


def descendants(node, local):
    return [n for n in node.getElementsByTagName("*") if n.localName == local]


def text_of(node):
    return "".join(n.data for n in node.childNodes if n.nodeType == Node.TEXT_NODE)


def element(doc, ns, tag, attrs=None):
    node = doc.createElementNS(ns, tag)
    for key, value in (attrs or {}).items():
        if key.startswith("w:"):
            node.setAttributeNS(W, key, str(value))
        elif key.startswith("r:"):
            node.setAttributeNS(R, key, str(value))
        else:
            node.setAttribute(key, str(value))
    return node


def remove_children(node, keep=()):
    for child in list(node.childNodes):
        if child.nodeType != Node.ELEMENT_NODE or child.localName not in keep:
            node.removeChild(child)


class Package:
    def __init__(self, path: Path):
        self.path = path
        self.original_hash = sha256(path.read_bytes())
        with ZipFile(path) as archive:
            self.entries = archive.infolist()
            self.parts = {info.filename: archive.read(info.filename) for info in self.entries}
            self.comment = archive.comment
        self.original = self.parts.copy()

    def xml(self, name):
        return minidom.parseString(self.parts[name])

    def set_xml(self, name, doc):
        self.parts[name] = doc.toxml(encoding="UTF-8")

    def save(self, path):
        if path.exists():
            raise ValueError(f"Refusing to overwrite existing output: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(path, "w") as archive:
            archive.comment = self.comment
            for info in self.entries:
                if info.filename in self.parts:
                    archive.writestr(copy.copy(info), self.parts[info.filename])
            known = {info.filename for info in self.entries}
            for name in sorted(self.parts.keys() - known):
                archive.writestr(name, self.parts[name])

    def audit(self, allowed):
        changed = [name for name in self.original
                   if self.parts.get(name) != self.original[name]]
        unexpected = set(changed) - set(allowed)
        if unexpected:
            raise ValueError(f"Unexpected package changes: {sorted(unexpected)}")
        for name, data in self.parts.items():
            if name.endswith((".xml", ".rels")):
                minidom.parseString(data)
        return {
            "template_sha256": self.original_hash,
            "unchanged_parts": len(self.original) - len(changed),
            "changed_parts": changed,
            "added_parts": sorted(self.parts.keys() - self.original.keys()),
            "removed_parts": sorted(self.original.keys() - self.parts.keys()),
            "format_parts_preserved": not unexpected,
        }


@dataclass
class Block:
    kind: str
    text: str = ""
    level: int = 0
    rows: list[list[str]] | None = None
    language: str = ""
    source: Path | None = None


def split_row(line):
    line = line.strip()[1:-1] if line.strip().endswith("|") else line.strip()[1:]
    cells, buf = [], []
    i = 0
    while i < len(line):
        if line[i:i + 2] == "\\|":
            buf.append("|")
            i += 2
            continue
        if line[i] == "|":
            cells.append("".join(buf).strip())
            buf = []
        else:
            buf.append(line[i])
        i += 1
    cells.append("".join(buf).strip())
    return cells


def separator(line):
    return bool(re.fullmatch(r"\s*\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)+\|?\s*", line))


def read_table(lines, start, path, strict_tables=True):
    """Read one table starting at ``lines[start]``.

    A single blank line inside a Markdown table is a formatting accident, not
    the end of the table. Editors add one when a row is long. Treat at most one
    blank line as skippable while pipe rows continue, so a stray blank does not
    dump the rest of the table into the document as raw prose.
    """
    rows = [split_row(lines[start])]
    i = start + 2  # skip header and its separator
    width = len(rows[0])
    while i < len(lines):
        if not lines[i].strip():
            nxt = i + 1
            if nxt < len(lines) and lines[nxt].lstrip().startswith("|"):
                i = nxt
                continue
            break
        if not lines[i].lstrip().startswith("|"):
            break
        row = split_row(lines[i])
        if len(row) != width:
            if strict_tables or len(row) < width:
                raise ValueError(f"Table width mismatch at {path}:{i + 1}")
            # Some historical Word-source rows append a reference cell
            # without adding a header. Preserve it in the final cell;
            # record the mismatch as a warning in the Word exporter.
            row = row[:width - 1] + [" | ".join(row[width - 1:])]
        rows.append(row)
        i += 1
    return rows, i


def plain(text):
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"(?<!\w)\*([^*\n]+)\*(?!\w)", r"\1", text)
    return html.unescape(text).strip()


def parse_markdown(path, strict_tables=True):
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if lines and lines[0] == "---":
        try:
            end = lines.index("---", 1)
        except ValueError as exc:
            raise ValueError(f"Unclosed frontmatter: {path}") from exc
        lines = lines[end + 1:]
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or re.fullmatch(r"-{3,}|\*{3,}|_{3,}", line.strip()):
            i += 1
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            blocks.append(Block("heading", heading[2], len(heading[1]), source=path))
            i += 1
        elif line.startswith("```"):
            language = line[3:].strip()
            i += 1
            code = []
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            if i == len(lines):
                raise ValueError(f"Unclosed code block: {path}")
            blocks.append(Block("code", "\n".join(code), language=language, source=path))
            i += 1
        elif line.lstrip().startswith("|") and i + 1 < len(lines) and separator(lines[i + 1]):
            rows, i = read_table(lines, i, path, strict_tables)
            blocks.append(Block("table", rows=rows, source=path))
        elif re.fullmatch(r"!\[[^\]]*\]\([^)]+\)", line.strip()):
            match = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", line.strip())
            blocks.append(Block("image", match[2], language=match[1], source=path))
            i += 1
        elif re.match(r"^\s*(?:[-*+] |\d+\. )", line):
            # Keep the item text and its indent level, not the Markdown marker.
            # The marker itself becomes real Word numbering at render time.
            level = len(line) - len(line.lstrip(" "))
            match = re.match(r"^\s*(?:[-*+] |(\d+)\. )(.*)$", line)
            ordered = match[1] is not None
            blocks.append(Block("list", match[2], level=level // 2,
                                language="ordered" if ordered else "bullet", source=path))
            i += 1
        else:
            para = [line.lstrip("> ") if line.startswith(">") else line]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(
                    r"^(?:#|```|\||[-*+] |\d+\. |!\[)", lines[i]):
                para.append(lines[i])
                i += 1
            blocks.append(Block("paragraph", " ".join(para), source=path))
    return blocks


def tables(path):
    return [block.rows for block in parse_markdown(path) if block.kind == "table"]


def find_table(path, first_header):
    matches = [t for t in tables(path) if plain(t[0][0]) == first_header]
    if len(matches) != 1:
        raise ValueError(f"Expected one {first_header!r} table in {path}, found {len(matches)}")
    return matches[0]


def key_values(path, first_header="Field"):
    return {plain(row[0]): plain(row[-1]) for row in find_table(path, first_header)[1:]}


class WordDocument:
    def __init__(self, template):
        self.package = Package(template)
        self.doc = self.package.xml("word/document.xml")
        self.body = descendants(self.doc, "body")[0]
        original = children(self.body)
        self.headings = {}
        for p in [n for n in original if n.localName == "p"]:
            styles = descendants(p, "pStyle")
            if styles:
                name = styles[0].getAttribute("w:val")
                if name.startswith("Heading") and name not in self.headings:
                    self.headings[name] = p.cloneNode(True)
        self.table_prototypes = [n.cloneNode(True) for n in original if n.localName == "tbl"]
        body_candidates = [p for p in original if p.localName == "p"
                           and self.text(p) and not descendants(p, "pStyle")
                           and not descendants(p, "drawing") and original.index(p) > 28]
        # Blue/italic instruction paragraphs are template authoring hints, not
        # report prose. Prefer an actual example body paragraph, then a plain
        # caption with normal run properties when a report has no prose sample.
        normal = [p for p in body_candidates if not any(
            color.getAttribute("w:val") == "0000FF" for color in descendants(p, "color"))
            and self.text(p) not in {"…", ">>"}]
        samples = [p for p in normal if self.text(p).startswith("<<Sample:")]
        self.paragraph_prototype = (samples or normal or body_candidates)[0].cloneNode(True)
        for ppr in children(self.paragraph_prototype, "pPr"):
            remove_children(ppr)
            ppr.appendChild(element(self.doc, W, "w:spacing", {
                "w:before": "80", "w:after": "120", "w:line": "276", "w:lineRule": "auto"
            }))
            ppr.appendChild(element(self.doc, W, "w:jc", {"w:val": "left"}))
        for r in children(self.paragraph_prototype, "r"):
            self.paragraph_prototype.removeChild(r)
        self.picture_prototype = next(
            p.cloneNode(True) for p in original
            if p.localName == "p" and descendants(p, "drawing"))
        self.run_prototype = element(self.doc, W, "w:r")
        # Reuse a real template list paragraph so bullets, indents and the
        # numbering definition stay the originals instead of being invented.
        self.list_prototype = next(
            (p.cloneNode(True) for p in original
             if p.localName == "p" and descendants(p, "numPr")), None)
        self.list_num_id = ""
        if self.list_prototype is not None:
            ids = [n.getAttribute("w:val")
                   for n in descendants(self.list_prototype, "numId")]
            self.list_num_id = ids[0] if ids else ""
        first_heading = next(i for i, n in enumerate(original)
                             if n.localName == "p" and descendants(n, "pStyle")
                             and descendants(n, "pStyle")[0].getAttribute("w:val") == "Heading1")
        self.cover = original[:first_heading]
        self.section = next(n.cloneNode(True) for n in original if n.localName == "sectPr")
        for node in original[first_heading:]:
            self.body.removeChild(node)
        self.warnings = []
        self.heading_count = 0
        self.list_count = 0
        self.image_count = 0
        self.table_count = 0

    @staticmethod
    def text(node):
        return "".join(text_of(t) for t in descendants(node, "t"))

    def run(self, text, prototype=None, bold=False, italic=False, size=None):
        r = (prototype or self.run_prototype)
        r = r.cloneNode(True) if r is not None else element(self.doc, W, "w:r")
        remove_children(r, ("rPr",))
        if bold or italic or size:
            rp = (children(r, "rPr") or [None])[0]
            if rp is None:
                rp = element(self.doc, W, "w:rPr")
                r.insertBefore(rp, r.firstChild)
            for name, enabled in (("b", bold), ("i", italic)):
                if enabled and not children(rp, name):
                    rp.appendChild(element(self.doc, W, "w:" + name))
            if size:
                for tag in ("sz", "szCs"):
                    for old in children(rp, tag):
                        rp.removeChild(old)
                    rp.appendChild(element(self.doc, W, "w:" + tag, {"w:val": str(size)}))
        for index, line in enumerate(text.split("\n")):
            if index:
                r.appendChild(element(self.doc, W, "w:br"))
            t = element(self.doc, W, "w:t", {"xml:space": "preserve"})
            t.appendChild(self.doc.createTextNode(line))
            r.appendChild(t)
        return r

    def fill_paragraph(self, p, text, size=None):
        runs = descendants(p, "r")
        prototype = runs[0].cloneNode(True) if runs else self.run_prototype
        remove_children(p, ("pPr",))
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
        parts = re.split(r"(\*\*[^*\n]+\*\*|`[^`\n]+`|\[[^\]]+\]\([^)]+\))", text)
        for part in parts:
            if not part:
                continue
            visible = plain(part)
            leading = "\n" if part.startswith("\n") else (" " if part[:1].isspace() else "")
            trailing = "\n" if (visible and part.endswith("\n")) else (" " if visible and part[-1:].isspace() else "")
            p.appendChild(self.run(leading + visible + trailing, prototype,
                                  bold=part.startswith("**") and part.endswith("**"),
                                  italic=part.startswith("*") and not part.startswith("**"),
                                  size=size))
        return p

    def list_paragraph(self, text, level=0):
        """Render one list item as a real Word list, not text starting with '-'."""
        if self.list_prototype is None:
            return self.paragraph(text)
        p = self.list_prototype.cloneNode(True)
        properties = (children(p, "pPr") or [None])[0]
        if properties is not None:
            # Drop the inherited numPr as well; keeping it would duplicate the
            # element and leave Word resolving an ambiguous list definition.
            remove_children(properties, ("pStyle",))
            if self.list_num_id:
                num_pr = element(self.doc, W, "w:numPr")
                num_pr.appendChild(element(self.doc, W, "w:ilvl",
                                           {"w:val": str(min(level, 2))}))
                num_pr.appendChild(element(self.doc, W, "w:numId",
                                           {"w:val": self.list_num_id}))
                properties.insertBefore(num_pr, properties.firstChild)
        for r in children(p, "r"):
            p.removeChild(r)
        p = self.fill_paragraph(p, text)
        return p

    def paragraph(self, text, heading=None):
        if heading:
            prototype = self.headings.get(f"Heading{heading}")
            if prototype is None:
                prototype = self.headings.get("Heading3", self.paragraph_prototype)
                self.warnings.append(f"Heading level {heading} uses nearest available template style")
        else:
            prototype = self.paragraph_prototype
        p = self.fill_paragraph(prototype.cloneNode(True), text)
        # Remove copied target bookmarks so generated headings do not share ids.
        for name in ("bookmarkStart", "bookmarkEnd"):
            for node in list(descendants(p, name)):
                node.parentNode.removeChild(node)
        return p

    def choose_table(self, header):
        wanted = {plain(x).lower() for x in header}
        def score(table):
            trs = children(table, "tr")
            header_trs = trs[:2] if len(trs) >= 3 and descendants(trs[0], "gridSpan") else trs[:1]
            labels = {self.text(c).strip().lower() for r in header_trs for c in children(r, "tc") if self.text(c).strip()}
            data_row = trs[2] if len(trs) >= 3 and descendants(trs[0], "gridSpan") else trs[0]
            return (len(wanted & labels), len(children(data_row, "tc")) == len(header))
        return max(self.table_prototypes, key=score)

    def table(self, rows):
        template = self.choose_table(rows[0])
        table = template.cloneNode(True)
        prototypes = children(template, "tr")
        has_two_row_merged_header = (
            len(prototypes) >= 3
            and bool(descendants(prototypes[0], "gridSpan"))
            and bool(descendants(prototypes[1], "vMerge"))
            and len(children(prototypes[2], "tc")) == len(rows[0])
        )
        old_grid = children(template, "tblGrid")
        widths = [int(c.getAttribute("w:w") or 1000)
                  for c in children(old_grid[0], "gridCol")] if old_grid else []
        total = sum(widths) or 9000
        wanted_headers = {plain(x).strip().lower() for x in rows[0] if plain(x).strip()}
        tpl_hdr_trs = prototypes[:2] if len(prototypes) >= 3 and descendants(prototypes[0], "gridSpan") else prototypes[:1]
        tpl_labels = {self.text(c).strip().lower() for r in tpl_hdr_trs for c in children(r, "tc") if self.text(c).strip()}
        headers_match = len(wanted_headers & tpl_labels) >= max(2, len(rows[0]) // 2)
        if len(rows[0]) == 3 and wanted_headers <= {"#", "no", "no.", "package", "table", "class", "entity", "actor", "description"}:
            widths = [650, 2750, max(4500, total - 3400)]
        elif len(rows[0]) == 2:
            widths = [int(total * 0.34), total - int(total * 0.34)]
        elif len(widths) != len(rows[0]) or not headers_match:
            col_weights = []
            for col_idx in range(len(rows[0])):
                hdr_txt = plain(rows[0][col_idx]).strip()
                hdr_lower = hdr_txt.lower()
                col_cells = [plain(r[col_idx]).strip() for r in rows[:20] if col_idx < len(r)]
                max_line_len = max((len(ln.strip()) for c in col_cells for ln in c.splitlines()), default=len(hdr_txt))
                max_word_len = max((len(w) for c in col_cells for w in re.findall(r"\S+", c)), default=len(hdr_txt))
                if hdr_lower in {"#", "no", "no.", "id"} and max_line_len <= 10:
                    col_weights.append(7)
                elif max_line_len <= 16 and max_word_len <= 14:
                    col_weights.append(14)
                elif max_line_len <= 32 and max_word_len <= 20:
                    col_weights.append(22)
                elif max_line_len <= 55:
                    col_weights.append(30)
                else:
                    col_weights.append(42)
            weight_sum = sum(col_weights) or 1
            widths = [max(650, int(total * w / weight_sum)) for w in col_weights]
            widths[-1] = max(650, widths[-1] + (total - sum(widths)))
        for row in children(table, "tr"):
            table.removeChild(row)
        grid = (children(table, "tblGrid") or [None])[0]
        if grid is None:
            grid = element(self.doc, W, "w:tblGrid")
            table.appendChild(grid)
        remove_children(grid)
        for width in widths:
            grid.appendChild(element(self.doc, W, "w:gridCol", {"w:w": width}))
        start_index = 0
        if has_two_row_merged_header:
            table.appendChild(prototypes[0].cloneNode(True))
            table.appendChild(prototypes[1].cloneNode(True))
            start_index = 1
        for index, values in enumerate(rows[start_index:], start_index):
            if has_two_row_merged_header:
                proto = prototypes[2]
            else:
                proto = prototypes[0] if index == 0 else prototypes[min(1, len(prototypes) - 1)]
            row = proto.cloneNode(True)
            tr_pr = (children(row, "trPr") or [None])[0]
            if tr_pr is None:
                tr_pr = element(self.doc, W, "w:trPr")
                row.insertBefore(tr_pr, row.firstChild)
            if not children(tr_pr, "cantSplit"):
                tr_pr.appendChild(element(self.doc, W, "w:cantSplit"))
            if index == 0 and not children(tr_pr, "tblHeader"):
                tr_pr.appendChild(element(self.doc, W, "w:tblHeader"))
            cells = children(proto, "tc")
            for cell in children(row, "tc"):
                row.removeChild(cell)
            for col, value in enumerate(values):
                cell = cells[min(col, len(cells) - 1)].cloneNode(True)
                properties = (children(cell, "tcPr") or [None])[0]
                if properties is not None:
                    for span in children(properties, "gridSpan") + children(properties, "vMerge"):
                        properties.removeChild(span)
                    for width in children(properties, "tcW"):
                        width.setAttributeNS(W, "w:w", str(widths[col]))
                ps = children(cell, "p")
                cell_p = ps[0].cloneNode(True) if ps else self.paragraph_prototype.cloneNode(True)
                if index > 0:
                    hdr_lower = plain(rows[0][col]).strip().lower() if col < len(rows[0]) else ""
                    jc_val = "center" if (col == 0 and hdr_lower in {"#", "no", "no.", "id"} and len(plain(value)) <= 8) else "left"
                    for ppr in children(cell_p, "pPr"):
                        for rpr in children(ppr, "rPr"):
                            ppr.removeChild(rpr)
                        for pstyle in children(ppr, "pStyle"):
                            ppr.removeChild(pstyle)
                        for sp in children(ppr, "spacing"):
                            ppr.removeChild(sp)
                        for jc in children(ppr, "jc"):
                            ppr.removeChild(jc)
                        ppr.appendChild(element(self.doc, W, "w:spacing", {
                            "w:before": "60", "w:after": "60", "w:line": "250", "w:lineRule": "auto"
                        }))
                        ppr.appendChild(element(self.doc, W, "w:jc", {"w:val": jc_val}))
                    for r in children(cell_p, "r"):
                        cell_p.removeChild(r)
                p = self.fill_paragraph(cell_p, value, size=20 if index > 0 else None)
                # Drop every inherited child, not just paragraphs: a cloned
                # cell may carry a nested table or extra paragraph that would
                # otherwise wrap the new text inside the original content.
                remove_children(cell, ("tcPr",))
                cell.appendChild(p)
                row.appendChild(cell)
            table.appendChild(row)
        self.table_count += 1
        return table

    def image(self, path, alt):
        if not path.is_file():
            raise ValueError(f"Missing source image: {path}")
        data = path.read_bytes()
        if data[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Only PNG report images are supported: {path}")
        width, height = struct.unpack(">II", data[16:24])
        self.image_count += 1
        part = f"word/media/source_report_{self.image_count}.png"
        self.package.parts[part] = data
        rels = self.package.xml("word/_rels/document.xml.rels")
        used = {n.getAttribute("Id") for n in descendants(rels, "Relationship")}
        rel_id = f"rIdReport{self.image_count}"
        while rel_id in used:
            rel_id += "x"
        rels.documentElement.appendChild(element(rels, PKG_R, "Relationship", {
            "Id": rel_id, "Type": R + "/image", "Target": part.removeprefix("word/")}))
        self.package.set_xml("word/_rels/document.xml.rels", rels)
        # All official DOCX templates already include PNG content-type defaults.
        p = self.picture_prototype.cloneNode(True)
        size_x = 5_500_000
        size_y = round(size_x * height / width)
        max_y = 6_800_000
        if size_y > max_y:
            size_x = round(max_y * width / height)
            size_y = max_y
        for extent in descendants(p, "extent") + descendants(p, "ext"):
            if extent.hasAttribute("cx"):
                extent.setAttribute("cx", str(size_x))
                extent.setAttribute("cy", str(size_y))
        for blip in descendants(p, "blip"):
            blip.setAttributeNS(R, "r:embed", rel_id)
        for prop in descendants(p, "docPr"):
            prop.setAttribute("id", str(1000 + self.image_count))
            prop.setAttribute("name", path.name)
            prop.setAttribute("descr", alt)
        return p

    def fill_cover(self, project_name, location):
        paras = [p for p in self.cover if p.localName == "p"]
        title = next((p for p in paras if self.text(p).startswith("Report")), None)
        if title:
            index = paras.index(title)
            for p in paras[index + 1:]:
                if not self.text(p) and not descendants(p, "drawing"):
                    self.fill_paragraph(p, project_name)
                    break
        for p in paras:
            if "Hanoi" in self.text(p) and location:
                self.fill_paragraph(p, location)
        self.toc_content = None
        for sdt in [n for n in self.cover if n.localName == "sdt"]:
            content = descendants(sdt, "sdtContent")[0]
            paras = children(content, "p")
            self.toc_title = paras[0].cloneNode(True)
            instructions = descendants(content, "instrText")
            self.toc_instruction = next((text_of(t) for t in instructions if "TOC " in text_of(t)),
                                        ' TOC \\o "1-3" \\h \\z \\u ')
            self.toc_content = content

    def append(self, blocks):
        toc_entries = []
        current_page = 3
        page_lines = 0

        for block in blocks:
            if block.kind == "heading":
                if block.level == 1 and current_page > 3:
                    current_page += 1
                    page_lines = 0
                hp = self.paragraph(block.text, block.level)
                if block.level in (1, 2, 3):
                    bm_id = str(900000 + len(toc_entries) + 1)
                    anchor = f"_Toc{bm_id}"
                    bm_start = element(self.doc, W, "w:bookmarkStart", {"w:id": bm_id, "w:name": anchor})
                    bm_end = element(self.doc, W, "w:bookmarkEnd", {"w:id": bm_id})
                    first_run = next((c for c in children(hp) if c.localName != "pPr"), None)
                    if first_run is not None:
                        hp.insertBefore(bm_start, first_run)
                    else:
                        hp.appendChild(bm_start)
                    hp.appendChild(bm_end)
                    toc_entries.append((block.level, plain(block.text), current_page, anchor))
                self.body.appendChild(hp)
                self.heading_count += 1
                page_lines += 2
            elif block.kind == "table":
                self.body.appendChild(self.table(block.rows))
                page_lines += len(block.rows) + 2
            elif block.kind == "image":
                self.body.appendChild(self.image(block.source.parent / block.text, block.language))
                page_lines += 15
            elif block.kind == "code":
                if block.language == "mermaid":
                    title = "System Diagram"
                    match = re.search(r"%%\s*title:\s*(.+)$", block.text, re.M | re.I)
                    if match:
                        title = match.group(1).strip()
                    else:
                        text_lower = block.text.lower()
                        if "sequencediagram" in text_lower:
                            title = "Sequence Diagram"
                        elif "classdiagram" in text_lower:
                            title = "Class Diagram"
                        elif "statediagram" in text_lower:
                            title = "State Machine Diagram"
                        elif "package" in text_lower:
                            title = "Package Diagram"
                        elif "architecture" in text_lower:
                            title = "System Architecture Diagram"
                        elif "erdiagram" in text_lower or "entity relationship" in text_lower:
                            title = "Entity Relationship Diagram (ERD)"
                        elif "flowchart lr" in text_lower or "use case" in text_lower:
                            title = "Use Case Diagram"
                        elif "screens flow" in text_lower or "flowchart td" in text_lower:
                            title = "Screens Flow Diagram"
                    digest = sha256(block.text.strip().encode("utf-8"))[:12]
                    png_path = (block.source.parent / "assets" / "mermaid" / f"{digest}.png") if block.source else None
                    if png_path is not None and png_path.is_file():
                        self.warnings.append(f"Mermaid diagram embedded ({png_path.name}): {block.source.name}")
                        self.body.appendChild(self.image(png_path, title))
                        self.body.appendChild(self.paragraph(f"**Figure: {title}**"))
                        page_lines += 16
                    else:
                        self.warnings.append(f"Mermaid diagram placeholder rendered: {block.source.name}")
                        placeholder_content = (
                            f"**[ Figure Placeholder: {title} ]**\n\n\n\n\n"
                            f"*(Insert {title} image / screenshot here)*\n\n\n\n"
                        )
                        self.body.appendChild(self.table([[placeholder_content]]))
                        page_lines += 12
                else:
                    self.body.appendChild(self.paragraph(block.text))
                    page_lines += max(1, len(block.text) // 80)
            elif block.kind == "list":
                self.body.appendChild(self.list_paragraph(block.text, block.level))
                self.list_count += 1
                page_lines += 1
            else:
                self.body.appendChild(self.paragraph(block.text))
                page_lines += max(1, len(block.text) // 80)

            if page_lines >= 38:
                current_page += page_lines // 38
                page_lines = page_lines % 38

        if self.toc_content is not None:
            remove_children(self.toc_content)
            self.toc_content.appendChild(self.toc_title)
            if not toc_entries:
                field = self.paragraph_prototype.cloneNode(True)
                remove_children(field, ("pPr",))
                for kind in ("begin", "instruction", "separate", "end"):
                    r = element(self.doc, W, "w:r")
                    if kind == "instruction":
                        instr = element(self.doc, W, "w:instrText", {"xml:space": "preserve"})
                        instr.appendChild(self.doc.createTextNode(self.toc_instruction))
                        r.appendChild(instr)
                    else:
                        r.appendChild(element(self.doc, W, "w:fldChar", {"w:fldCharType": kind}))
                    field.appendChild(r)
                self.toc_content.appendChild(field)
            else:
                for i, (lvl, text, pg, anchor) in enumerate(toc_entries):
                    p = element(self.doc, W, "w:p")
                    pPr = element(self.doc, W, "w:pPr")
                    pPr.appendChild(element(self.doc, W, "w:pStyle", {"w:val": f"TOC{lvl}"}))
                    tabs = element(self.doc, W, "w:tabs")
                    tabs.appendChild(element(self.doc, W, "w:tab", {"w:val": "right", "w:leader": "dot", "w:pos": "9040"}))
                    pPr.appendChild(tabs)
                    p_rpr = element(self.doc, W, "w:rPr")
                    p_rpr.appendChild(element(self.doc, W, "w:rFonts", {"w:eastAsiaTheme": "minorEastAsia"}))
                    p_rpr.appendChild(element(self.doc, W, "w:noProof"))
                    p_rpr.appendChild(element(self.doc, W, "w:sz", {"w:val": "24"}))
                    p_rpr.appendChild(element(self.doc, W, "w:szCs", {"w:val": "24"}))
                    p_rpr.appendChild(element(self.doc, W, "w:lang", {"w:eastAsia": "en-GB"}))
                    pPr.appendChild(p_rpr)
                    p.appendChild(pPr)

                    if i == 0:
                        r_begin = element(self.doc, W, "w:r")
                        r_begin.appendChild(element(self.doc, W, "w:fldChar", {"w:fldCharType": "begin"}))
                        p.appendChild(r_begin)

                        r_instr = element(self.doc, W, "w:r")
                        instr = element(self.doc, W, "w:instrText", {"xml:space": "preserve"})
                        instr.appendChild(self.doc.createTextNode(self.toc_instruction))
                        r_instr.appendChild(instr)
                        p.appendChild(r_instr)

                        r_sep = element(self.doc, W, "w:r")
                        r_sep.appendChild(element(self.doc, W, "w:fldChar", {"w:fldCharType": "separate"}))
                        p.appendChild(r_sep)

                    hl = element(self.doc, W, "w:hyperlink", {"w:anchor": anchor, "w:history": "1"})

                    r_text = element(self.doc, W, "w:r")
                    r_text_pr = element(self.doc, W, "w:rPr")
                    r_text_pr.appendChild(element(self.doc, W, "w:rStyle", {"w:val": "Hyperlink"}))
                    r_text_pr.appendChild(element(self.doc, W, "w:noProof"))
                    r_text.appendChild(r_text_pr)
                    t = element(self.doc, W, "w:t")
                    t.appendChild(self.doc.createTextNode(text))
                    r_text.appendChild(t)
                    hl.appendChild(r_text)

                    def hidden_run(child_node):
                        rr = element(self.doc, W, "w:r")
                        rr_pr = element(self.doc, W, "w:rPr")
                        rr_pr.appendChild(element(self.doc, W, "w:noProof"))
                        rr_pr.appendChild(element(self.doc, W, "w:webHidden"))
                        rr.appendChild(rr_pr)
                        rr.appendChild(child_node)
                        return rr

                    hl.appendChild(hidden_run(element(self.doc, W, "w:tab")))
                    hl.appendChild(hidden_run(element(self.doc, W, "w:fldChar", {"w:fldCharType": "begin"})))
                    p_instr = element(self.doc, W, "w:instrText", {"xml:space": "preserve"})
                    p_instr.appendChild(self.doc.createTextNode(f" PAGEREF {anchor} \\h "))
                    hl.appendChild(hidden_run(p_instr))
                    hl.appendChild(hidden_run(element(self.doc, W, "w:fldChar", {"w:fldCharType": "separate"})))
                    t_page = element(self.doc, W, "w:t")
                    t_page.appendChild(self.doc.createTextNode(str(pg)))
                    hl.appendChild(hidden_run(t_page))
                    hl.appendChild(hidden_run(element(self.doc, W, "w:fldChar", {"w:fldCharType": "end"})))

                    p.appendChild(hl)
                    self.toc_content.appendChild(p)

                p_end = element(self.doc, W, "w:p")
                r_end = element(self.doc, W, "w:r")
                r_end_pr = element(self.doc, W, "w:rPr")
                r_end_pr.appendChild(element(self.doc, W, "w:b"))
                r_end_pr.appendChild(element(self.doc, W, "w:bCs"))
                r_end_pr.appendChild(element(self.doc, W, "w:noProof"))
                r_end.appendChild(r_end_pr)
                r_end.appendChild(element(self.doc, W, "w:fldChar", {"w:fldCharType": "end"}))
                p_end.appendChild(r_end)
                self.toc_content.appendChild(p_end)
        self.body.appendChild(self.section)
        self.package.set_xml("word/document.xml", self.doc)
        settings = self.package.xml("word/settings.xml")
        updates = descendants(settings, "updateFields")
        update = updates[0] if updates else element(settings, W, "w:updateFields")
        update.setAttributeNS(W, "w:val", "true")
        if not updates:
            settings.documentElement.appendChild(update)
        self.package.set_xml("word/settings.xml", settings)

    def save(self, path):
        audit = self.package.audit({"word/document.xml", "word/settings.xml", "word/_rels/document.xml.rels"})
        self.package.save(path)
        return {**audit, "headings": self.heading_count, "tables": self.table_count,
                "lists": self.list_count,
                "source_images": self.image_count, "warnings": sorted(set(self.warnings))}


def col_number(column):
    result = 0
    for ch in column:
        result = result * 26 + ord(ch) - 64
    return result


def col_letter(number):
    result = ""
    while number:
        number, rest = divmod(number - 1, 26)
        result = chr(65 + rest) + result
    return result


class Spreadsheet:
    def __init__(self, template):
        self.package = Package(template)
        self.changed_parts = set()
        self.next_sheet_id = 0
        self.strings = []
        if "xl/sharedStrings.xml" in self.package.parts:
            for si in descendants(self.package.xml("xl/sharedStrings.xml"), "si"):
                self.strings.append("".join(text_of(t) for t in descendants(si, "t")))
        book = self.package.xml("xl/workbook.xml")
        rels = self.package.xml("xl/_rels/workbook.xml.rels")
        targets = {r.getAttribute("Id"): r.getAttribute("Target")
                   for r in descendants(rels, "Relationship")}
        self.sheets = {}
        for sheet in descendants(book, "sheet"):
            target = targets[sheet.getAttribute("r:id")]
            part = target.lstrip("/") if target.startswith("/") else "xl/" + target
            self.sheets[sheet.getAttribute("name")] = (part, self.package.xml(part))

    def sheet(self, name):
        return self.sheets[name][1]

    def cell(self, name, coord):
        doc = self.sheet(name)
        data = descendants(doc, "sheetData")[0]
        row_no = int(re.search(r"\d+", coord)[0])
        rows = children(data, "row")
        row = next((r for r in rows if r.getAttribute("r") == str(row_no)), None)
        if row is None:
            row = element(doc, S, "row", {"r": row_no})
            later = next((r for r in rows if int(r.getAttribute("r")) > row_no), None)
            data.insertBefore(row, later)
        cells = children(row, "c")
        cell = next((c for c in cells if c.getAttribute("r") == coord), None)
        if cell is None:
            cell = element(doc, S, "c", {"r": coord})
            number = col_number(re.match(r"[A-Z]+", coord)[0])
            later = next((c for c in cells if col_number(re.match(r"[A-Z]+", c.getAttribute("r"))[0]) > number), None)
            row.insertBefore(cell, later)
        return cell

    def value(self, name, coord):
        cell = self.cell(name, coord)
        if cell.getAttribute("t") == "inlineStr":
            return "".join(text_of(t) for t in descendants(cell, "t"))
        vs = children(cell, "v")
        value = text_of(vs[0]) if vs else ""
        if cell.getAttribute("t") == "s" and value:
            return self.strings[int(value)]
        return value

    def put(self, name, coord, value, formula=None):
        cell = self.cell(name, coord)
        remove_children(cell)
        if formula is not None:
            cell.removeAttribute("t") if cell.hasAttribute("t") else None
            f = element(cell.ownerDocument, S, "f")
            f.appendChild(cell.ownerDocument.createTextNode(formula.lstrip("=")))
            cell.appendChild(f)
            v = element(cell.ownerDocument, S, "v")
            v.appendChild(cell.ownerDocument.createTextNode(str(value)))
            cell.appendChild(v)
        elif value is None or value == "":
            if cell.hasAttribute("t"):
                cell.removeAttribute("t")
        elif isinstance(value, (int, float)):
            if cell.hasAttribute("t"):
                cell.removeAttribute("t")
            v = element(cell.ownerDocument, S, "v")
            v.appendChild(cell.ownerDocument.createTextNode(str(value)))
            cell.appendChild(v)
        else:
            cell.setAttribute("t", "inlineStr")
            inline = element(cell.ownerDocument, S, "is")
            t = element(cell.ownerDocument, S, "t", {"xml:space": "preserve"})
            t.appendChild(cell.ownerDocument.createTextNode(str(value)))
            inline.appendChild(t)
            cell.appendChild(inline)

    def row_template(self, name, row):
        return next(r.cloneNode(True) for r in descendants(self.sheet(name), "row")
                    if r.getAttribute("r") == str(row))

    def clear_rows(self, name, start):
        data = descendants(self.sheet(name), "sheetData")[0]
        for row in children(data, "row"):
            if int(row.getAttribute("r")) >= start:
                data.removeChild(row)

    def clone_row(self, name, number, prototype):
        doc = self.sheet(name)
        row = doc.importNode(prototype, True)
        old = int(row.getAttribute("r"))
        row.setAttribute("r", str(number))
        for cell in children(row, "c"):
            coord = re.match(r"[A-Z]+", cell.getAttribute("r"))[0] + str(number)
            cell.setAttribute("r", coord)
            remove_children(cell)
            if cell.hasAttribute("t"):
                cell.removeAttribute("t")
        data = descendants(doc, "sheetData")[0]
        later = next((r for r in children(data, "row") if int(r.getAttribute("r")) > number), None)
        data.insertBefore(row, later)
        return row

    def fit_height(self, name, row, values, widths):
        doc = self.sheet(name)
        target = next(r for r in descendants(doc, "row") if r.getAttribute("r") == str(row))
        # Excel has no AutoFit for all merged/wrapped text. Estimate conservatively
        # within its 409-point row-height limit and surface the limit to callers.
        lines = max((sum(max(1, math.ceil(len(line) / max(8, widths[i] - 2)))
                         for line in plain(value).split("\n"))
                     for i, value in enumerate(values)), default=1)
        height = min(409, max(28, lines * 15 + 8))
        target.setAttribute("ht", str(height))
        target.setAttribute("customHeight", "1")
        return height == 409

    def dimensions(self, name, last_col, last_row):
        doc = self.sheet(name)
        dim = descendants(doc, "dimension")[0]
        dim.setAttribute("ref", f"A1:{last_col}{last_row}")

    def _add_content_type(self, part_name, content_type):
        types = self.package.xml("[Content_Types].xml")
        for existing in descendants(types, "Override"):
            if existing.getAttribute("PartName") == part_name:
                return
        node = element(types, "http://schemas.openxmlformats.org/package/2006/content-types",
                       "Override", {"PartName": part_name, "ContentType": content_type})
        types.documentElement.appendChild(node)
        self.package.set_xml("[Content_Types].xml", types)

    def _own_relationships(self, data, index):
        """Drop the source sheet's comment and VML links from a clone.

        A worksheet's comments are anchored to specific cells and their legacy
        VML shape carries those anchors. A cloned sheet has none of that
        content, and Excel rejects the workbook outright when the anchors are
        missing. Printer settings and drawings are shared by design and are
        left in place.
        """
        rels = minidom.parseString(data)
        for rel in list(descendants(rels, "Relationship")):
            if any(kind in rel.getAttribute("Type")
                   for kind in ("/comments", "/vmlDrawing")):
                rel.parentNode.removeChild(rel)
        return rels.toxml(encoding="UTF-8")

    def duplicate_sheet(self, source, new_name):
        """Clone an existing sheet, its part and its styles, under a new name.

        The clone is a byte-level copy of the source sheet XML, so column
        widths, merged cells, validations and style ids are identical. Only the
        sheet name and the internal part name change.
        """
        if new_name in self.sheets:
            raise ValueError(f"Sheet already exists: {new_name}")
        part, doc = self.sheets[source]
        index = 1 + max((int(m.group(1)) for m in
                         (re.fullmatch(r"xl/worksheets/sheet(\d+)\.xml", p)
                          for p in self.package.parts) if m), default=0)
        new_part = f"xl/worksheets/sheet{index}.xml"
        self.package.parts[new_part] = self.package.parts[part]
        # The legacy VML shape only anchors the source sheet's comments, which
        # this clone drops. Register the edited DOM, not a second parse of the
        # unchanged bytes, or the removal is lost when the sheet is saved.
        clone_doc = self.package.xml(new_part)
        for shape in descendants(clone_doc, "legacyDrawing"):
            shape.parentNode.removeChild(shape)
        self.sheets[new_name] = (new_part, clone_doc)
        # A sheet may reference its own parts (printer settings, images) by
        # r:id. Those ids resolve through the sheet's .rels file, so the clone
        # needs its own copy or Excel rejects the workbook as corrupt.
        source_rels = part.rsplit("/", 1)[0] + "/_rels/" + part.rsplit("/", 1)[1] + ".rels"
        if source_rels in self.package.parts:
            new_rels = "xl/worksheets/_rels/" + Path(new_part).name + ".rels"
            self.package.parts[new_rels] = self._own_relationships(
                self.package.parts[source_rels], index)
            self.changed_parts.add(new_rels)

        book = self.package.xml("xl/workbook.xml")
        rels = self.package.xml("xl/_rels/workbook.xml.rels")
        sheet_nodes = descendants(book, "sheet")
        clone = sheet_nodes[-1].cloneNode(True)
        used = {n.getAttribute("name") for n in sheet_nodes}
        name = new_name
        while name in used:
            name += "_"
        clone.setAttribute("name", name)
        rel_ids = {n.getAttribute("Id") for n in descendants(rels, "Relationship")}
        rel_id = f"rIdSheet{index}"
        while rel_id in rel_ids:
            rel_id += "x"
        clone.setAttributeNS(R, "r:id", rel_id)
        # sheetId must be unique across the workbook; Excel refuses to open a
        # file where several sheets share one.
        used_ids = {int(n.getAttribute("sheetId") or 0) for n in sheet_nodes}
        # The template reuses non-contiguous sheetIds, so take max+1 rather
        # than the lowest free value.
        clone.setAttribute("sheetId", str(max(used_ids) + 1))
        self.next_sheet_id = max(used_ids) + 1
        sheet_nodes[-1].parentNode.appendChild(clone)

        # The workbook part resolves sheets through this relationship list;
        # a sheet entry without its relationship makes the file unreadable.
        template_rel = next(r for r in descendants(rels, "Relationship")
                            if r.getAttribute("Id")
                            == sheet_nodes[-2].getAttribute("r:id"))
        new_rel = template_rel.cloneNode(True)
        new_rel.setAttribute("Id", rel_id)
        new_rel.setAttribute("Target", "worksheets/" + Path(new_part).name)
        template_rel.parentNode.appendChild(new_rel)

        types = self.package.xml("[Content_Types].xml")
        override = next(o for o in descendants(types, "Override")
                         if o.getAttribute("PartName") == "/" + part)
        # Register through the helper so entries added while copying this
        # sheet's comments part are not overwritten here.
        self.package.parts["xl/workbook.xml"] = book.toxml(encoding="UTF-8")
        self.package.parts["xl/_rels/workbook.xml.rels"] = rels.toxml(encoding="UTF-8")
        self._add_content_type("/" + new_part, override.getAttribute("ContentType"))
        # New parts are additions, not modifications: the audit reports them
        # through ``added_parts`` and must not treat them as format changes.
        self.changed_parts.add(new_part)
        self.changed_parts.add("xl/workbook.xml")
        self.changed_parts.add("xl/_rels/workbook.xml.rels")
        self.changed_parts.add("[Content_Types].xml")
        return new_name

    def save(self, path, extra_changed=()):
        new_parts = self.changed_parts
        allowed = ({part for part, _ in self.sheets.values()}
                   | set(extra_changed)
                   | {p for p in new_parts
                      if p in self.package.original})
        for part, doc in self.sheets.values():
            # Serialize only changed sheets, keeping unrelated sheets byte-identical.
            candidate = doc.toxml(encoding="UTF-8")
            if part not in self.package.original:
                self.package.parts[part] = candidate
                continue
            original_dom = minidom.parseString(self.package.original[part])
            if doc.toxml() != original_dom.toxml():
                self.package.parts[part] = candidate
        audit = self.package.audit(allowed)
        self.package.save(path)
        return audit
