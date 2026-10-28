import argparse
import csv
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from time import perf_counter_ns

from pathfinding import astar, bidirectional_dijkstra, dijkstra

from .maps import build_grid, grid_sha256, manifest_csv, shortest_steps
from .protocol import ALGORITHMS, PROTOCOL_VERSION, REPEATS, algorithm_order, size_manifest_csv, suite_cases

RUNNERS = {"dijkstra": dijkstra, "astar": astar, "bidirectional_dijkstra": bidirectional_dijkstra}
ROOT = Path(__file__).resolve().parents[1]
RAW_FIELDS = (
    "case_id", "terrain", "distance", "size", "seed", "grid_sha256",
    "manhattan_steps", "shortest_steps", "walkable_cells", "case_order",
    "algorithm", "repeat", "order_position", "elapsed_ns", "reached",
    "cost", "path_steps", "expanded", "pq_pushes", "pq_pops",
)


def check_manifests() -> None:
    expected = {
        ROOT / "data/core_manifest.csv": manifest_csv(),
        ROOT / "data/size_manifest.csv": size_manifest_csv(),
    }
    for path, content in expected.items():
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            raise ValueError(f"manifest mismatch: {path}")


def _validated(result, grid, expected_cost: int | None) -> int:
    if not result.reached or result.cost is None:
        raise ValueError("reachable case was not solved")
    if grid.path_cost(result.path) != result.cost:
        raise ValueError("invalid result path or cost")
    if expected_cost is not None and result.cost != expected_cost:
        raise ValueError("algorithm costs disagree")
    return result.cost


def measure_cases(cases) -> list[dict[str, object]]:
    rows = []
    for case_index, case in enumerate(cases):
        grid = build_grid(case)
        steps = shortest_steps(grid)
        if steps is None:
            raise ValueError(f"unreachable case: {case.case_id}")
        metadata = {
            "case_id": case.case_id,
            "terrain": case.terrain,
            "distance": case.distance,
            "size": case.size,
            "seed": case.seed,
            "grid_sha256": grid_sha256(grid),
            "manhattan_steps": abs(case.start[0] - case.goal[0]) + abs(case.start[1] - case.goal[1]),
            "shortest_steps": steps,
            "walkable_cells": sum(cost is not None for row in grid.costs for cost in row),
            "case_order": case_index,
        }
        expected_cost = None
        for algorithm in ALGORITHMS:
            result = RUNNERS[algorithm](grid)
            expected_cost = _validated(result, grid, expected_cost)
        for repeat in range(REPEATS):
            for position, algorithm in enumerate(algorithm_order(case_index, repeat), start=1):
                start_ns = perf_counter_ns()
                result = RUNNERS[algorithm](grid)
                elapsed_ns = perf_counter_ns() - start_ns
                _validated(result, grid, expected_cost)
                rows.append({
                    **metadata,
                    "algorithm": algorithm,
                    "repeat": repeat + 1,
                    "order_position": position,
                    "elapsed_ns": elapsed_ns,
                    "reached": int(result.reached),
                    "cost": result.cost,
                    "path_steps": len(result.path) - 1,
                    "expanded": result.expanded,
                    "pq_pushes": result.pq_pushes,
                    "pq_pops": result.pq_pops,
                })
    return rows


def rows_csv(rows: list[dict[str, object]]) -> str:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=RAW_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def validate_rows(rows: list[dict[str, object]], cases) -> None:
    cases = tuple(cases)
    if len(rows) != len(cases) * len(ALGORITHMS) * REPEATS:
        raise ValueError("incomplete measurement rows")
    observed = set()
    for row in rows:
        key = (row["case_id"], row["algorithm"], row["repeat"])
        if key in observed:
            raise ValueError("duplicate measurement row")
        observed.add(key)
    expected = {
        (case.case_id, algorithm, repeat)
        for case in cases for algorithm in ALGORITHMS for repeat in range(1, REPEATS + 1)
    }
    if observed != expected:
        raise ValueError("measurement keys mismatch")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("suite", choices=("pilot", "core", "size_extra"))
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output
    meta_path = output.with_suffix(".meta.json")
    if output.exists() or meta_path.exists():
        parser.error("output already exists; use a new versioned name")
    check_manifests()
    cases = suite_cases(args.suite)
    rows = measure_cases(cases)
    validate_rows(rows, cases)
    meta = {
        "protocol_version": PROTOCOL_VERSION,
        "suite": args.suite,
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "timer": "perf_counter_ns",
        "repeats": REPEATS,
        "warmups_per_algorithm_case": 1,
        "case_order": "sha256(case-order-v1:case_id) ascending",
        "algorithm_order": "rotate by (case_index + repeat_index) mod 3",
        "case_ids": [case.case_id for case in cases],
        "core_manifest_sha256": hashlib.sha256((ROOT / "data/core_manifest.csv").read_bytes()).hexdigest(),
        "size_manifest_sha256": hashlib.sha256((ROOT / "data/size_manifest.csv").read_bytes()).hexdigest(),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="") as stream:
        stream.write(rows_csv(rows))
    with meta_path.open("x", encoding="utf-8") as stream:
        json.dump(meta, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(f"{args.suite}: {len(cases)} cases, {len(rows)} rows -> {output}")


if __name__ == "__main__":
    main()
