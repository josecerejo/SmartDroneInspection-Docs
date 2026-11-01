# Report 5 template layout reference

This is a structural reference for the supplied workbook at
`capstone-official-docs/2_SEP490/Report5_Test Report.xlsx`. The copy in
`template/` must remain byte-for-byte unchanged unless the report owner
explicitly approves a new template version.

## Sheet order and used areas

The supplied workbook has five sheets and two feature sheets. At the user's
request, generated workbooks extend that source template with six cloned feature
sheets so Report 5 has one feature sheet for each Report 3 feature. The original
file in `template/` is unchanged. `Feature N` maps to `FE-0N` (Report 3 §§3.2–3.9).

| Order | Sheet name | Used area in the supplied template / generated output | Editable source |
| ---: | --- | --- | --- |
| 1 | `Cover` | `A2:F17` / content-driven through row 47 | `00-cover/cover.md`, `00-cover/record-of-changes.md` |
| 2 | `Test Cases` | `B1:F21` / content-driven | `01-test-cases/test-case-list.md` |
| 3 | `Test Statistics` | `A1:H18` / `A1:H22` with eight module rows | `02-test-statistics/test-statistics.md` |
| 4–11 | `Feature 1`–`Feature 8` | `A2:R19` / content-driven; one sheet per FE | Matching `03-features/fe-01` through `fe-08` source |

The generator clones the official feature-sheet layout, including its widths,
styles, print settings and metadata block. It adds no rows or columns to the
execution table; it adds worksheets because the SRS has eight product features.
Feature 1/2/7/8 have zero cases. Feature 3 contains three MF2 cases, and
Features 4/5/6 contain eight MF3 cases, including pending `WF3-010`, `WF3-011`
and `WF3-012`. Adding or
reordering an SRS FE requires updating case routing and the summary row together.

## `Cover`

The sheet contains project metadata followed by a record-of-change table. The
change table columns are, verbatim from row 10:

`Effective Date` · `Version` · `Change Item` · `*A,D,M` · `Change description` · `Reference`

Earlier drafts of these sources headed this table `A / D / M` and `Change
Description`. Those were normalised English, not the template's labels; the
template itself reads `*A,D,M` and `Change description`. Use the template's own
text so a copied value lands in a column whose header already matches.

## `Test Cases`

The sheet contains project/environment metadata and a case index with these
columns, in this exact order:

`No` · `Function Name` · `Sheet Name` · `Description` · `Pre-Condition`

The working source keeps all cases in one table, including cases that belong to
both business workflows represented by a feature sheet.

**Sheet-name spacing.** The template's own placeholder cells in `Sheet Name`
read `Feature1` and `Feature2` (no space, `D9:D13`), while the actual sheet tabs
are `Feature 1` and `Feature 2` (with a space). The Markdown sources use the
tab names with a space, because that is what identifies the destination sheet.
Whoever exports must not copy the unspaced placeholder into the cell: it would
point at a sheet that does not exist.

## `Test Statistics`

The module summary columns are:

`No` · `Module code` · `Passed` · `Failed` · `Pending` · `N/A` · `Number of  test cases`

Note the double space in the template's own last header — `H10` reads
`Number of  test cases`. The Markdown tables below spell it with single spacing
so they stay internally consistent; the spacing difference is cosmetic and does
not affect an export, because the workbook keeps its own header cell.

In the supplied template, module rows 11–12 contain formulas that point to
`Feature 1` and `Feature 2`. Generated workbooks extend the same mapping pattern
to rows 11–18, pointing row N+10 at sheet `Feature N`:

- Column `C` references the sheet's `B2` Feature name.
- Columns `D:G` reference `B6:E6`, the Round 1 status counts.
- Column `H` references `B4`, the number of test cases.

So `Module code` reports the SRS feature name in the sheet's `Feature` cell
(`B2`), not the workbook sheet name. The generated workbook has eight module
rows. `Sub total` moves to row 19 and sums the eight feature rows; coverage is
computed from it at rows 21–22:

- `Test coverage` = `(Passed + Failed) * 100 / (Number of TCs - N/A)`
- `Test successful coverage` = `Passed * 100 / (Number of TCs - N/A)`

