import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from .measure import RAW_FIELDS, ROOT, check_manifests
from .protocol import ALGORITHMS, PROTOCOL_VERSION, REPEATS, algorithm_order, suite_cases

CASE_FIELDS = ("case_id", "terrain", "distance", "size", "seed", "grid_sha256", "manhattan_steps", "shortest_steps", "walkable_cells")
COUNTER_FIELDS = ("cost", "path_steps", "expanded", "pq_pushes", "pq_pops")


def verify(rows: list[dict[str, str]], meta: dict, manifest_rows: list[dict[str, str]], suite: str) -> dict[str, int]:
    cases = suite_cases(suite)
    selected = {case.case_id for case in cases}
    manifest = {row["case_id"]: row for row in manifest_rows if row["case_id"] in selected}
    if len(manifest) != len(cases):
        raise ValueError("manifest cases missing")
    if suite == "size_extra" and any(row.get("source") != "additional" for row in manifest.values()):
        raise ValueError("size suite must contain only additional cases")
    if meta.get("protocol_version") != PROTOCOL_VERSION or meta.get("suite") != suite:
        raise ValueError("wrong protocol or suite")
    if meta.get("repeats") != REPEATS or meta.get("warmups_per_algorithm_case") != 1:
        raise ValueError("wrong measurement repetitions")
    if meta.get("case_ids") != [case.case_id for case in cases]:
        raise ValueError("wrong case order in metadata")
    if meta.get("timer") != "perf_counter_ns" or meta.get("algorithm_order") != "rotate by (case_index + repeat_index) mod 3":
        raise ValueError("wrong timing or algorithm order policy")
    if meta.get("case_order") != "sha256(case-order-v1:case_id) ascending":
        raise ValueError("wrong case order policy")
    if not meta.get("python") or not meta.get("platform"):
        raise ValueError("missing runtime metadata")
    datetime.fromisoformat(meta["recorded_at_utc"])
    for name in ("core_manifest", "size_manifest"):
        actual = hashlib.sha256((ROOT / f"data/{name}.csv").read_bytes()).hexdigest()
        if meta.get(f"{name}_sha256") != actual:
            raise ValueError(f"{name} hash mismatch")
    if len(rows) != len(cases) * len(ALGORITHMS) * REPEATS:
        raise ValueError("wrong row count")
    expected_sequence = [
        (case.case_id, repeat + 1, position, algorithm)
        for index, case in enumerate(cases)
        for repeat in range(REPEATS)
        for position, algorithm in enumerate(algorithm_order(index, repeat), start=1)
    ]
    observed_sequence = [
        (row["case_id"], int(row["repeat"]), int(row["order_position"]), row["algorithm"])
        for row in rows
    ]
    if observed_sequence != expected_sequence:
        raise ValueError("CSV execution sequence mismatch")
    groups = defaultdict(list)
    for row in rows:
        if set(row) != set(RAW_FIELDS) or None in row:
            raise ValueError("wrong CSV columns")
        case_id = row["case_id"]
        if case_id not in manifest:
            raise ValueError("unknown case")
        if any(row[field] != manifest[case_id][field] for field in CASE_FIELDS):
            raise ValueError("case metadata mismatch")
        index = int(row["case_order"])
        repeat = int(row["repeat"])
        position = int(row["order_position"])
        algorithm = row["algorithm"]
        if not 0 <= index < len(cases) or cases[index].case_id != case_id:
            raise ValueError("wrong case execution order")
        if not 1 <= repeat <= REPEATS or not 1 <= position <= len(ALGORITHMS):
            raise ValueError("wrong repeat or position")
        if algorithm_order(index, repeat - 1)[position - 1] != algorithm:
            raise ValueError("wrong algorithm execution order")
        if row["reached"] != "1" or int(row["elapsed_ns"]) <= 0:
            raise ValueError("invalid reachability or elapsed time")
        if any(int(row[field]) < 0 for field in COUNTER_FIELDS):
            raise ValueError("negative result metric")
        if int(row["path_steps"]) < int(row["shortest_steps"]) or int(row["cost"]) < int(row["path_steps"]):
            raise ValueError("impossible path length or cost")
        groups[(case_id, algorithm)].append(row)
    if set(groups) != {(case.case_id, algorithm) for case in cases for algorithm in ALGORITHMS}:
        raise ValueError("missing algorithm group")
    for group in groups.values():
        if sorted(int(row["repeat"]) for row in group) != list(range(1, REPEATS + 1)):
            raise ValueError("missing or duplicate repeat")
        if any(len({row[field] for row in group}) != 1 for field in COUNTER_FIELDS):
            raise ValueError("non-deterministic result metric")
    for case in cases:
        if len({groups[(case.case_id, algorithm)][0]["cost"] for algorithm in ALGORITHMS}) != 1:
            raise ValueError("algorithm costs disagree")
    return {"cases": len(cases), "rows": len(rows), "groups": len(groups)}


def verify_file(path: Path, suite: str) -> dict[str, int]:
    check_manifests()
    manifest_path = ROOT / ("data/size_manifest.csv" if suite == "size_extra" else "data/core_manifest.csv")
    with manifest_path.open(encoding="utf-8", newline="") as stream:
        manifest_rows = list(csv.DictReader(stream))
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    with path.with_suffix(".meta.json").open(encoding="utf-8") as stream:
        meta = json.load(stream)
    return verify(rows, meta, manifest_rows, suite)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("suite", choices=("pilot", "core", "size_extra"))
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    result = verify_file(args.input, args.suite)
    print(f"verified {args.suite}: {result['cases']} cases, {result['rows']} rows, {result['groups']} groups")


if __name__ == "__main__":
    main()
