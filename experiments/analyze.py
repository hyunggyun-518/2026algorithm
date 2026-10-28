import argparse
import csv
import json
import math
from collections import defaultdict
from io import StringIO
from pathlib import Path
from statistics import median
from xml.sax.saxutils import escape

from pathfinding import bidirectional_dijkstra, dijkstra

from .maps import MapCase, build_grid
from .measure import ROOT
from .protocol import ALGORITHMS, SIZE_SEEDS
from .verify import verify_file

CASE_FIELDS = (
    "suite", "case_id", "terrain", "distance", "size", "seed", "algorithm",
    "median_elapsed_ns", "min_elapsed_ns", "max_elapsed_ns", "expanded",
    "pq_pushes", "pq_pops", "cost", "path_steps", "shortest_steps",
    "manhattan_steps", "walkable_cells", "grid_sha256",
)
GROUP_FIELDS = (
    "terrain", "distance", "algorithm", "cases", "baseline_median_ms",
    "candidate_median_ms", "time_ratio_q1", "time_ratio_median", "time_ratio_q3",
    "time_wins", "expanded_ratio_q1", "expanded_ratio_median",
    "expanded_ratio_q3", "expanded_wins", "median_shortest_steps",
)
SIZE_FIELDS = (
    "terrain", "distance", "size", "source", "algorithm", "cases",
    "baseline_median_ms", "candidate_median_ms", "baseline_median_expanded",
    "candidate_median_expanded", "time_ratio_q1", "time_ratio_median",
    "time_ratio_q3", "time_wins", "expanded_ratio_q1",
    "expanded_ratio_median", "expanded_ratio_q3", "expanded_wins",
    "median_shortest_steps", "median_manhattan_steps", "median_cost",
)
TERRAINS = ("open", "barrier", "maze")
DISTANCES = ("near", "far")
CANDIDATES = ALGORITHMS[1:]
COLORS = {"dijkstra": "#455a64", "astar": "#e08a22", "bidirectional_dijkstra": "#2679b5"}


def _csv_text(fields, rows) -> str:
    stream = StringIO()
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def _number(value: float) -> str:
    return f"{value:.6f}"


def _quartiles(values) -> tuple[float, float, float]:
    ordered = sorted(values)
    if len(ordered) not in (6, 12):
        raise ValueError("unexpected number of paired cases")
    half = len(ordered) // 2
    return median(ordered[:half]), median(ordered), median(ordered[half:])


def _raw_rows(path: Path, suite: str) -> list[dict[str, str]]:
    verify_file(path, suite)
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def case_metrics(raw_rows: list[dict[str, str]], suite: str) -> list[dict[str, object]]:
    groups = defaultdict(list)
    for row in raw_rows:
        groups[(row["case_id"], row["algorithm"])].append(row)
    result = []
    for (case_id, algorithm), rows in sorted(groups.items()):
        first = rows[0]
        times = [int(row["elapsed_ns"]) for row in rows]
        result.append({
            "suite": suite,
            "case_id": case_id,
            "terrain": first["terrain"],
            "distance": first["distance"],
            "size": int(first["size"]),
            "seed": int(first["seed"]),
            "algorithm": algorithm,
            "median_elapsed_ns": int(median(times)),
            "min_elapsed_ns": min(times),
            "max_elapsed_ns": max(times),
            "expanded": int(first["expanded"]),
            "pq_pushes": int(first["pq_pushes"]),
            "pq_pops": int(first["pq_pops"]),
            "cost": int(first["cost"]),
            "path_steps": int(first["path_steps"]),
            "shortest_steps": int(first["shortest_steps"]),
            "manhattan_steps": int(first["manhattan_steps"]),
            "walkable_cells": int(first["walkable_cells"]),
            "grid_sha256": first["grid_sha256"],
        })
    return result


