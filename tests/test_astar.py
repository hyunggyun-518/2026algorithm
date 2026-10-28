import random
import unittest

from pathfinding import Grid
from pathfinding.astar import astar, manhattan_lower_bound, minimum_entry_cost
from pathfinding.dijkstra import dijkstra
from tests.bellman_ford_oracle import bellman_ford_cost


class AStarTests(unittest.TestCase):
    def test_weighted_detour_matches_both_references(self) -> None:
        grid = Grid.from_rows(
            [[1, 9, 1], [1, 9, 1], [1, 1, 1]],
            start=(0, 0),
            goal=(0, 2),
        )
        result = astar(grid)
        self.assertTrue(result.reached)
        self.assertEqual(result.cost, 6)
        self.assertEqual(result.cost, dijkstra(grid).cost)
        self.assertEqual(result.cost, bellman_ford_cost(grid))
        self.assertEqual(grid.path_cost(result.path), result.cost)

    def test_wall_detour(self) -> None:
        grid = Grid.from_rows(
            [[1, None, 1], [1, None, 1], [1, 1, 1]],
            start=(0, 0),
            goal=(0, 2),
        )
        result = astar(grid)
        self.assertEqual(result.cost, 6)
        self.assertEqual(grid.path_cost(result.path), 6)

    def test_unreachable_goal(self) -> None:
        grid = Grid.from_rows([[1, None, 1]], start=(0, 0), goal=(0, 2))
        result = astar(grid)
        self.assertFalse(result.reached)
        self.assertIsNone(result.cost)
        self.assertEqual(result.path, ())
        self.assertEqual(result.expanded, 1)

    def test_start_equals_goal(self) -> None:
        grid = Grid.from_rows([[7]], start=(0, 0), goal=(0, 0))
        result = astar(grid)
        self.assertTrue(result.reached)
        self.assertEqual(result.cost, 0)
        self.assertEqual(result.path, ((0, 0),))
        self.assertEqual(result.expanded, 0)

    def test_tie_breaking_is_deterministic(self) -> None:
        grid = Grid.from_rows(
            [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
            start=(0, 0),
            goal=(2, 2),
        )
        results = [astar(grid) for _ in range(5)]
        self.assertTrue(all(result.path == results[0].path for result in results))
        self.assertEqual(results[0].cost, 4)
        self.assertEqual(grid.path_cost(results[0].path), 4)

    def test_heuristic_uses_smallest_traversable_cost(self) -> None:
        grid = Grid.from_rows([[4, 7, 6], [5, None, 8]], start=(0, 0), goal=(0, 2))
        self.assertEqual(minimum_entry_cost(grid), 4)
        self.assertEqual(manhattan_lower_bound(grid.start, grid.goal, 4), 8)
        self.assertEqual(manhattan_lower_bound(grid.goal, grid.goal, 4), 0)

    def test_goal_guidance_on_uniform_open_grid(self) -> None:
        grid = Grid.from_rows([[1] * 9 for _ in range(9)], start=(0, 0), goal=(8, 8))
        result = astar(grid)
        baseline = dijkstra(grid)
        self.assertEqual(result.cost, baseline.cost)
        self.assertEqual(result.cost, 16)
        self.assertEqual(grid.path_cost(result.path), 16)
        self.assertLess(result.expanded, baseline.expanded)

    def test_small_random_grids_match_oracle_and_dijkstra(self) -> None:
        rng = random.Random(20261029)
        for case in range(120):
            height = rng.randint(2, 6)
            width = rng.randint(2, 6)
            rows = [
                [None if rng.random() < 0.25 else rng.randint(1, 9) for _ in range(width)]
                for _ in range(height)
            ]
            start = (rng.randrange(height), rng.randrange(width))
            goal = (rng.randrange(height), rng.randrange(width))
            rows[start[0]][start[1]] = rng.randint(1, 9)
            rows[goal[0]][goal[1]] = rng.randint(1, 9)
            grid = Grid.from_rows(rows, start, goal)
            result = astar(grid)
            oracle_cost = bellman_ford_cost(grid)
            with self.subTest(case=case, start=start, goal=goal):
                self.assertEqual(result.cost, oracle_cost)
                self.assertEqual(result.cost, dijkstra(grid).cost)
                self.assertEqual(result.reached, oracle_cost is not None)
                self.assertGreaterEqual(result.pq_pushes, result.pq_pops)
                if oracle_cost is None:
                    self.assertEqual(result.path, ())
                else:
                    self.assertEqual(grid.path_cost(result.path), oracle_cost)

    def test_heuristic_is_admissible_and_consistent(self) -> None:
        rng = random.Random(20261030)
        for case in range(40):
            height = rng.randint(2, 5)
            width = rng.randint(2, 5)
            rows = [
                [None if rng.random() < 0.2 else rng.randint(1, 9) for _ in range(width)]
                for _ in range(height)
            ]
            goal = (rng.randrange(height), rng.randrange(width))
            rows[goal[0]][goal[1]] = rng.randint(1, 9)
            grid = Grid.from_rows(rows, goal, goal)
            step_cost = minimum_entry_cost(grid)
            for row in range(height):
                for column in range(width):
                    position = (row, column)
                    if not grid.traversable(position):
                        continue
                    estimate = manhattan_lower_bound(position, goal, step_cost)
                    exact = bellman_ford_cost(Grid(grid.costs, position, goal))
                    with self.subTest(case=case, position=position, goal=goal):
                        if exact is not None:
                            self.assertLessEqual(estimate, exact)
                        for neighbor, edge_cost in grid.forward_neighbors(position):
                            neighbor_estimate = manhattan_lower_bound(neighbor, goal, step_cost)
                            self.assertLessEqual(estimate, edge_cost + neighbor_estimate)


if __name__ == "__main__":
    unittest.main()
