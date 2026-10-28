import random
import unittest
from itertools import product

from pathfinding import Grid
from pathfinding.astar import astar
from pathfinding.bidirectional import bidirectional_dijkstra
from pathfinding.dijkstra import dijkstra
from tests.bellman_ford_oracle import bellman_ford_cost


class BidirectionalDijkstraTests(unittest.TestCase):
    def test_reverse_edge_uses_original_destination_cost(self) -> None:
        grid = Grid.from_rows([[9, 2]], start=(0, 0), goal=(0, 1))
        self.assertEqual(dict(grid.reverse_neighbors(grid.goal))[(0, 0)], 2)
        result = bidirectional_dijkstra(grid)
        self.assertEqual(result.cost, 2)
        self.assertEqual(result.path, ((0, 0), (0, 1)))
        self.assertEqual(grid.path_cost(result.path), 2)

    def test_first_overlap_is_not_safe_to_stop(self) -> None:
        grid = Grid.from_rows(
            [[1, 9, 1], [1, 9, 1], [1, 1, 1]],
            start=(0, 0),
            goal=(0, 2),
        )
        first_forward = dict(grid.forward_neighbors(grid.start))
        first_reverse = dict(grid.reverse_neighbors(grid.goal))
        self.assertEqual(first_forward[(0, 1)] + first_reverse[(0, 1)], 10)
        result = bidirectional_dijkstra(grid)
        self.assertEqual(result.cost, 6)
        self.assertEqual(result.cost, bellman_ford_cost(grid))
        self.assertEqual(grid.path_cost(result.path), 6)

    def test_unreachable_goal(self) -> None:
        grid = Grid.from_rows([[1, None, 1]], start=(0, 0), goal=(0, 2))
        result = bidirectional_dijkstra(grid)
        self.assertFalse(result.reached)
        self.assertIsNone(result.cost)
        self.assertEqual(result.path, ())

    def test_start_equals_goal(self) -> None:
        grid = Grid.from_rows([[7]], start=(0, 0), goal=(0, 0))
        result = bidirectional_dijkstra(grid)
        self.assertTrue(result.reached)
        self.assertEqual(result.cost, 0)
        self.assertEqual(result.path, ((0, 0),))
        self.assertEqual(result.expanded, 0)
        self.assertEqual(grid.path_cost(result.path), 0)

    def test_equal_cost_ties_are_deterministic(self) -> None:
        grid = Grid.from_rows(
            [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
            start=(0, 0),
            goal=(2, 2),
        )
        results = [bidirectional_dijkstra(grid) for _ in range(5)]
        self.assertTrue(all(result.path == results[0].path for result in results))
        self.assertEqual(results[0].cost, 4)
        self.assertEqual(grid.path_cost(results[0].path), 4)

    def test_exhaustive_tiny_grids_match_oracle(self) -> None:
        for start_cost, goal_cost in product((1, 9), repeat=2):
            for cells in product((None, 1, 4), repeat=4):
                rows = [
                    [start_cost, cells[0], cells[1]],
                    [cells[2], cells[3], goal_cost],
                ]
                grid = Grid.from_rows(rows, start=(0, 0), goal=(1, 2))
                result = bidirectional_dijkstra(grid)
                expected = bellman_ford_cost(grid)
                with self.subTest(rows=rows):
                    self.assertEqual(result.cost, expected)
                    self.assertEqual(result.reached, expected is not None)
                    self.assertGreaterEqual(result.pq_pushes, result.pq_pops)
                    if expected is None:
                        self.assertEqual(result.path, ())
                    else:
                        self.assertEqual(grid.path_cost(result.path), expected)

    def test_random_weighted_grids_match_all_references(self) -> None:
        rng = random.Random(20261031)
        for case in range(300):
            height = rng.randint(2, 7)
            width = rng.randint(2, 7)
            rows = [
                [None if rng.random() < 0.25 else rng.randint(1, 9) for _ in range(width)]
                for _ in range(height)
            ]
            start = (rng.randrange(height), rng.randrange(width))
            goal = (rng.randrange(height), rng.randrange(width))
            rows[start[0]][start[1]] = rng.randint(1, 9)
            rows[goal[0]][goal[1]] = rng.randint(1, 9)
            grid = Grid.from_rows(rows, start, goal)
            result = bidirectional_dijkstra(grid)
            expected = bellman_ford_cost(grid)
            with self.subTest(case=case, start=start, goal=goal):
                self.assertEqual(result.cost, expected)
                self.assertEqual(result.cost, dijkstra(grid).cost)
                self.assertEqual(result.cost, astar(grid).cost)
                self.assertEqual(result.reached, expected is not None)
                self.assertGreaterEqual(result.pq_pushes, result.pq_pops)
                if expected is None:
                    self.assertEqual(result.path, ())
                else:
                    self.assertEqual(grid.path_cost(result.path), expected)


if __name__ == "__main__":
    unittest.main()