def _paired_summary(cases, lookup, fields) -> dict[str, object]:
    base = [lookup[(case, "dijkstra")] for case in cases]
    candidate = [lookup[(case, fields["algorithm"])] for case in cases]
    time = [a["median_elapsed_ns"] / b["median_elapsed_ns"] for a, b in zip(candidate, base)]
    expanded = [a["expanded"] / b["expanded"] for a, b in zip(candidate, base)]
    tq1, tmedian, tq3 = _quartiles(time)
    eq1, emedian, eq3 = _quartiles(expanded)
    return {
        **fields,
        "cases": len(cases),
        "baseline_median_ms": _number(median(row["median_elapsed_ns"] for row in base) / 1e6),
        "candidate_median_ms": _number(median(row["median_elapsed_ns"] for row in candidate) / 1e6),
        "time_ratio_q1": _number(tq1),
        "time_ratio_median": _number(tmedian),
        "time_ratio_q3": _number(tq3),
        "time_wins": sum(value < 1 for value in time),
        "expanded_ratio_q1": _number(eq1),
        "expanded_ratio_median": _number(emedian),
        "expanded_ratio_q3": _number(eq3),
        "expanded_wins": sum(value < 1 for value in expanded),
        "median_shortest_steps": _number(median(row["shortest_steps"] for row in base)),
    }


def core_groups(metrics: list[dict[str, object]]) -> list[dict[str, object]]:
    lookup = {(row["case_id"], row["algorithm"]): row for row in metrics}
    result = []
    for terrain in TERRAINS:
        for distance in DISTANCES:
            cases = [f"{terrain}-{distance}-101-{seed:02d}" for seed in range(12)]
            for algorithm in CANDIDATES:
                result.append(_paired_summary(cases, lookup, {
                    "terrain": terrain, "distance": distance, "algorithm": algorithm,
                }))
    return result


def size_groups(metrics: list[dict[str, object]]) -> list[dict[str, object]]:
    lookup = {(row["case_id"], row["algorithm"]): row for row in metrics}
    result = []
    for terrain in ("open", "barrier"):
        for size in (51, 101, 201):
            cases = [f"{terrain}-far-{size}-{seed:02d}" for seed in SIZE_SEEDS]
            for algorithm in CANDIDATES:
                summary = _paired_summary(cases, lookup, {
                    "terrain": terrain, "distance": "far", "size": size,
                    "source": "core_reuse" if size == 101 else "additional",
                    "algorithm": algorithm,
                })
                base = [lookup[(case, "dijkstra")] for case in cases]
                candidate = [lookup[(case, algorithm)] for case in cases]
                summary["baseline_median_expanded"] = _number(median(row["expanded"] for row in base))
                summary["candidate_median_expanded"] = _number(median(row["expanded"] for row in candidate))
                summary["median_manhattan_steps"] = _number(median(row["manhattan_steps"] for row in base))
                summary["median_cost"] = _number(median(row["cost"] for row in base))
                result.append(summary)
    return result


def _svg_header(width: int, height: int, title: str, description: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">',
        f"<title>{escape(title)}</title>",
        f"<desc>{escape(description)}</desc>",
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
    ]


