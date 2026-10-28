from pathfinding import Grid
from pathfinding.astar import astar
from pathfinding.dijkstra import dijkstra


grid = Grid.from_rows(
    [[1, 9, 1], [1, 9, 1], [1, 1, 1]],
    start=(0, 0),
    goal=(0, 2),
)
for name, search in (("Dijkstra", dijkstra), ("A*", astar)):
    result = search(grid)
    print(f"{name}: reached={result.reached}, cost={result.cost}")
    print(f"path={result.path}")
    print(f"expanded={result.expanded}")
