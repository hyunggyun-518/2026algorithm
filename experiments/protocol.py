import csv
import hashlib
from io import StringIO

from .maps import CORE_SIZE, MANIFEST_FIELDS, MapCase, core_cases, manifest_csv

PROTOCOL_VERSION = "1"
ALGORITHMS = ("dijkstra", "astar", "bidirectional_dijkstra")
REPEATS = 3
SIZE_SEEDS = (0, 2, 4, 6, 8, 10)
SIZE_TERRAINS = ("open", "barrier")
SIZE_VALUES = (51, 101, 201)
PILOT_IDS = ("open-near-101-00", "barrier-far-101-00", "maze-far-101-00")


def size_cases() -> tuple[MapCase, ...]:
    return tuple(
        MapCase(terrain, "far", size, seed)
        for terrain in SIZE_TERRAINS
        for size in SIZE_VALUES
        for seed in SIZE_SEEDS
    )


def size_extra_cases() -> tuple[MapCase, ...]:
    return tuple(case for case in size_cases() if case.size != CORE_SIZE)


def pilot_cases() -> tuple[MapCase, ...]:
    cases = {case.case_id: case for case in core_cases()}
    return tuple(cases[case_id] for case_id in PILOT_IDS)


def suite_cases(suite: str) -> tuple[MapCase, ...]:
    suites = {"pilot": pilot_cases, "core": core_cases, "size_extra": size_extra_cases}
    if suite not in suites:
        raise ValueError(f"unknown suite: {suite}")
    return tuple(sorted(suites[suite](), key=lambda case: hashlib.sha256(
        f"case-order-v1:{case.case_id}".encode("ascii")
    ).digest()))


def algorithm_order(case_index: int, repeat: int) -> tuple[str, ...]:
    offset = (case_index + repeat) % len(ALGORITHMS)
    return ALGORITHMS[offset:] + ALGORITHMS[:offset]


def size_manifest_csv() -> str:
    input_rows = csv.DictReader(StringIO(manifest_csv(size_cases())))
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=(*MANIFEST_FIELDS, "source"), lineterminator="\n")
    writer.writeheader()
    for row in input_rows:
        row["source"] = "core_reuse" if int(row["size"]) == CORE_SIZE else "additional"
        writer.writerow(row)
    return output.getvalue()
