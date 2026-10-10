"""Medeu Ice: тесты бизнес-правил для данных."""
import csv
import json
import unittest
from pathlib import Path
 
ROOT = Path(__file__).resolve().parent.parent
with open(ROOT / "data" / "records.csv", encoding="utf-8-sig", newline="") as f:
    ROWS = list(csv.DictReader(f))
 
COLUMNS = ["sale_id", "session", "ticket", "qty", "price", "buyer"]
PRICE = {"adult": 2500, "student": 1500, "child": 1200}
CAPACITY = 120
 
 
class DataRulesTest(unittest.TestCase):
    def test_columns(self):
        self.assertEqual(list(ROWS[0].keys()), COLUMNS)
 
    def test_own_records_added(self):
        self.assertGreaterEqual(len(ROWS), 35, "добавьте свои 5 записей в конец records.csv")
 
    def test_report_created(self):
        report = json.loads((ROOT / "out" / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["records"], len(ROWS))
        self.assertEqual(len(report["control_code"]), 8)
 
    def test_price_matches_ticket(self):
        for line, r in enumerate(ROWS, start=2):
            with self.subTest(line=line):
                self.assertIn(r["ticket"], PRICE)
                self.assertEqual(int(r["price"]), PRICE[r["ticket"]])
 
    def test_qty_positive(self):
        for line, r in enumerate(ROWS, start=2):
            with self.subTest(line=line):
                self.assertGreater(int(r["qty"]), 0)
 
    def test_session_not_overbooked(self):
        sold = {}
        for r in ROWS:
            sold[r["session"]] = sold.get(r["session"], 0) + int(r["qty"])
        for session, qty in sold.items():
            with self.subTest(session=session):
                self.assertLessEqual(qty, CAPACITY)
 
 
if __name__ == "__main__":
    unittest.main()