With eleven cases (8 `Passed`, 3 `Pending`, no `Failed` or `N/A`), both formulas
evaluate to 72.73%; pending cases remain in the denominator. These rates cover
the recorded cases only. Keep workbook formulas; change underlying statuses.

## Feature sheets (supplied template and generated workbook)

The supplied template's `Feature 1` and `Feature 2`, and the six cloned sheets
in generated outputs, use the same test execution columns:

`Test Case ID` · `Test Case Description` · `Test Case Procedure` ·
`Expected Results` · `Pre-conditions` · `Round 1` · `Test date` · `Tester` ·
`Round 2` · `Test date` · `Tester` · `Round 3` · `Test date` · `Tester` · `Note`

The used range also extends to `R`, but only `A10:O10` are execution headers.
The three trailing columns are **not** additional case fields:

| Column | Content | Border |
| --- | --- | --- |
| `P` | empty | none |
| `Q` | empty, but `Q10` carries a background fill | none |
| `R` | `R2:R5` hold the status legend `Passed`, `Failed`, `Pending`, `N/A` | none |

`R2:R5` is a legend, not data: it repeats the four status words the round
summary above counts. It sits outside the bordered summary block, which spans
`A2:E8` only, and outside the bordered case table, which spans `A10:O…`. The
`Q10` fill is a leftover — the cell has no header text and no border.

Leave `P:R` alone. Copying a case row into `P:Q` would push content past the
table's right edge, and typing over `R2:R5` would destroy the legend.

Each sheet groups rows under `Function A`, `Function B`, and so on. The eight
Markdown feature sources are separated by FE code; workbook rows are combined
from those files only when exporting. Each case retains its FE and WF codes.

### Per-sheet summary block (`A2:E8`)

Every generated feature sheet repeats this block above the case table, fully
bordered (`B2:E2`, `B3:E3` and `B4:E4` are merged), and `Test Statistics` reads
its values back out by formula:

| Cell | Label | Formula |
| --- | --- | --- |
| `A2`/`B2` | `Feature` | Feature name, e.g. `MF3 inspection evidence, findings and reporting` |
| `A3`/`B3` | `Test requirement` | One-line description of what this sheet tests |
| `A4`/`B4` | `Number of TCs` | Supplied template: `=COUNTA(A12:A1000)` / `=COUNTA(A12:A998)`. Generated copies count only stable WFx case IDs in `A11:A1000`, excluding FE function bars. |
| `A5:E5` | `Testing Round` | Column headers `Passed`, `Failed`, `Pending`, `N/A` |
| `A6`/`B6:E6` | `Round 1` | `=COUNTIF($F10:$F998, B5)` etc. |
| `A7`/`B7:E7` | `Round 2` | Same range, Round 2 |
| `A8`/`B8:E8` | `Round 3` | Same range, Round 3 |

`Number of TCs` and the per-round counts are workbook formulas over the case
rows, so they need no Markdown source. `Feature` name and `Test requirement`
are typed values with no formula behind them, and the Markdown equivalent is
the `Feature sheet summary` table in each matching `fe-0N-…md` file. Populate
`B2`/`B3` on every sheet, including those with zero cases, because the
`Test Statistics` module rows read every `Feature N!B2` regardless.

| FE source | Workbook destination | Stable case IDs |
| --- | --- | --- |
| FE-01 Authentication, Google OAuth2 & 5-Role Access Control (§3.2) | `Feature 1` | WF1-001 to WF1-005 (5 cases) |
| FE-02 Partner Onboarding, Workforce, Asset & Inspector Drone Registry (§3.3) | `Feature 2` | WF1-006 to WF1-016 (11 cases) |
| FE-03 Recurring Schedules, Contract Occurrences & Outbox Notifications (§3.4) | `Feature 3` | WF1-017 to WF1-021 (5 cases) |
| FE-04 Service Requests, Quotations, Contracts, Dispatch & Airspace Map (§3.5) | `Feature 4` | WF2-001 to WF2-005 (5 cases) |
| FE-05 Flight Permit Gate, Field Execution, Dashboard & Calendar (§3.6) | `Feature 5` | WF2-008, WF2-009, WF2-011, WF2-012, WF2-015 to WF2-020, WF3-009 (11 cases) |
| FE-06 Evidence Intake, YOLO11 Detection, Auto-Compiled Report & PayOS (§3.7) | `Feature 6` | WF3-001 to WF3-008, WF3-010, WF3-012, WF3-016, WF3-017 (12 cases) |
| FE-07 Maintenance Work Orders, RAG Scope/Norms Advisor & Repair Execution (§3.8) | `Feature 7` | WF4-001 to WF4-011 (11 cases) |
| FE-08 Completion Report, 3-Way Re-inspection Verification & Cost Closure (§3.9) | `Feature 8` | WF4-012 to WF4-016 (5 cases) |

