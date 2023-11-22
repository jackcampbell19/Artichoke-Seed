from typing import Tuple
from math import sqrt


def distance(v0: Tuple[int, int], v1: Tuple[int, int]) -> float:
    x0, y0 = v0
    x1, y1 = v1
    return sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)