def ratio_figure(groups: list[dict[str, object]], metric: str) -> str:
    title = "Core cases: paired time ratio" if metric == "time" else "Core cases: paired expanded-node ratio"
    description = "Candidate divided by Dijkstra; dots show median and bars show interquartile range across 12 seeds."
    width, height = 920, 540
    left, right, top, bottom = 220, 840, 100, 490
    minimum, maximum = (0.35, 3.2) if metric == "time" else (0.3, 1.15)
    ticks = (0.5, 1, 2, 3) if metric == "time" else (0.4, 0.6, 0.8, 1)
    def x(value):
        return left + (math.log(value) - math.log(minimum)) / (math.log(maximum) - math.log(minimum)) * (right - left)
    svg = _svg_header(width, height, title, description)
    svg.append(f'<text x="{left}" y="42" font-size="24" font-family="Arial" fill="#1b2b36">{escape(title)}</text>')
    svg.append(f'<text x="{left}" y="64" font-size="13" font-family="Arial" fill="#455a64">Ratio below 1 favors the candidate</text>')
    for tick in ticks:
        px = x(tick)
        stroke = "#546e7a" if tick == 1 else "#e2e8ec"
        svg.append(f'<line x1="{px:.2f}" y1="{top}" x2="{px:.2f}" y2="{bottom}" stroke="{stroke}" stroke-width="{2 if tick == 1 else 1}"/>')
        svg.append(f'<text x="{px:.2f}" y="{bottom+24}" text-anchor="middle" font-size="13" font-family="Arial" fill="#455a64">{tick:g}</text>')
    labels = [(terrain, distance) for terrain in TERRAINS for distance in DISTANCES]
    by_key = {(row["terrain"], row["distance"], row["algorithm"]): row for row in groups}
    for index, (terrain, distance) in enumerate(labels):
        cy = top + 31 + index * 56
        svg.append(f'<text x="{left-18}" y="{cy+4}" text-anchor="end" font-size="15" font-family="Arial" fill="#1b2b36">{terrain} · {distance}</text>')
        for offset, algorithm in ((-10, "astar"), (10, "bidirectional_dijkstra")):
            row = by_key[(terrain, distance, algorithm)]
            y = cy + offset
            q1, mid, q3 = (float(row[f"{metric}_ratio_{part}"]) for part in ("q1", "median", "q3"))
            color = COLORS[algorithm]
            svg.append(f'<line x1="{x(q1):.2f}" y1="{y}" x2="{x(q3):.2f}" y2="{y}" stroke="{color}" stroke-width="4" stroke-linecap="round"/>')
            svg.append(f'<circle cx="{x(mid):.2f}" cy="{y}" r="6" fill="{color}"/>')
    svg.append(f'<text x="{(left+right)/2}" y="{height-12}" text-anchor="middle" font-size="14" font-family="Arial" fill="#1b2b36">Candidate / Dijkstra (log scale)</text>')
    svg.append(f'<circle cx="{left}" cy="82" r="5" fill="{COLORS["astar"]}"/><text x="{left+12}" y="86" font-size="13" font-family="Arial" fill="#1b2b36">A*</text>')
    svg.append(f'<circle cx="{left+62}" cy="82" r="5" fill="{COLORS["bidirectional_dijkstra"]}"/><text x="{left+74}" y="86" font-size="13" font-family="Arial" fill="#1b2b36">Bidirectional Dijkstra</text>')
    svg.append("</svg>\n")
    return "\n".join(svg)


def size_figure(size_rows: list[dict[str, object]]) -> str:
    title = "Runtime by grid size"
    svg = _svg_header(1050, 560, title, "Median milliseconds across six seeds; 101-by-101 values are reused from the core run.")
    svg.append(f'<text x="70" y="42" font-size="24" font-family="Arial" fill="#1b2b36">{title}</text>')
    svg.append('<text x="70" y="64" font-size="13" font-family="Arial" fill="#455a64">Far goal · median across 6 matched seeds · log runtime axis</text>')
    for panel, terrain in enumerate(("open", "barrier")):
        x0, x1 = 75 + panel * 510, 455 + panel * 510
        y0, y1 = 105, 450
        values = []
        for size in (51, 101, 201):
            rows = [row for row in size_rows if row["terrain"] == terrain and row["size"] == size]
            values.append(float(rows[0]["baseline_median_ms"]))
            values.extend(float(row["candidate_median_ms"]) for row in rows)
        low, high = min(values) * 0.75, max(values) * 1.35
        def px(size):
            return x0 + (math.log(size) - math.log(51)) / (math.log(201) - math.log(51)) * (x1 - x0)
        def py(value):
            return y1 - (math.log(value) - math.log(low)) / (math.log(high) - math.log(low)) * (y1 - y0)
        svg.append(f'<text x="{x0}" y="96" font-size="18" font-family="Arial" fill="#1b2b36">{terrain.capitalize()}</text>')
        for tick in (1, 3, 10, 30, 100):
            if low <= tick <= high:
                yy = py(tick)
                svg.append(f'<line x1="{x0}" y1="{yy:.2f}" x2="{x1}" y2="{yy:.2f}" stroke="#e2e8ec"/>')
                svg.append(f'<text x="{x0-8}" y="{yy+4:.2f}" text-anchor="end" font-size="12" font-family="Arial" fill="#455a64">{tick}</text>')
        for size in (51, 101, 201):
            xx = px(size)
            svg.append(f'<text x="{xx:.2f}" y="{y1+24}" text-anchor="middle" font-size="13" font-family="Arial" fill="#455a64">{size}</text>')
        for algorithm in ALGORITHMS:
            points = []
            for size in (51, 101, 201):
                rows = [row for row in size_rows if row["terrain"] == terrain and row["size"] == size]
                value = float(rows[0]["baseline_median_ms"]) if algorithm == "dijkstra" else float(next(row["candidate_median_ms"] for row in rows if row["algorithm"] == algorithm))
                points.append((px(size), py(value)))
            color = COLORS[algorithm]
            coordinates = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
            svg.append(f'<polyline points="{coordinates}" fill="none" stroke="{color}" stroke-width="3"/>')
            for x, y in points:
                svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" fill="{color}"/>')
        svg.append(f'<text x="{(x0+x1)/2}" y="{y1+52}" text-anchor="middle" font-size="14" font-family="Arial" fill="#1b2b36">Grid width and height (cells)</text>')
    svg.append('<text x="20" y="280" transform="rotate(-90 20 280)" text-anchor="middle" font-size="14" font-family="Arial" fill="#1b2b36">Median runtime (ms, log scale)</text>')
    for index, (algorithm, label) in enumerate((("dijkstra", "Dijkstra"), ("astar", "A*"), ("bidirectional_dijkstra", "Bidirectional Dijkstra"))):
        x = 280 + 220 * index
        svg.append(f'<line x1="{x}" y1="535" x2="{x+26}" y2="535" stroke="{COLORS[algorithm]}" stroke-width="3"/><text x="{x+35}" y="540" font-size="13" font-family="Arial" fill="#1b2b36">{label}</text>')
    svg.append("</svg>\n")
    return "\n".join(svg)


