from heapq import heappop, heappush

from pathfinding.grid import Grid, Position
from pathfinding.result import SearchResult


def dijkstra(grid: Grid) -> SearchResult:
    distances = {grid.start: 0}
    predecessors: dict[Position, Position] = {}
    queue = [(0, grid.start)]
    expanded = 0
    pq_pushes = 1
    pq_pops = 0

    while queue:
        distance, position = heappop(queue)
        pq_pops += 1
        if distance != distances[position]:
            continue
        if position == grid.goal:
            path = [position]
            while path[-1] != grid.start:
                path.append(predecessors[path[-1]])
            path.reverse()
            return SearchResult(True, distance, tuple(path), expanded, pq_pushes, pq_pops)

        expanded += 1
        for neighbor, edge_cost in grid.forward_neighbors(position):
            candidate = distance + edge_cost
            if neighbor not in distances or candidate < distances[neighbor]:
                distances[neighbor] = candidate
                predecessors[neighbor] = position
                heappush(queue, (candidate, neighbor))
                pq_pushes += 1

    return SearchResult(False, None, (), expanded, pq_pushes, pq_pops)
