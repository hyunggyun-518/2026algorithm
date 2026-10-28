import csv
import unittest
from io import StringIO

from experiments.maps import MapCase
from experiments.measure import RAW_FIELDS, check_manifests, measure_cases, rows_csv, validate_rows
from experiments.summarize import summarize


class MeasureTests(unittest.TestCase):
    def test_manifests(self):
        check_manifests()

    def test_small_case_complete_and_valid(self):
        cases = (MapCase("open", "near", 11, 0),)
        rows = measure_cases(cases)
        validate_rows(rows, cases)
        self.assertEqual(len(rows), 9)
        self.assertEqual(set(rows[0]), set(RAW_FIELDS))
        self.assertEqual({row["cost"] for row in rows}, {rows[0]["cost"]})
        self.assertEqual(sorted(row["order_position"] for row in rows if row["algorithm"] == "astar"), [1, 2, 3])
        parsed = list(csv.DictReader(StringIO(rows_csv(rows))))
        self.assertEqual(len(parsed), 9)
        self.assertEqual(len(list(csv.DictReader(StringIO(summarize(parsed))))), 3)

    def test_duplicate_and_missing_rejected(self):
        cases = (MapCase("open", "near", 11, 0),)
        rows = measure_cases(cases)
        with self.assertRaises(ValueError):
            validate_rows(rows[:-1], cases)
        with self.assertRaises(ValueError):
            summarize(list(csv.DictReader(StringIO(rows_csv(rows[:-1])))))


if __name__ == "__main__":
    unittest.main()