def map_figure(case: MapCase, metrics: list[dict[str, object]], title: str) -> str:
    grid = build_grid(case)
    optimal = dijkstra(grid)
    other = bidirectional_dijkstra(grid)
    lookup = {row["algorithm"]: row for row in metrics if row["case_id"] == case.case_id}
    if optimal.cost != other.cost or optimal.cost != lookup["dijkstra"]["cost"]:
        raise ValueError("map path does not match recorded cost")
    scale, left, top = 5, 55, 85
    width, height = 900, 660
    svg = _svg_header(width, height, title, f"Topology and an optimal path for {case.case_id}.")
    svg.append(f'<text x="{left}" y="35" font-size="24" font-family="Arial" fill="#1b2b36">{escape(title)}</text>')
    svg.append(f'<text x="{left}" y="58" font-size="14" font-family="Arial" fill="#455a64">{escape(case.case_id)} · walls in dark gray · Dijkstra optimal path in blue</text>')
    svg.append(f'<rect x="{left}" y="{top}" width="{grid.width*scale}" height="{grid.height*scale}" fill="#f3f7f9" stroke="#bccbd3"/>')
    for row_index, row in enumerate(grid.costs):
        start = None
        for column in range(len(row) + 1):
            blocked = column < len(row) and row[column] is None
            if blocked and start is None:
                start = column
            elif not blocked and start is not None:
                svg.append(f'<rect x="{left+start*scale}" y="{top+row_index*scale}" width="{(column-start)*scale}" height="{scale}" fill="#263238"/>')
                start = None
    path = " ".join(f"{left+(column+0.5)*scale:.1f},{top+(row+0.5)*scale:.1f}" for row, column in optimal.path)
    svg.append(f'<polyline points="{path}" fill="none" stroke="#2679b5" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>')
    for position, color, label in ((case.start, "#00866a", "S"), (case.goal, "#c43f43", "G")):
        x = left + (position[1] + 0.5) * scale
        y = top + (position[0] + 0.5) * scale
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{color}" stroke="#ffffff" stroke-width="2"/>')
        svg.append(f'<text x="{x:.1f}" y="{y+4:.1f}" text-anchor="middle" font-size="11" font-family="Arial" font-weight="bold" fill="#ffffff">{label}</text>')
    x = 590
    svg.append(f'<text x="{x}" y="{top+20}" font-size="15" font-family="Arial" fill="#1b2b36">Median runtime</text>')
    for index, algorithm in enumerate(ALGORITHMS):
        row = lookup[algorithm]
        label = {"dijkstra": "Dijkstra", "astar": "A*", "bidirectional_dijkstra": "Bidirectional"}[algorithm]
        svg.append(f'<text x="{x}" y="{top+53+index*55}" font-size="14" font-family="Arial" fill="{COLORS[algorithm]}">{label}</text>')
        svg.append(f'<text x="{x}" y="{top+73+index*55}" font-size="14" font-family="Arial" fill="#1b2b36">{row["median_elapsed_ns"]/1e6:.3f} ms · {row["expanded"]} nodes</text>')
    svg.append(f'<text x="{x}" y="{top+250}" font-size="14" font-family="Arial" fill="#1b2b36">Optimal cost: {optimal.cost}</text>')
    svg.append(f'<text x="{x}" y="{top+278}" font-size="14" font-family="Arial" fill="#1b2b36">Shortest unweighted: {lookup["dijkstra"]["shortest_steps"]} steps</text>')
    svg.append(f'<text x="{left}" y="{top+grid.height*scale+30}" font-size="12" font-family="Arial" fill="#455a64">Selection: extreme bidirectional/Dijkstra runtime ratio within its named group; not a typical case.</text>')
    svg.append("</svg>\n")
    return "\n".join(svg)


