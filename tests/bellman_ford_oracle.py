from pathfinding import Grid


def bellman_ford_cost(grid: Grid) -> int | None:
    vertices = [
        (row, column)
        for row in range(grid.height)
        for column in range(grid.width)
        if grid.costs[row][column] is not None
    ]
    distances: dict[tuple[int, int], int | None] = {vertex: None for vertex in vertices}
    distances[grid.start] = 0

    for _ in range(len(vertices) - 1):
        changed = False
        for row, column in vertices:
            current = distances[(row, column)]
            if current is None:
                continue
            for next_row, next_column in (
                (row - 1, column),
                (row, column + 1),
                (row + 1, column),
                (row, column - 1),
            ):
                if not (0 <= next_row < grid.height and 0 <= next_column < grid.width):
                    continue
                edge_cost = grid.costs[next_row][next_column]
                if edge_cost is None:
                    continue
                neighbor = (next_row, next_column)
                candidate = current + edge_cost
                if distances[neighbor] is None or candidate < distances[neighbor]:
                    distances[neighbor] = candidate
                    changed = True
        if not changed:
            break

    return distances[grid.goal]
