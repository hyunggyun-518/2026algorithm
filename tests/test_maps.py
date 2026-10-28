import csv
import unittest
from collections import deque
from io import StringIO
from pathlib import Path

from experiments.maps import (
    CORE_SEEDS,
    CORE_SIZE,
    DISTANCES,
    TERRAINS,
    MapCase,
    build_grid,
    core_cases,
    grid_sha256,
    manifest_csv,
    render_topology,
    shortest_steps,
)
from pathfinding import astar, bidirectional_dijkstra, dijkstra


class MapGenerationTests(unittest.TestCase):
    def test_invalid_case_settings(self) -> None:
        for terrain, distance, size, seed in (
            ("unknown", "near", 101, 0),
            ("open", "unknown", 101, 0),
            ("open", "near", 100, 0),
            ("open", "near", 9, 0),
            ("open", "near", 101, -1),
            ("open", "near", 101, 2**64),
        ):
            with self.subTest(terrain=terrain, distance=distance, size=size, seed=seed):
                with self.assertRaises(ValueError):
                    MapCase(terrain, distance, size, seed)

    def test_core_cases_are_complete_and_unique(self) -> None:
        cases = core_cases()
        self.assertEqual(len(cases), 72)
        self.assertEqual(len({case.case_id for case in cases}), 72)
        for terrain in TERRAINS:
            for distance in DISTANCES:
                matching = [case for case in cases if (case.terrain, case.distance) == (terrain, distance)]
                self.assertEqual(len(matching), 12)
                self.assertEqual({case.seed for case in matching}, set(CORE_SEEDS))
                self.assertTrue(all(case.size == CORE_SIZE for case in matching))

    def test_paired_goals_share_identical_maps(self) -> None:
        hashes = set()
        for terrain in TERRAINS:
            for seed in CORE_SEEDS:
                near = build_grid(MapCase(terrain, "near", CORE_SIZE, seed))
                far = build_grid(MapCase(terrain, "far", CORE_SIZE, seed))
                self.assertEqual(near.costs, far.costs)
                self.assertEqual(near.start, far.start)
                self.assertEqual(shortest_steps(near), 10)
                self.assertGreater(shortest_steps(far), shortest_steps(near))
                queue = deque([near.start])
                visited = {near.start}
                while queue:
                    for neighbor in near.adjacent(queue.popleft()):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                walkable = sum(cost is not None for row in near.costs for cost in row)
                self.assertEqual(len(visited), walkable)
                hashes.add(grid_sha256(near))
        self.assertEqual(len(hashes), 36)

    def test_all_core_cases_have_matching_optimal_paths(self) -> None:
        for case in core_cases():
            grid = build_grid(case)
            results = [search(grid) for search in (dijkstra, astar, bidirectional_dijkstra)]
            with self.subTest(case=case.case_id):
                self.assertTrue(all(result.reached for result in results))
                self.assertEqual(len({result.cost for result in results}), 1)
                self.assertTrue(all(grid.path_cost(result.path) == result.cost for result in results))

    def test_each_terrain_is_connected_and_distinct(self) -> None:
        wall_counts = {}
        for terrain in TERRAINS:
            grid = build_grid(MapCase(terrain, "far", 21, 0))
            queue = deque([grid.start])
            visited = {grid.start}
            while queue:
                for neighbor in grid.adjacent(queue.popleft()):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            walkable = sum(cost is not None for row in grid.costs for cost in row)
            wall_counts[terrain] = grid.height * grid.width - walkable
            self.assertEqual(len(visited), walkable)
            self.assertIsNotNone(shortest_steps(grid))
            self.assertTrue(all(cost is None or 1 <= cost <= 9 for row in grid.costs for cost in row))
        self.assertEqual(wall_counts["open"], 0)
        self.assertLess(wall_counts["barrier"], wall_counts["maze"])

    def test_supported_size_scaling(self) -> None:
        for size in (51, 101, 201):
            for terrain in TERRAINS:
                near = build_grid(MapCase(terrain, "near", size, 0))
                far = build_grid(MapCase(terrain, "far", size, 0))
                with self.subTest(size=size, terrain=terrain):
                    self.assertEqual((near.height, near.width), (size, size))
                    self.assertEqual(near.costs, far.costs)
                    self.assertIsNotNone(shortest_steps(near))
                    self.assertIsNotNone(shortest_steps(far))
                    self.assertLess(shortest_steps(near), shortest_steps(far))

    def test_same_seed_recreates_same_map(self) -> None:
        for terrain in TERRAINS:
            case = MapCase(terrain, "far", 51, 7)
            self.assertEqual(build_grid(case), build_grid(case))
            self.assertNotEqual(grid_sha256(build_grid(case)), grid_sha256(build_grid(MapCase(terrain, "far", 51, 8))))

    def test_manifest_matches_checked_in_file(self) -> None:
        generated = manifest_csv()
        path = Path(__file__).resolve().parents[1] / "data" / "core_manifest.csv"
        self.assertEqual(generated, path.read_text(encoding="utf-8"))
        rows = list(csv.DictReader(StringIO(generated)))
        self.assertEqual(len(rows), 72)
        self.assertTrue(all(row["shortest_steps"] and row["grid_sha256"] for row in rows))

    def test_ascii_rendering(self) -> None:
        grid = build_grid(MapCase("maze", "far", 21, 0))
        lines = render_topology(grid).splitlines()
        self.assertEqual(len(lines), 21)
        self.assertTrue(all(len(line) == 21 for line in lines))
        self.assertEqual("".join(lines).count("S"), 1)
        self.assertEqual("".join(lines).count("G"), 1)


if __name__ == "__main__":
    unittest.main()