def generate() -> dict[Path, str]:
    core_rows = _raw_rows(ROOT / "data/raw/core_v1.csv", "core")
    extra_rows = _raw_rows(ROOT / "data/raw/size_extra_v1.csv", "size_extra")
    core_meta = json.loads((ROOT / "data/raw/core_v1.meta.json").read_text(encoding="utf-8"))
    extra_meta = json.loads((ROOT / "data/raw/size_extra_v1.meta.json").read_text(encoding="utf-8"))
    if core_meta["python"] != extra_meta["python"] or core_meta["platform"] != extra_meta["platform"]:
        raise ValueError("core and size runs used different environments")
    metrics = case_metrics(core_rows, "core") + case_metrics(extra_rows, "size_extra")
    if len(metrics) != 288:
        raise ValueError("wrong combined case metric count")
    core = core_groups(metrics)
    size = size_groups(metrics)
    lookup = {(row["case_id"], row["algorithm"]): row for row in metrics}
    def bidirectional_ratio(row):
        return lookup[(row["case_id"], "bidirectional_dijkstra")]["median_elapsed_ns"] / row["median_elapsed_ns"]
    baseline = [row for row in metrics if row["suite"] == "core" and row["algorithm"] == "dijkstra"]
    counter_row = max((row for row in baseline if row["terrain"] == "barrier" and row["distance"] == "far"), key=bidirectional_ratio)
    success_row = min((row for row in baseline if row["terrain"] == "maze" and row["distance"] == "far"), key=bidirectional_ratio)
    counterexample = MapCase(counter_row["terrain"], counter_row["distance"], counter_row["size"], counter_row["seed"])
    success = MapCase(success_row["terrain"], success_row["distance"], success_row["size"], success_row["seed"])
    outputs = {
        ROOT / "data/analysis/case_metrics.csv": _csv_text(CASE_FIELDS, metrics),
        ROOT / "data/analysis/core_group_summary.csv": _csv_text(GROUP_FIELDS, core),
        ROOT / "data/analysis/size_group_summary.csv": _csv_text(SIZE_FIELDS, size),
        ROOT / "figures/core_time_ratios.svg": ratio_figure(core, "time"),
        ROOT / "figures/core_expanded_ratios.svg": ratio_figure(core, "expanded"),
        ROOT / "figures/size_scaling.svg": size_figure(size),
        ROOT / "figures/barrier_far_counterexample.svg": map_figure(counterexample, metrics, "Counterexample: distant barrier"),
        ROOT / "figures/maze_far_success.svg": map_figure(success, metrics, "Strong case: distant maze"),
    }
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("build", "check"))
    args = parser.parse_args()
    outputs = generate()
    for path, content in outputs.items():
        if args.mode == "check":
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                raise ValueError(f"generated output mismatch: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    print(f"{args.mode}: {len(outputs)} analysis outputs")


if __name__ == "__main__":
    main()
