from dataclasses import dataclass

from .grid import Position


@dataclass(frozen=True)
class SearchResult:
    reached: bool
    cost: int | None
    path: tuple[Position, ...]
    expanded: int
    pq_pushes: int
    pq_pops: int
