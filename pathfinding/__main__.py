from pathfinding import Grid
from pathfinding.dijkstra import dijkstra


grid = Grid.from_rows(
    [[1, 9, 1], [1, 9, 1], [1, 1, 1]],
    start=(0, 0),
    goal=(0, 2),
)
result = dijkstra(grid)
print(f"reached={result.reached}")
print(f"cost={result.cost}")
print(f"path={result.path}")
print(f"expanded={result.expanded}")
