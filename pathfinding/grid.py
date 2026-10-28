from dataclasses import dataclass
from typing import Iterator

Position = tuple[int, int]
Neighbor = tuple[Position, int]


@dataclass(frozen=True)
class Grid:
    costs: tuple[tuple[int | None, ...], ...]
    start: Position
    goal: Position

    def __post_init__(self) -> None:
        if not self.costs or not self.costs[0]:
            raise ValueError("grid must have positive height and width")
        width = len(self.costs[0])
        if any(len(row) != width for row in self.costs):
            raise ValueError("grid rows must have equal width")
        for row in self.costs:
            for cost in row:
                if cost is not None and (type(cost) is not int or not 1 <= cost <= 9):
                    raise ValueError("traversable costs must be integers from 1 to 9")
        for position in (self.start, self.goal):
            if not self._valid_position(position) or self.costs[position[0]][position[1]] is None:
                raise ValueError("start and goal must be traversable positions")

    @classmethod
    def from_rows(
        cls,
        rows: list[list[int | None]] | tuple[tuple[int | None, ...], ...],
        start: Position,
        goal: Position,
    ) -> "Grid":
        return cls(tuple(tuple(row) for row in rows), start, goal)

    @property
    def height(self) -> int:
        return len(self.costs)

    @property
    def width(self) -> int:
        return len(self.costs[0])

    def _valid_position(self, position: object) -> bool:
        return (
            isinstance(position, tuple)
            and len(position) == 2
            and type(position[0]) is int
            and type(position[1]) is int
            and 0 <= position[0] < self.height
            and 0 <= position[1] < self.width
        )

    def traversable(self, position: Position) -> bool:
        return self._valid_position(position) and self.costs[position[0]][position[1]] is not None

    def adjacent(self, position: Position) -> Iterator[Position]:
        if not self.traversable(position):
            raise ValueError("position must be traversable")
        row, column = position
        for candidate in ((row - 1, column), (row, column + 1), (row + 1, column), (row, column - 1)):
            if self.traversable(candidate):
                yield candidate

    def forward_neighbors(self, position: Position) -> Iterator[Neighbor]:
        for neighbor in self.adjacent(position):
            cost = self.costs[neighbor[0]][neighbor[1]]
            assert cost is not None
            yield neighbor, cost

    def reverse_neighbors(self, position: Position) -> Iterator[Neighbor]:
        if not self.traversable(position):
            raise ValueError("position must be traversable")
        cost = self.costs[position[0]][position[1]]
        assert cost is not None
        for predecessor in self.adjacent(position):
            yield predecessor, cost

    def path_cost(self, path: tuple[Position, ...] | list[Position]) -> int:
        if not path or path[0] != self.start or path[-1] != self.goal:
            raise ValueError("path must run from start to goal")
        total = 0
        for current, next_position in zip(path, path[1:]):
            if next_position not in self.adjacent(current):
                raise ValueError("path contains an invalid move")
            cost = self.costs[next_position[0]][next_position[1]]
            assert cost is not None
            total += cost
        return total
