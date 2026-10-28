import random
import unittest

from pathfinding import Grid
from pathfinding.dijkstra import dijkstra
from tests.bellman_ford_oracle import bellman_ford_cost


class DijkstraTests(unittest.TestCase):
    def test_weighted_detour_and_path_reconstruction(self) -> None:
        grid = Grid.from_rows(
            [[1, 9, 1], [1, 9, 1], [1, 1, 1]],
            start=(0, 0),
            goal=(0, 2),
        )
        result = dijkstra(grid)
        self.assertTrue(result.reached)
        self.assertEqual(result.cost, 6)
        self.assertEqual(
            result.path,
            ((0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2)),
        )
        self.assertEqual(grid.path_cost(result.path), result.cost)

    def test_unreachable_goal(self) -> None:
        grid = Grid.from_rows([[1, None, 1]], start=(0, 0), goal=(0, 2))
        result = dijkstra(grid)
        self.assertFalse(result.reached)
        self.assertIsNone(result.cost)
        self.assertEqual(result.path, ())
        self.assertEqual(result.expanded, 1)

    def test_start_equals_goal(self) -> None:
        grid = Grid.from_rows([[7]], start=(0, 0), goal=(0, 0))
        result = dijkstra(grid)
        self.assertTrue(result.reached)
        self.assertEqual(result.cost, 0)
        self.assertEqual(result.path, ((0, 0),))
        self.assertEqual(result.expanded, 0)
        self.assertEqual(grid.path_cost(result.path), 0)

    def test_equal_cost_ties_are_deterministic(self) -> None:
        grid = Grid.from_rows([[1, 1], [1, 1]], start=(0, 0), goal=(1, 1))
        results = [dijkstra(grid) for _ in range(5)]
        self.assertTrue(all(result.path == results[0].path for result in results))
        self.assertEqual(results[0].path, ((0, 0), (0, 1), (1, 1)))

    def test_priority_queue_counts(self) -> None:
        grid = Grid.from_rows(
            [[1, 9, 1, 9], [1, 1, 1, 9]],
            start=(0, 0),
            goal=(0, 3),
        )
        result = dijkstra(grid)
        self.assertEqual(result.cost, 13)
        self.assertEqual(result.pq_pops, result.expanded + 1)
        self.assertGreaterEqual(result.pq_pushes, result.pq_pops)
        self.assertEqual(grid.path_cost(result.path), result.cost)

    def test_small_random_grids_match_independent_oracle(self) -> None:
        rng = random.Random(20261028)
        for case in range(100):
            height = rng.randint(2, 5)
            width = rng.randint(2, 5)
            rows = [
                [None if rng.random() < 0.22 else rng.randint(1, 9) for _ in range(width)]
                for _ in range(height)
            ]
            start = (rng.randrange(height), rng.randrange(width))
            goal = (rng.randrange(height), rng.randrange(width))
            rows[start[0]][start[1]] = rng.randint(1, 9)
            rows[goal[0]][goal[1]] = rng.randint(1, 9)
            grid = Grid.from_rows(rows, start, goal)
            result = dijkstra(grid)
            expected = bellman_ford_cost(grid)
            with self.subTest(case=case, start=start, goal=goal):
                self.assertEqual(result.cost, expected)
                self.assertEqual(result.reached, expected is not None)
                self.assertGreaterEqual(result.pq_pushes, result.pq_pops)
                if expected is None:
                    self.assertEqual(result.path, ())
                else:
                    self.assertEqual(grid.path_cost(result.path), expected)


if __name__ == "__main__":
    unittest.main()
