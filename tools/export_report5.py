#!/usr/bin/env python3
"""Export the Report 5 test workbook with lossless round data and original styles."""
from pathlib import Path
import re
import sys
from collections import Counter

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from export_common import number
from report_ooxml import Spreadsheet, descendants, find_table, key_values, parse_markdown, plain, tables

TEMPLATE_NAME = "Report5_Test Report.xlsx"
SOURCES = ["report-5-test-report"]
STATUS = {"Passed", "Failed", "Pending", "N/A"}
# Report 3 defines eight product features (FE-01..FE-08, sections 3.2-3.9).
# The supplied template ships two feature sheets; the generated workbook gives
# each Report 3 feature its own sheet, so sheet N tests FE-0N.
FEATURE_SHEETS = [f"Feature {n}" for n in range(1, 9)]
CASE_HEADER = ["Test Case ID", "Test Case Description", "Test Case Procedure",
               "Expected Results", "Pre-conditions", "Round 1", "Test date", "Tester",
               "Round 2", "Test date", "Tester", "Round 3", "Test date", "Tester", "Note"]
# Row 15 is the template's own empty spacer between the Sub total and the
# coverage rows; cloning it keeps the original vertical spacing.
BLANK_SPACER_ROW = 15


def validate_cases(report_dir):
    index = find_table(report_dir / "01-test-cases/test-case-list.md", "No")
    if index[0] != ["No", "Function Name", "Sheet Name", "Description", "Pre-Condition"]:
        raise ValueError("Report 5 case index columns do not match the official template")
    routes = {}
    for row in index[1:]:
        case = re.search(r"WF\d-\d{3}", row[1])
        feature = re.search(r"FE-\d{2}", row[1])
        if not case or not feature or plain(row[2]) not in FEATURE_SHEETS:
            raise ValueError(f"Invalid Report 5 index row: {row}")
        if case[0] in routes:
            raise ValueError(f"Duplicate Report 5 index ID: {case[0]}")
        if plain(row[2]) != f"Feature {int(feature[0][3:])}":
            raise ValueError(
                f"Case {case[0]} ({feature[0]}) must sit on sheet "
                f"Feature {int(feature[0][3:])}, not {row[2]}")
        routes[case[0]] = (plain(row[2]), feature[0])
    cases = {sheet: [] for sheet in FEATURE_SHEETS}
    ids, summaries = set(), {}
    feature_files = sorted((report_dir / "03-features").glob("fe-*.md"))
    if len(feature_files) != len(FEATURE_SHEETS):
        raise ValueError(f"Report 5 must have exactly {len(FEATURE_SHEETS)} FE-specific sources")
    for path in feature_files:
        text = path.read_text(encoding="utf-8")
        heading = re.search(r"^# (FE-\d{2}):", text, re.M)
        if heading is None:
            raise ValueError(f"Missing FE title: {path}")
        for table in tables(path):
            if table[0] == ["Cell", "Label", "Value"]:
                values = {plain(row[0]): plain(row[2]) for row in table[1:]}
                sheet = re.search(r"Values for the `([^`]+)` summary", text)
                if sheet:
                    if not values.get("B2") or not values.get("B3"):
                        raise ValueError(f"Empty sheet summary: {path}")
                    expected_sheet = f"Feature {int(heading[1][3:])}"
                    if sheet[1] != expected_sheet:
                        raise ValueError(
                            f"{heading[1]} summary belongs on {expected_sheet}, "
                            f"not {sheet[1]}: {path}")
                    summaries[sheet[1]] = values
            if table[0][0] != "Test Case ID":
                continue
            if table[0] != CASE_HEADER:
                raise ValueError(f"Execution columns differ from the 15 official columns: {path}")
            for row in table[1:]:
                # Repeated date/tester headers are positional, never dictionary keys.
                if row[0] in ids or row[0] not in routes:
                    raise ValueError(f"Duplicate or unindexed case: {row[0]}")
                route, feature = routes[row[0]]
                if feature != heading[1]:
                    raise ValueError(f"Case {row[0]} assigned to wrong FE source")
                for start in (5, 8, 11):
                    if row[start] not in STATUS:
                        raise ValueError(f"Invalid round status for {row[0]}")
                    if row[start] in {"Passed", "Failed"} and (not row[start + 1] or not row[start + 2]):
                        raise ValueError(f"Executed round lacks date/tester for {row[0]}")
                    if row[start] == "Pending" and (row[start + 1] or row[start + 2]):
                        raise ValueError(f"Unexecuted round has date/tester for {row[0]}")
                    if row[start + 1] and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row[start + 1]):
                        raise ValueError(f"Invalid test date for {row[0]}")
                ids.add(row[0])
                cases[route].append((feature, row, path))
    if ids != set(routes):
        raise ValueError(f"Missing cases: {set(routes) - ids}")
    for name in cases:
        if name not in summaries:
            raise ValueError(f"Missing summary source for {name}")
    counts = Counter(row[5] for group in cases.values() for _, row, _ in group)
    stats = find_table(report_dir / "02-test-statistics/test-statistics.md", "No")
    subtotal = next(row for row in stats[1:] if plain(row[0]).lower().replace(" ", "") == "subtotal")
    recorded = [int(plain(value)) for value in subtotal[2:]]
    expected = [counts[s] for s in ("Passed", "Failed", "Pending", "N/A")] + [len(ids)]
    if recorded != expected:
        raise ValueError(f"Recorded statistics {recorded} differ from cases {expected}")
    return cases, index, summaries


