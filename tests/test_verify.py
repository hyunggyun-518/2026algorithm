import csv
import json
import unittest
from copy import deepcopy

from experiments.measure import ROOT
from experiments.verify import verify, verify_file


class VerifyTests(unittest.TestCase):
    def test_core_artifacts(self):
        self.assertEqual(verify_file(ROOT / "data/raw/core_v1.csv", "core"), {"cases": 72, "rows": 648, "groups": 216})

    def test_pilot_artifacts_and_tampering(self):
        with (ROOT / "data/raw/pilot_v1.csv").open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        with (ROOT / "data/raw/pilot_v1.meta.json").open(encoding="utf-8") as stream:
            meta = json.load(stream)
        with (ROOT / "data/core_manifest.csv").open(encoding="utf-8", newline="") as stream:
            manifest = list(csv.DictReader(stream))
        self.assertEqual(verify(rows, meta, manifest, "pilot"), {"cases": 3, "rows": 27, "groups": 9})
        altered = deepcopy(rows)
        altered[0]["cost"] = str(int(altered[0]["cost"]) + 1)
        with self.assertRaises(ValueError):
            verify(altered, meta, manifest, "pilot")
        with self.assertRaises(ValueError):
            verify(rows[:-1], meta, manifest, "pilot")


if __name__ == "__main__":
    unittest.main()
