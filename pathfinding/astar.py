from heapq import heappop, heappush

from pathfinding.grid import Grid, Position
from pathfinding.result import SearchResult


def minimum_entry_cost(grid: Grid) -> int:
    return min(cost for row in grid.costs for cost in row if cost is not None)


def manhattan_lower_bound(position: Position, goal: Position, step_cost: int) -> int:
    return (abs(position[0] - goal[0]) + abs(position[1] - goal[1])) * step_cost


def astar(grid: Grid) -> SearchResult:
    step_cost = minimum_entry_cost(grid)
    distances = {grid.start: 0}
    predecessors: dict[Position, Position] = {}
    queue = [(manhattan_lower_bound(grid.start, grid.goal, step_cost), 0, grid.start)]
    expanded = 0
    pq_pushes = 1
    pq_pops = 0

    while queue:
        _, negative_distance, position = heappop(queue)
        pq_pops += 1
        distance = -negative_distance
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
                priority = candidate + manhattan_lower_bound(neighbor, grid.goal, step_cost)
                heappush(queue, (priority, -candidate, neighbor))
                pq_pushes += 1

    return SearchResult(False, None, (), expanded, pq_pushes, pq_pops)
