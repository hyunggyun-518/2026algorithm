import argparse
import csv
from collections import defaultdict
from io import StringIO
from pathlib import Path
from statistics import median

from .protocol import ALGORITHMS, REPEATS

SUMMARY_FIELDS = ("case_id", "algorithm", "median_elapsed_ns", "min_elapsed_ns", "max_elapsed_ns", "expanded", "cost")


def summarize(rows: list[dict[str, str]]) -> str:
    groups = defaultdict(list)
    for row in rows:
        groups[(row["case_id"], row["algorithm"])].append(row)
    output = StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(SUMMARY_FIELDS)
    for case_id, algorithm in sorted(groups):
        group = groups[(case_id, algorithm)]
        if algorithm not in ALGORITHMS or sorted(int(row["repeat"]) for row in group) != list(range(1, REPEATS + 1)):
            raise ValueError("missing or duplicate repetitions")
        if len({row["expanded"] for row in group}) != 1 or len({row["cost"] for row in group}) != 1:
            raise ValueError("non-deterministic counters or cost")
        times = [int(row["elapsed_ns"]) for row in group]
        if any(time <= 0 for time in times):
            raise ValueError("non-positive elapsed time")
        writer.writerow((case_id, algorithm, int(median(times)), min(times), max(times), group[0]["expanded"], group[0]["cost"]))
    cases = {case_id for case_id, _ in groups}
    if set(groups) != {(case_id, algorithm) for case_id in cases for algorithm in ALGORITHMS}:
        raise ValueError("incomplete algorithm groups")
    return output.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    with args.input.open(encoding="utf-8", newline="") as stream:
        result = summarize(list(csv.DictReader(stream)))
    print(result, end="")


if __name__ == "__main__":
    main()
