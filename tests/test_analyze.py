import csv
import unittest
import xml.etree.ElementTree as ElementTree
from io import StringIO

from experiments.analyze import generate
from experiments.measure import ROOT
from experiments.verify import verify_file


class AnalyzeTests(unittest.TestCase):
    def test_size_extra_artifacts(self):
        self.assertEqual(verify_file(ROOT / "data/raw/size_extra_v1.csv", "size_extra"), {"cases": 24, "rows": 216, "groups": 72})

    def test_generated_analysis(self):
        outputs = generate()
        self.assertEqual(len(outputs), 8)
        for path, content in outputs.items():
            self.assertEqual(path.read_text(encoding="utf-8"), content)
        cases = list(csv.DictReader(StringIO(outputs[ROOT / "data/analysis/case_metrics.csv"])))
        core = list(csv.DictReader(StringIO(outputs[ROOT / "data/analysis/core_group_summary.csv"])))
        size = list(csv.DictReader(StringIO(outputs[ROOT / "data/analysis/size_group_summary.csv"])))
        self.assertEqual(len(cases), 288)
        self.assertEqual(len(core), 12)
        self.assertEqual(len(size), 12)
        self.assertEqual(sum(row["source"] == "core_reuse" for row in size), 4)
        maze_near_astar = next(row for row in core if row["terrain"] == "maze" and row["distance"] == "near" and row["algorithm"] == "astar")
        self.assertGreater(float(maze_near_astar["time_ratio_median"]), 2)
        self.assertLess(float(maze_near_astar["expanded_ratio_median"]), 1)
        barrier_far_bidirectional = next(row for row in core if row["terrain"] == "barrier" and row["distance"] == "far" and row["algorithm"] == "bidirectional_dijkstra")
        self.assertEqual(int(barrier_far_bidirectional["time_wins"]), 8)
        for path, content in outputs.items():
            if path.suffix == ".svg":
                root = ElementTree.fromstring(content)
                self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")


if __name__ == "__main__":
    unittest.main()
