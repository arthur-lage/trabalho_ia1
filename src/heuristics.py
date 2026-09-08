import math
from typing import Tuple

Pos = Tuple[int, int]


def manhattan(a: Pos, b: Pos) -> float:
    """Implemente a distância Manhattan entre duas posições."""
    return float(abs(a[0] - b[0]) + abs(a[1] - b[1]))


def euclidean(a: Pos, b: Pos) -> float:
    """Implemente a distância Euclidiana entre duas posições."""
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
