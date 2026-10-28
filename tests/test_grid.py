import unittest

from pathfinding import Grid


class GridTests(unittest.TestCase):
    def test_forward_and_reverse_edge_costs(self):
        grid = Grid.from_rows([[1, 9], [2, None]], (0, 0), (0, 1))
        self.assertEqual(list(grid.forward_neighbors((0, 0))), [((0, 1), 9), ((1, 0), 2)])
        self.assertEqual(list(grid.reverse_neighbors((0, 1))), [((0, 0), 9)])

    def test_path_cost_excludes_start(self):
        grid = Grid.from_rows([[7, 3], [2, 4]], (0, 0), (1, 1))
        self.assertEqual(grid.path_cost(((0, 0), (0, 1), (1, 1))), 7)
        self.assertEqual(grid.path_cost(((0, 0), (1, 0), (1, 1))), 6)

    def test_same_start_and_goal(self):
        grid = Grid.from_rows([[5]], (0, 0), (0, 0))
        self.assertEqual(grid.path_cost(((0, 0),)), 0)

    def test_rejects_ragged_rows_and_invalid_costs(self):
        for rows in ([[1, 2], [3]], [[0]], [[10]], [[True]], [[]], []):
            with self.subTest(rows=rows):
                with self.assertRaises(ValueError):
                    Grid.from_rows(rows, (0, 0), (0, 0))

    def test_rejects_wall_or_out_of_bounds_endpoints(self):
        for start, goal in (((0, 1), (0, 0)), ((0, 0), (1, 0)), ((-1, 0), (0, 0))):
            with self.subTest(start=start, goal=goal):
                with self.assertRaises(ValueError):
                    Grid.from_rows([[1, None]], start, goal)

    def test_rejects_non_adjacent_path(self):
        grid = Grid.from_rows([[1, 1], [1, 1]], (0, 0), (1, 1))
        with self.assertRaises(ValueError):
            grid.path_cost(((0, 0), (1, 1)))


if __name__ == "__main__":
    unittest.main()
