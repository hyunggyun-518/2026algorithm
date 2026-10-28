import argparse
import csv
import hashlib
from collections import deque
from dataclasses import dataclass
from io import StringIO
from random import Random

from pathfinding import Grid
from pathfinding.grid import Position

TERRAINS = ("open", "barrier", "maze")
DISTANCES = ("near", "far")
CORE_SIZE = 101
CORE_SEEDS = tuple(range(12))
MANIFEST_FIELDS = (
    "case_id",
    "terrain",
    "distance",
    "size",
    "seed",
    "start_row",
    "start_col",
    "goal_row",
    "goal_col",
    "manhattan_steps",
    "shortest_steps",
    "walkable_cells",
    "grid_sha256",
)


def _positions(size: int) -> tuple[Position, Position, Position]:
    center = size // 2
    if center % 2 == 0:
        center += 1
    near = (center - 2 * max(1, size // 20), center)
    far_coordinate = size - 1 - size // 10
    if far_coordinate % 2 == 0:
        far_coordinate -= 1
    return (center, center), near, (far_coordinate, far_coordinate)


@dataclass(frozen=True)
class MapCase:
    terrain: str
    distance: str
    size: int
    seed: int

    def __post_init__(self) -> None:
        if self.terrain not in TERRAINS:
            raise ValueError("unknown terrain")
        if self.distance not in DISTANCES:
            raise ValueError("unknown distance class")
        if type(self.size) is not int or self.size < 11 or self.size % 2 != 1:
            raise ValueError("size must be an odd integer of at least 11")
        if type(self.seed) is not int or not 0 <= self.seed < 2**64:
            raise ValueError("seed must be a 64-bit nonnegative integer")

    @property
    def case_id(self) -> str:
        return f"{self.terrain}-{self.distance}-{self.size}-{self.seed:02d}"

    @property
    def start(self) -> Position:
        return _positions(self.size)[0]

    @property
    def goal(self) -> Position:
        _, near, far = _positions(self.size)
        return near if self.distance == "near" else far


def _open_topology(size: int) -> list[list[bool]]:
    return [[True] * size for _ in range(size)]


def _barrier_topology(size: int, rng: Random) -> list[list[bool]]:
    walkable = _open_topology(size)
    for index in range(1, 5):
        column = 2 * ((index * (size - 1) + 5) // 10)
        if index % 2 == 1:
            gate = rng.randint(size // 8, 3 * size // 8)
        else:
            gate = rng.randint(5 * size // 8, 7 * size // 8)
        for row in range(size):
            walkable[row][column] = False
        for row in range(max(0, gate - 1), min(size, gate + 2)):
            walkable[row][column] = True
    return walkable


def _maze_topology(size: int, rng: Random) -> list[list[bool]]:
    walkable = [[False] * size for _ in range(size)]
    walkable[1][1] = True
    stack = [(1, 1)]
    while stack:
        row, column = stack[-1]
        candidates = []
        for next_row, next_column in (
            (row - 2, column),
            (row, column + 2),
            (row + 2, column),
            (row, column - 2),
        ):
            if 1 <= next_row < size - 1 and 1 <= next_column < size - 1:
                if not walkable[next_row][next_column]:
                    candidates.append((next_row, next_column))
        if candidates:
            next_row, next_column = rng.choice(candidates)
            walkable[(row + next_row) // 2][(column + next_column) // 2] = True
            walkable[next_row][next_column] = True
            stack.append((next_row, next_column))
        else:
            stack.pop()

    for row in range(1, size - 1, 2):
        for column in range(1, size - 1, 2):
            for next_row, next_column in ((row + 2, column), (row, column + 2)):
                if next_row < size - 1 and next_column < size - 1:
                    middle = ((row + next_row) // 2, (column + next_column) // 2)
                    if not walkable[middle[0]][middle[1]] and rng.random() < 0.12:
                        walkable[middle[0]][middle[1]] = True

    start, near, _ = _positions(size)
    for row in range(near[0], start[0] + 1):
        walkable[row][start[1]] = True
    return walkable


def build_grid(case: MapCase) -> Grid:
    terrain_code = TERRAINS.index(case.terrain) + 1
    rng = Random((terrain_code << 64) + case.seed)
    if case.terrain == "open":
        walkable = _open_topology(case.size)
    elif case.terrain == "barrier":
        walkable = _barrier_topology(case.size, rng)
    else:
        walkable = _maze_topology(case.size, rng)
    rows = [
        [rng.randint(1, 9) if walkable[row][column] else None for column in range(case.size)]
        for row in range(case.size)
    ]
    return Grid.from_rows(rows, case.start, case.goal)


def shortest_steps(grid: Grid) -> int | None:
    queue = deque([(grid.start, 0)])
    visited = {grid.start}
    while queue:
        position, steps = queue.popleft()
        if position == grid.goal:
            return steps
        for neighbor in grid.adjacent(position):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, steps + 1))
    return None


def grid_sha256(grid: Grid) -> str:
    content = "\n".join(
        "".join("#" if cost is None else str(cost) for cost in row)
        for row in grid.costs
    )
    return hashlib.sha256(content.encode("ascii")).hexdigest()


def render_topology(grid: Grid) -> str:
    rows = []
    for row in range(grid.height):
        symbols = []
        for column in range(grid.width):
            position = (row, column)
            if position == grid.start:
                symbols.append("S")
            elif position == grid.goal:
                symbols.append("G")
            elif grid.costs[row][column] is None:
                symbols.append("#")
            else:
                symbols.append(".")
        rows.append("".join(symbols))
    return "\n".join(rows)


def core_cases() -> tuple[MapCase, ...]:
    return tuple(
        MapCase(terrain, distance, CORE_SIZE, seed)
        for terrain in TERRAINS
        for distance in DISTANCES
        for seed in CORE_SEEDS
    )


def manifest_csv(cases: tuple[MapCase, ...] | None = None) -> str:
    output = StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(MANIFEST_FIELDS)
    for case in core_cases() if cases is None else cases:
        grid = build_grid(case)
        steps = shortest_steps(grid)
        if steps is None:
            raise ValueError(f"unreachable case: {case.case_id}")
        writer.writerow(
            (
                case.case_id,
                case.terrain,
                case.distance,
                case.size,
                case.seed,
                case.start[0],
                case.start[1],
                case.goal[0],
                case.goal[1],
                abs(case.start[0] - case.goal[0]) + abs(case.start[1] - case.goal[1]),
                steps,
                sum(cost is not None for row in grid.costs for cost in row),
                grid_sha256(grid),
            )
        )
    return output.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("manifest", "sample"))
    parser.add_argument("--size", type=int, default=21)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--distance", choices=DISTANCES, default="far")
    arguments = parser.parse_args()
    if arguments.mode == "manifest":
        print(manifest_csv(), end="")
    else:
        for terrain in TERRAINS:
            case = MapCase(terrain, arguments.distance, arguments.size, arguments.seed)
            grid = build_grid(case)
            print(f"{case.case_id}: shortest_steps={shortest_steps(grid)}")
            print(render_topology(grid))
            print()


if __name__ == "__main__":
    main()
