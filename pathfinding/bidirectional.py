from heapq import heappop, heappush

from pathfinding.grid import Grid, Position
from pathfinding.result import SearchResult


def _discard_invalid(
    queue: list[tuple[int, Position]],
    distances: dict[Position, int],
    settled: set[Position],
) -> int:
    removed = 0
    while queue:
        distance, position = queue[0]
        if position not in settled and distance == distances[position]:
            break
        heappop(queue)
        removed += 1
    return removed


def _reconstruct_path(
    start: Position,
    goal: Position,
    meeting: Position,
    forward_parent: dict[Position, Position],
    reverse_parent: dict[Position, Position],
) -> tuple[Position, ...]:
    forward_path = [meeting]
    while forward_path[-1] != start:
        forward_path.append(forward_parent[forward_path[-1]])
    forward_path.reverse()

    position = meeting
    while position != goal:
        position = reverse_parent[position]
        forward_path.append(position)
    return tuple(forward_path)


def bidirectional_dijkstra(grid: Grid) -> SearchResult:
    if grid.start == grid.goal:
        return SearchResult(True, 0, (grid.start,), 0, 0, 0)

    forward_distances = {grid.start: 0}
    reverse_distances = {grid.goal: 0}
    forward_parent: dict[Position, Position] = {}
    reverse_parent: dict[Position, Position] = {}
    forward_queue = [(0, grid.start)]
    reverse_queue = [(0, grid.goal)]
    forward_settled: set[Position] = set()
    reverse_settled: set[Position] = set()
    best_cost: int | None = None
    meeting: Position | None = None
    expanded = 0
    pq_pushes = 2
    pq_pops = 0

    while True:
        pq_pops += _discard_invalid(forward_queue, forward_distances, forward_settled)
        pq_pops += _discard_invalid(reverse_queue, reverse_distances, reverse_settled)
        if not forward_queue or not reverse_queue:
            break
        if best_cost is not None and forward_queue[0][0] + reverse_queue[0][0] >= best_cost:
            break

        if forward_queue[0][0] <= reverse_queue[0][0]:
            queue = forward_queue
            distances = forward_distances
            other_distances = reverse_distances
            parents = forward_parent
            settled = forward_settled
            neighbors = grid.forward_neighbors
            endpoint = grid.goal
        else:
            queue = reverse_queue
            distances = reverse_distances
            other_distances = forward_distances
            parents = reverse_parent
            settled = reverse_settled
            neighbors = grid.reverse_neighbors
            endpoint = grid.start

        distance, position = heappop(queue)
        pq_pops += 1
        settled.add(position)
        if position in other_distances:
            candidate = distance + other_distances[position]
            if best_cost is None or candidate < best_cost:
                best_cost = candidate
                meeting = position
        if position == endpoint:
            continue

        expanded += 1
        for neighbor, edge_cost in neighbors(position):
            if neighbor in settled:
                continue
            candidate = distance + edge_cost
            if neighbor not in distances or candidate < distances[neighbor]:
                distances[neighbor] = candidate
                parents[neighbor] = position
                heappush(queue, (candidate, neighbor))
                pq_pushes += 1
                if neighbor in other_distances:
                    connection_cost = candidate + other_distances[neighbor]
                    if best_cost is None or connection_cost < best_cost:
                        best_cost = connection_cost
                        meeting = neighbor

    if best_cost is None:
        return SearchResult(False, None, (), expanded, pq_pushes, pq_pops)
    assert meeting is not None
    path = _reconstruct_path(grid.start, grid.goal, meeting, forward_parent, reverse_parent)
    return SearchResult(True, best_cost, path, expanded, pq_pushes, pq_pops)
