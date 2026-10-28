import csv
import unittest
from io import StringIO

from experiments.maps import core_cases, manifest_csv
from experiments.protocol import ALGORITHMS, PILOT_IDS, algorithm_order, pilot_cases, size_cases, size_extra_cases, size_manifest_csv, suite_cases


class ProtocolTests(unittest.TestCase):
    def test_size_cases_and_reuse(self):
        cases = size_cases()
        self.assertEqual(len(cases), 36)
        self.assertEqual(len(size_extra_cases()), 24)
        self.assertEqual(len({case.case_id for case in cases}), 36)
        size_rows = list(csv.DictReader(StringIO(size_manifest_csv())))
        core_rows = {row["case_id"]: row for row in csv.DictReader(StringIO(manifest_csv()))}
        self.assertEqual(sum(row["source"] == "core_reuse" for row in size_rows), 12)
        self.assertEqual(sum(row["source"] == "additional" for row in size_rows), 24)
        for row in size_rows:
            if row["source"] == "core_reuse":
                self.assertEqual({key: value for key, value in row.items() if key != "source"}, core_rows[row["case_id"]])

    def test_pilot_and_order(self):
        self.assertEqual(tuple(case.case_id for case in pilot_cases()), PILOT_IDS)
        self.assertEqual(len(core_cases()), 72)
        self.assertEqual({case.case_id for case in suite_cases("size_extra")}, {case.case_id for case in size_extra_cases()})
        self.assertEqual(suite_cases("core"), suite_cases("core"))
        for case_index in range(8):
            orders = [algorithm_order(case_index, repeat) for repeat in range(3)]
            for algorithm in ALGORITHMS:
                self.assertEqual(sorted(order.index(algorithm) for order in orders), [0, 1, 2])


if __name__ == "__main__":
    unittest.main()
