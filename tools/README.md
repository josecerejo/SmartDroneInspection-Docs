# Report export tools

## Content and formatting sources

- **Content:** the editable Markdown under `../reports/`.
- **Formatting:** the original files in `../../capstone-official-docs/`.
- The older DOCX copies inside `reports/` are **not** format templates.
- Original files and Markdown sources are read-only inputs. Outputs go into a
  new `reports/generated/<run>/` directory; existing output paths are refused.

## Generate

Python 3.10+ is sufficient; no pip packages are needed. From the docs repository:

Each report owns its source mapping and validations in a separate exporter:

```text
tools/
  export_report1.py    Project Introduction
  export_report2.py    Project Management Plan
  export_report3.py    Seven-part SRS
  export_report5.py    Test workbook and three-round evidence
  export_weekly.py     Weekly tables, one workbook per week
  export_all.py        Calls exporters and collects the manifest only
  export_common.py     Shared input/output safety and Word rendering
  report_ooxml.py      Markdown parsing and original-package/style preservation
  tests/              One suite per report, plus shared-safety tests
```

```powershell
# Export one report independently:
python -I tools/export_report1.py
python -I tools/export_report2.py
python -I tools/export_report3.py
python -I tools/export_report5.py --output reports/generated/report5-preview
python -I tools/export_weekly.py --week week-05

# Export every report with available sources:
python -I tools/export_all.py --list
python -I tools/export_all.py
python -I tools/export_all.py --only report1 report2 report3 report5 weekly
python -I tools/export_all.py --templates "E:/Dev/Repos/Capstone/capstone-official-docs" --output "reports/generated/my-preview"
```

`export_reports.py` and `report5_export.py` are compatibility names only; they
contain no report-filling logic. The old `--out file.xlsx` interface is replaced
with `--output directory`, which refuses an existing output directory. This
avoids overwriting an Office workbook already open or edited by someone.

### Current source coverage

| Official artifact | Source | Result |
| --- | --- | --- |
| Report 1 Project Introduction | `report-1-project-introduction/report1-project-introduction.md` | Generated DOCX |
| Report 2 Project Management Plan | `report-2-project-management-plan/report2-project-management-plan.md` | Generated DOCX |
| Report 3 SRS (`FE-01`–`FE-08`) | Six ordered sources in `report-3-software-requirement-specification/` | Generated DOCX |
| Report 3 Project Tracking | `project-tracking/project-tracking.md` | Generated XLSX |
| Report 4 SDD | Detailed-design sources `00-record-of-changes` through `03-detailed-design` (as mapped in `export_report4.py`) + rendered Mermaid PNGs | Generated DOCX |
| Report 5 Test Documentation | Two ordered sources in `report-5-test-documentation/` | Generated DOCX |
| Report 5 Test Report (`Feature 1`–`Feature 8`) | Cover/history, case index (`65` cases), statistics and eight FE sources (`fe-01`–`fe-08`) | Generated XLSX |
| Review 2 Submission Pack (`BM01`–`BM04`) | `review-2-registration/`, `review-2-design-brief/`, `review-2-self-review/` (`export_review2_pack.py`) | Generated DOCX |
| Project Weekly Report | `weekly-project-reports/week-01.md` through `week-07.md` | One XLSX per week |

Student guides, sample schedules and example reference images are not report
content sources. The generator does not invent new requirements, test results,
work logs, people or reports. It preserves the source text even when older
reports describe an earlier product baseline.

## Fidelity contract

The exporter copies each original Office ZIP package and changes only relevant
content XML. Unchanged members are copied byte-for-byte. The manifest lists all
changed/added package parts, original SHA-256, sources, content counts and
warnings. Styles, numbering, themes, fonts, headers/footers, original media,
printer settings and unrelated relationships are preserved.

New paragraphs/cells/table rows are cloned from actual template elements;
additional content is not written into unstyled rows. Section/page settings,
existing sheet names/order, column widths and style IDs remain original.

**This does not promise identical pagination.** Different content necessarily
changes pages and row heights. A table with a different number of columns keeps
the original total width and redistributes it. These content-driven changes are
reported separately from package/style preservation.

### Report 5 safeguards

- The supplied template has two feature sheets. Generated copies clone this
  layout to eight sheets, `Feature 1`–`Feature 8`, mapped one-to-one to Report 3
  `FE-01`–`FE-08`. The original workbook is read-only and is never modified.
  Zero-case sheets remain present so the generated workbook matches the SRS.