The FE-xx codes are Report 3's own, one per section 3.2–3.9. Report 5 does not
invent them. See `README.md` for the full code-to-section table.

The sheet names are generated presentation labels; the exported mapping is
explicit: sheet `Feature N` corresponds to SRS `FE-0N`. All 65 cases are
distributed across `Feature 1` through `Feature 8` (`5 + 11 + 5 + 5 + 11 + 12 + 11 + 5 = 65`):

| Workbook sheet | Included SRS feature | Included WF IDs |
| --- | --- | --- |
| `Feature 1` | FE-01 — Authentication, Google OAuth2 & 5-Role Access Control | WF1-001 to WF1-005 |
| `Feature 2` | FE-02 — Partner Onboarding, Workforce, Asset & Inspector Drone Registry | WF1-006 to WF1-016 |
| `Feature 3` | FE-03 — Recurring Schedules, Contract Occurrences & Outbox Notifications | WF1-017 to WF1-021 |
| `Feature 4` | FE-04 — Service Requests, Quotations, Contracts, Dispatch & Airspace Map | WF2-001 to WF2-005 |
| `Feature 5` | FE-05 — Flight Permit Gate, Field Execution, Dashboard & Calendar | WF2-008, WF2-009, WF2-011, WF2-012, WF2-015 to WF2-020, WF3-009 |
| `Feature 6` | FE-06 — Evidence Intake, YOLO11 Detection, Auto-Compiled Report & PayOS | WF3-001 to WF3-008, WF3-010, WF3-012, WF3-016, WF3-017 |
| `Feature 7` | FE-07 — Maintenance Work Orders, RAG Scope/Norms Advisor & Repair Execution | WF4-001 to WF4-011 |
| `Feature 8` | FE-08 — Completion Report, 3-Way Re-inspection Verification & Cost Closure | WF4-012 to WF4-016 |

There are exactly eight FE-specific Markdown source files. The supplied
workbook has two feature sheets; generated workbooks have eight output sheets,
one for each source file. Neither sheet names nor source filenames replace the
stable SRS feature codes. Removed case IDs (`WF1-*`, `WF2-001`–`WF2-007`,
`WF3-001`, `WF3-004`, `WF3-007`, `WF3-008`, `WF4-*`) stay reserved and are never
reused; `WF2-008` and `WF2-009` are active FE-03 case IDs. `WF3-010`, `WF3-011`
and `WF3-012` are active Pending MF3 cases; subsequent MF3 cases continue from
`WF3-013`. FE-02/MF1, the remaining MF2 boundaries, FE-07/MF4 and FE-08
remain coverage gaps; cases may cover only implemented behavior.

## Visual and status rules

- Preserve the template's header, function bars, section bars, borders, merged
  cells, and spacing. The named colours in earlier drafts of this file
  ("dark navy", "green", "light-blue") were never verified against a rendered
  sheet and are deliberately not restated here as facts. Open the workbook and
  copy the existing cell styles; do not re-create them from a description.
- Status values are exactly `Passed`, `Failed`, `Pending`, or `N/A`.
- Dates use `YYYY-MM-DD`.
- Do not put credentials, tokens, private keys, or personal secrets in any
  case description, note, or evidence reference.

### Metadata blocks to fill on export

Each sheet has a metadata area above its table. `Cover` has **no merge** on
`Version` — it is a plain label/value pair at `E6`, unlike the merged value
cells beside it:

| Sheet | Merged cells | Labels and their value cells |
| --- | --- | --- |
| `Cover` | `B2:F2`, `B4:D4`, `B5:D5`, `B6:D6` | `TEST REPORT DOCUMENT`; `Project Name` `B4`, `Project Code` `B5`, `Document Code` `B6` (formula), `Creator` `E4`, `Issue Date` `F5`, `Version` `E6` (**not merged** — its value goes in `F6`) |
| `Test Cases` | `B3:C3`, `B4:C4`, `B5:C5`, `D3:F3`, `D4:F4`, `D5:F5` | `Project Name` `D3` (`#REF!`), `Project Code` `D4` (`#REF!`), `Test Environment Setup Description` `D5` |
| `Test Statistics` | `B1:H1`, `C3:D3`, `C4:D4`, `C5:D5`, `C6:H6`, `E3:F3`, `E4:F4`, `E5:F5` | `TEST STATISTICS`; `Project Name` `C3`, `Project Code` `C4`, `Document Code` `C5` (formula), `Notes` `C6`, `Creator` `E3`, `Reviewer/Approver` `E4`, `Issue Date` `H5` |

`Creator` and `Reviewer/Approver` are still placeholders in the Markdown
(`*Enter team/member name*`) and need real names before submission. So is
`Version` on `Cover` — the label sits at `E6` with no merge, so the text goes in
`F6`, not `E6`.

`Cover!B6` and `Test Statistics!C5` are document-code formulas built from the
project code, so they are derived rather than typed. Both currently produce
`..._XXX_vx.x`; the `XXX` segment needs a real document code.

## Pre-existing template issues

These were verified by reading the workbook directly. `template/` is
byte-for-byte identical to the supplied workbook (both SHA-256
`DE84DD6F…F4D1`), so the same defects exist in both copies.

1. **`Test Cases!D3` and `D4` are `=#REF!`.** The project name and project code
   on the `Test Cases` sheet do not resolve.
2. **A defined name `ACTION` points to `#REF!`,** at workbook level and again
   scoped to `Cover`. It appears to be an unused leftover from an earlier
   macro.
3. **Both feature sheets' Round 2 and Round 3 summary rows count the Round 1
   column.** `Feature 1` `B7:E7` and `B8:E8` use `=COUNTIF($F10:$F998, …)`, the
   same `$F` range as Round 1 (`$F` is the `Round 1` status column). `Feature 2`
   does the same with `$F10:$F996`. Column `$I` holds Round 2 and `$L` holds
   Round 3, so the Round 2/3 summaries currently mirror Round 1 instead of
   counting their own column.
4. **`Feature 2!A18` holds a stray `6`** below the last case row, where the
   template expects a case ID or a `Function` bar. `COUNTA(A12:A998)` on that
   sheet counts it as a seventh test case, so a naive export reports 6 or 7
   cases instead of 5. It is almost certainly a template editing leftover.

Issue 3 is a genuine template bug, but correcting it changes the supplied
workbook and therefore needs the report owner's approval. Issues 1, 2 and 4
are placeholder artifacts of the blank template; when exporting, enter real
values in `Test Cases!D3`/`D4`, and make sure the stray `A18` value is removed
or replaced so `Number of TCs` counts only real cases.

The `Test Statistics` sheet also carries a cosmetic double space in header
`H10` (`Number of  test cases`), reproduced verbatim above. Leave the
workbook cell as-is; only the Markdown spelling is normalised.

## Generated copies

The independent exporter [export_report5.py](../../tools/export_report5.py)
uses this original workbook as a read-only format source. It clones the
original case/function/history row styles, preserving sheet names, column
order, widths, legend, comments, printer settings and theme/style parts.

In output copies only, case totals use `COUNTIF` over stable WFx IDs so
function bars are not counted as cases; Round 2/3 use the `I`/`L` status
columns, and zero-case coverage is guarded. The template calculation chain
contains references to metadata formulas replaced by source values; it is
removed with its relationship/content-type entry so Excel can rebuild that
non-format index. No original template is modified.

Source round fields are exported positionally, keeping all repeated date and
tester columns. Long cells may reach Excel's 409-point row-height limit;
these are reported as warnings, not declared visually verified. See
[export tooling](../../tools/README.md) for independent commands and Office
verification.