def discard_stale_calculation_chain(book):
    extra_parts = {"xl/workbook.xml"}
    if "xl/calcChain.xml" not in book.package.parts:
        return extra_parts
    # The original chain includes cells now populated with literal metadata.
    # Retaining it makes Excel reject the file. It is an index, not formatting.
    del book.package.parts["xl/calcChain.xml"]
    rels = book.package.xml("xl/_rels/workbook.xml.rels")
    for rel in list(descendants(rels, "Relationship")):
        if rel.getAttribute("Type").endswith("/calcChain"):
            rel.parentNode.removeChild(rel)
    book.package.set_xml("xl/_rels/workbook.xml.rels", rels)
    types = book.package.xml("[Content_Types].xml")
    for item in list(descendants(types, "Override")):
        if item.getAttribute("PartName") == "/xl/calcChain.xml":
            item.parentNode.removeChild(item)
    book.package.set_xml("[Content_Types].xml", types)
    return extra_parts | {"xl/calcChain.xml", "xl/_rels/workbook.xml.rels", "[Content_Types].xml"}


def export(template, reports, output):
    report = reports / SOURCES[0]
    cases, index, summaries = validate_cases(report)
    cover = key_values(report / "00-cover/cover.md")
    stats_meta = key_values(report / "02-test-statistics/test-statistics.md")
    index_meta = key_values(report / "01-test-cases/test-case-list.md")
    history = find_table(report / "00-cover/record-of-changes.md", "Effective Date")
    version = re.match(r"\d+\.\d+", cover["Version"])[0]
    date = history[-1][0]
    book, warnings = Spreadsheet(template), []
    # The template ships two feature sheets; clone Feature 2 until every Report 3
    # feature has one. Clones keep the original column widths, merges, validations
    # and style ids, so only the sheet name differs.
    while len(book.sheets) < len(FEATURE_SHEETS) + 3:
        book.duplicate_sheet("Feature 2", f"Feature {len(book.sheets) - 2}")
    for coord, value in {
        "B4": cover["Project Name"], "B5": cover["Project Code"],
        "F4": cover.get("Creator", "Not supplied"), "F5": date, "F6": version,
        "B6": cover.get("Document Code", "Not supplied"),
    }.items():
        book.put("Cover", coord, value)
    proto = book.row_template("Cover", 11)
    book.clear_rows("Cover", 11)
    for row_no, row in enumerate(history[1:], 11):
        book.clone_row("Cover", row_no, proto)
        for col, value in enumerate(row, 1):
            book.put("Cover", f"{chr(64 + col)}{row_no}", plain(value))
        if book.fit_height("Cover", row_no, row, [14, 9, 24, 7, 88, 50]):
            warnings.append(f"Cover history row {row_no} reaches Excel's row-height limit")
    book.dimensions("Cover", "F", len(history) + 9)
    for coord, value in {"D3": cover["Project Name"], "D4": cover["Project Code"],
                         "D5": index_meta.get("Test environment", "Not supplied")}.items():
        book.put("Test Cases", coord, value)
    proto = book.row_template("Test Cases", 9)
    book.clear_rows("Test Cases", 9)
    for row_no, row in enumerate(index[1:], 9):
        book.clone_row("Test Cases", row_no, proto)
        for col, value in enumerate(row, 2):
            book.put("Test Cases", f"{chr(64 + col)}{row_no}", number(value))
        book.fit_height("Test Cases", row_no, row, [6, 45, 16, 75, 60])
    book.dimensions("Test Cases", "F", len(index) + 7)
    summary_counts = {}
    for sheet in FEATURE_SHEETS:
        proto_case, proto_bar = book.row_template(sheet, 12), book.row_template(sheet, 11)
        book.clear_rows(sheet, 11)
        book.put(sheet, "B2", summaries[sheet]["B2"])
        book.put(sheet, "B3", summaries[sheet]["B3"])
        row_no, current_fe = 11, None
        for feature, row, path in cases[sheet]:
            if feature != current_fe:
                book.clone_row(sheet, row_no, proto_bar)
                title = next(b.text for b in parse_markdown(path) if b.kind == "heading")
                book.put(sheet, f"A{row_no}", title)
                row_no += 1
                current_fe = feature
            book.clone_row(sheet, row_no, proto_case)
            for col, value in enumerate(row, 1):
                book.put(sheet, f"{chr(64 + col)}{row_no}", plain(value))
            if book.fit_height(sheet, row_no, row, [17, 34, 34, 34, 28, 9, 11, 7, 9, 11, 7, 9, 11, 7, 29]):
                warnings.append(f"Case {row[0]} reaches Excel's row-height limit; review for clipping")
            row_no += 1
        # Repair counters only in generated output, retaining original grouping bars.
        book.put(sheet, "B4", len(cases[sheet]), "COUNTA(A12:A1000)")
        summary_counts[sheet] = []
        for round_no, status_col in enumerate(("F", "I", "L"), 6):
            source_index = {"F": 5, "I": 8, "L": 11}[status_col]
            counts = Counter(row[source_index] for _, row, _ in cases[sheet])
            summary_counts[sheet].append(counts)
            for column, status in zip("BCDE", ("Passed", "Failed", "Pending", "N/A")):
                book.put(sheet, f"{column}{round_no}", counts[status],
                         f'COUNTIF(${status_col}$11:${status_col}$1000,{column}$5)')
        # The declared dimension must match the rows that actually exist. Claiming
        # row 12 on a sheet that ends at row 10 makes Excel treat the file as
        # damaged, so report the real last row.
        book.dimensions(sheet, "R", max(10, row_no - 1))
        # Extend only the status columns' dropdown to the new case range.
        # The template's sqref mixes several disjoint ranges (headers, sample
        # cells, data), so rewriting every range corrupts the validation and
        # Excel rejects the file.
        status_columns = "GHIJKLMN"
        for validation in descendants(book.sheet(sheet), "dataValidation"):
            sqref = validation.getAttribute("sqref")
            parts = []
            for part in sqref.split():
                match = re.fullmatch(r"([A-Z]+)(\d+):([A-Z]+)(\d+)", part)
                if match and match[1] == match[3] and match[1] in status_columns:
                    col = match[1]
                    parts.append(f"{col}11:{col}1000")
                else:
                    parts.append(part)
            validation.setAttribute("sqref", " ".join(parts))
    for coord, value in {
        "C3": cover["Project Name"], "C4": cover["Project Code"],
        "C5": cover.get("Document Code", "Not supplied"),
        "G3": cover.get("Creator", "Not supplied"), "G4": "Not supplied in report sources",
        "H5": date, "C6": stats_meta.get("Test round", "MF3-only executed slice"),
    }.items():
        book.put("Test Statistics", coord, value)
    # Test Statistics layout for N modules: header row 10, modules rows
    # 11..10+N, Sub total, blank, coverage, successful coverage.
    module_proto = book.row_template("Test Statistics", 12)
    subtotal_proto = book.row_template("Test Statistics", 14)
    spacer = book.row_template("Test Statistics", BLANK_SPACER_ROW)
    coverage_proto = book.row_template("Test Statistics", 16)
    success_proto = book.row_template("Test Statistics", 17)
    book.clear_rows("Test Statistics", 11)
    first_module_row = 11
    last_module_row = first_module_row + len(FEATURE_SHEETS) - 1
    subtotal_row = last_module_row + 1
    coverage_row = subtotal_row + 2
    success_row = subtotal_row + 3
    totals, total_cases = Counter(), 0
    for offset, sheet in enumerate(FEATURE_SHEETS):
        stat_row = first_module_row + offset
        book.clone_row("Test Statistics", stat_row, module_proto)
        counts = summary_counts[sheet][0]
        totals.update(counts)
        total_cases += len(cases[sheet])
        book.put("Test Statistics", f"B{stat_row}", offset + 1)
        book.put("Test Statistics", f"C{stat_row}", summaries[sheet]["B2"], f"'{sheet}'!B2")
        book.cell("Test Statistics", f"C{stat_row}").setAttribute("t", "str")
        for target_col, source_col, status in zip("DEFG", "BCDE", ("Passed", "Failed", "Pending", "N/A")):
            book.put("Test Statistics", f"{target_col}{stat_row}", counts[status], f"'{sheet}'!{source_col}6")
        book.put("Test Statistics", f"H{stat_row}", len(cases[sheet]), f"'{sheet}'!B4")
    book.clone_row("Test Statistics", subtotal_row, subtotal_proto)
    book.put("Test Statistics", f"C{subtotal_row}", "Sub total")
    # Materialise the blank spacer row so the sheet's rows stay contiguous;
    # Excel rejects a sheet whose rows jump. The template's own blank row
    # carries the spacing, so clone that rather than inventing one.
    book.clone_row("Test Statistics", coverage_row - 1, spacer)
    book.clone_row("Test Statistics", coverage_row, coverage_proto)
    book.clone_row("Test Statistics", success_row, success_proto)
    for column, status in zip("DEFG", ("Passed", "Failed", "Pending", "N/A")):
        book.put("Test Statistics", f"{column}{subtotal_row}", totals[status],
                 f"SUM({column}9:{column}{last_module_row})")
    book.put("Test Statistics", f"H{subtotal_row}", total_cases,
             f"SUM(H9:H{last_module_row})")
    denominator = total_cases - totals["N/A"]
    for row, label, numerator, formula in (
        (coverage_row, "Test coverage", totals["Passed"] + totals["Failed"],
         f"(D{subtotal_row}+E{subtotal_row})*100/(H{subtotal_row}-G{subtotal_row})"),
        (success_row, "Test successful coverage", totals["Passed"],
         f"D{subtotal_row}*100/(H{subtotal_row}-G{subtotal_row})"),
    ):
        book.put("Test Statistics", f"C{row}", label)
        book.put("Test Statistics", f"E{row}", numerator * 100 / denominator if denominator else 0,
                 f'IFERROR({formula},0)')
        book.put("Test Statistics", f"F{row}", "%")
    # The sheet grew past the template's 18 rows; Excel refuses a file whose
    # declared dimension contradicts the rows it actually contains.
    book.dimensions("Test Statistics", "H", success_row)
    workbook = book.package.xml("xl/workbook.xml")
    calc = descendants(workbook, "calcPr")
    if calc:
        calc[0].setAttribute("fullCalcOnLoad", "1")
        calc[0].setAttribute("forceFullCalc", "1")
        book.package.set_xml("xl/workbook.xml", workbook)
    audit = book.save(output, discard_stale_calculation_chain(book))
    unresolved = [key for key, value in cover.items() if "Enter " in value or "confirm with" in value]
    warnings.extend(f"Unresolved source metadata: {key}" for key in unresolved)
    warnings.append("Reviewer/Approver has no source value; not invented")
    return {**audit, "cases": total_cases, "round1": dict(totals),
            "case_ids": sorted(row[0] for group in cases.values() for _, row, _ in group),
            "warnings": warnings, "content_complete": True,
            "output_only_formula_repairs": ["count only case IDs", "round-specific status columns",
                                            "zero-denominator coverage guard", "cached calculated totals",
                                            "discard stale calculation chain"]}


if __name__ == "__main__":
    from export_common import run_single
    run_single("report5", TEMPLATE_NAME, SOURCES, export)