- Each generated sheet keeps its own worksheet relationships; comments and
  their VML anchors from the source sheet are not copied to the clones.
- Test Statistics has eight module rows, Sub total at row 19 and coverage at
  rows 21–22. The Office verifier checks all eight sheets and recomputes the
  totals from the source statuses.
- Execution rows are positional: all 15 fields survive, including repeated
  `Test date` and `Tester` fields for each of the three rounds.
- The case index determines the destination sheet and FE ownership. Duplicate,
  missing or mismapped case IDs fail generation.
- Passed/Failed rounds require date/tester; Pending rounds cannot pretend to
  have execution metadata. Recorded statistics must reconcile with case rows.
- FE grouping bars keep their original style. In **output copies only**, case
  totals count real WFx IDs instead of grouping bars; Round 2/3 count `I`/`L`
  instead of incorrectly reusing `F`. Zero-case coverage has a denominator
  guard. Formula caches are generated from source statuses, then checked by
  Excel automation when requested.
- Genuine missing creator/reviewer/document-code metadata stays explicit and
  is listed in warnings. No names are invented.
- Source status, date, tester and evidence are not changed by exporting.
- The stale template calculation chain is removed only in generated copies,
  together with its relationship/content-type entry. Excel rebuilds this
  non-format index; retaining references to cells changed from formulas to
  literals makes Excel reject the workbook. Styles and printer settings stay
  byte-identical.

### Known content/rendering limitations

- Mermaid fenced diagrams are retained as source text, not silently dropped.
  They are flagged in the manifest; rendered diagrams need a separately
  configured renderer before submission.
- Report 3 historical change rows with extra reference cells are joined into
  the final description cell, preserving all text and the official column
  count. The source mismatch is reported.
- Excel has a 409-point row-height limit. Long evidence/history cells reaching
  this limit are warned and must be visually checked in PDF/Excel.
- The old `2026-10-10-export.xlsx` in Report 5 outputs is an earlier unvalidated
  preview and is not an output of this generator.

## Source readability

Markdown is a source format, not a rendering target. Three rules keep the
generated document readable, and `tests/test_readability.py` enforces them:

- **List markers never reach the page.** A `-` item becomes a real Word list
  (`ListParagraph` + `numPr` on the template's own numbering definition),
  not a paragraph whose first character happens to be a dash.
- **One blank line does not end a table.** Long change rows are often followed
  by a stray blank line in the editor; `read_table()` continues across it so a
  table cannot silently dump half its rows into the document as prose.
- **A list item carries exactly one `numPr`.** Cloning a template list must
  drop the inherited numbering element, or Word resolves the list ambiguously.

Table header cells keep the template's `HeadingLv1` style. That style has no
`outlineLvl`, so header text stays out of the table of contents; changing it
would alter the official formatting.

`apply_role_wording.py` applies configured human-readable role wording to Report 3 prose while leaving the enum inside backticks, the actor table and diagram source unchanged.
It is a one-off editorial pass, not part of generation:

```powershell
python -I tools/apply_role_wording.py            # dry run, reports counts
python -I tools/apply_role_wording.py --apply    # write
```

## Verify

```powershell
python -I -m unittest discover -s tools/tests -p "test_*.py" -v
# Run just one report's suite:
python -I -m unittest discover -s tools/tests -p test_report5.py -v
git diff --check
```

For Windows with Microsoft Word and Excel installed:

```powershell
./tools/verify_office_reports.ps1 -OutputDirectory reports/generated/my-preview
# Optional, only with working Office PDF export:
./tools/verify_office_reports.ps1 -OutputDirectory reports/generated/my-preview -ExportPdf
```

The Office verifier opens only generated outputs read-only, disables macros and
external-link updates, refreshes Word's TOC in memory, recalculates Excel and
checks Report 5 totals/rounds/coverage. It writes an `office-verification.json`
report; `-ExportPdf` additionally writes PDF previews. PDF export is optional
because some Office installations block or hang that COM operation. The
verifier closes without saving Office changes back into the master generated
files and checks their hashes stayed unchanged.

Generated directories are ignored by Git. Commit the tools and documentation,
not previews, PDFs, caches or generated Office packages.

## Review 2 Deliverables Synchronization
Reports 1-5, Project Tracking, Weekly Reports, and Review 2 Forms synchronized with the 12-feature architecture and full 31-table typed ERD.
