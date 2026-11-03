import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from support import OFFICIAL, REPORTS, original
from export_report5 import TEMPLATE_NAME, export, validate_cases
from report_ooxml import Spreadsheet, sha256


class Report5Tests(unittest.TestCase):
    def test_repeated_round_fields_remain_positional(self):
        cases, _, summaries = validate_cases(REPORTS / "report-5-test-report")
        # WF3-002 is FE-06, so it lands on the sheet for feature 6.
        row = next(row for _, row, _ in cases["Feature 6"] if row[0] == "WF3-002")
        self.assertEqual(len(row), 15)
        self.assertEqual(row[5:8], ["Passed", "2026-10-11", "Claude Code (automated)"])
        self.assertEqual(row[8:14], ["Pending", "", "", "Pending", "", ""])
        for case_id in ("WF3-006", "WF3-016"):
            case_row = next(row for _, row, _ in cases["Feature 6"] if row[0] == case_id)
            self.assertEqual(case_row[5:8][0], "Passed")
            self.assertEqual(case_row[8:11], ["Pending", "", ""])
            self.assertEqual(case_row[11:14], ["Passed", "2026-11-03", "Claude Code (automated)"])
        self.assertEqual(summaries["Feature 6"]["B2"],
                         "Evidence Intake, YOLO11 Detection, Auto-Compiled Report & PayOS")

    def test_workbook_has_correct_metadata_rounds_styles_and_calculation_chain(self):
        template = original(OFFICIAL, TEMPLATE_NAME)
        initial_hash = sha256(template.read_bytes())
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / TEMPLATE_NAME
            result = export(template, REPORTS, output)
            self.assertEqual(result["cases"], 65)
            self.assertTrue(result["format_parts_preserved"])
            book, source = Spreadsheet(output), Spreadsheet(template)
            self.assertEqual(list(book.sheets)[:5],
                             ["Cover", "Test Cases", "Test Statistics", "Feature 1", "Feature 2"])
            self.assertEqual(book.value("Feature 6", "B2"),
                             "Evidence Intake, YOLO11 Detection, Auto-Compiled Report & PayOS")
            for coord, expected in {"G12": "2026-10-11", "H12": "Claude Code (automated)",
                                    "J12": "", "K12": "", "M12": "", "N12": "",
                                    "B4": "12", "B6": "10", "B7": "0", "D7": "12", "D8": "10"}.items():
                self.assertEqual(book.value("Feature 6", coord), expected, coord)
            self.assertTrue(book.value("Feature 6", "A11").startswith("FE-06"))
            self.assertEqual(book.value("Feature 6", "A12"), "WF3-002")
            self.assertEqual(book.value("Feature 6", "A17"), "WF3-017")
            self.assertEqual(book.value("Feature 6", "F17"), "Pending")
            self.assertEqual(book.value("Feature 6", "I17"), "Pending")
            self.assertEqual(book.value("Feature 6", "L17"), "Pending")
            self.assertEqual(book.value("Feature 6", "A19"), "WF3-005")
            self.assertEqual(book.value("Test Statistics", "H19"), "65")
            self.assertAlmostEqual(float(book.value("Test Statistics", "E21")), 92.31, places=2)
            self.assertAlmostEqual(float(book.value("Test Statistics", "E22")), 92.31, places=2)
            self.assertEqual(book.value("Cover", "E4"), "Creator")
            self.assertEqual(book.value("Test Statistics", "C3"), "SmartDroneInspection")
            self.assertNotIn("<List enviroment", book.value("Test Cases", "D5"))
            self.assertEqual(book.cell("Feature 6", "C12").getAttribute("s"),
                             source.cell("Feature 2", "C12").getAttribute("s"))
            self.assertEqual(book.cell("Feature 6", "C13").getAttribute("s"),
                             source.cell("Feature 2", "C12").getAttribute("s"))
            self.assertEqual(book.cell("Feature 6", "A11").getAttribute("s"),
                             source.cell("Feature 2", "A11").getAttribute("s"))
            with ZipFile(template) as original_zip, ZipFile(output) as output_zip:
                for part in ("xl/styles.xml", "xl/sharedStrings.xml", "xl/theme/theme1.xml"):
                    self.assertEqual(original_zip.read(part), output_zip.read(part), part)
                self.assertNotIn("xl/calcChain.xml", output_zip.namelist())
                self.assertNotIn(b"calcChain", output_zip.read("xl/_rels/workbook.xml.rels"))
        self.assertEqual(sha256(template.read_bytes()), initial_hash)


if __name__ == "__main__":
    unittest.main()
