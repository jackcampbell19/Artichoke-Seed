from typing import List, Tuple
import cv2
import numpy as np
import math
from .VectorUtil import distance


def contour_length(contour: List[Tuple[int, int]]) -> float:
    return cv2.arcLength(np.array(contour), False)


def average_distance(outline: List[Tuple[int, int]]) -> float:
    num_points = len(outline)
    if num_points < 2:
        return math.inf
    distances = []
    for i in range(num_points):
        point1 = outline[i]
        point2 = outline[(i + 1) % num_points]  # Added modulus operator to account for last point
        dist = math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
        distances.append(dist)
    avg_distance = sum(distances) / len(distances)
    return avg_distance


def simplify_path(path: List[Tuple[int, int]], target_average: float, iteration_max: int = 15) -> List[Tuple[int, int]]:
    """
    Simplifies a given outline using the Ramer-Douglas-Peucker algorithm until the average
    line length is roughly target_average.

    :param iteration_max: Max iteration of simplification.
    :param path: A list of (x, y) tuples representing the original outline points.
    :param target_average: A float value representing the target average line length.
    :return: A list of (x, y) tuples representing the simplified outline points.
    """
    path_len = contour_length(path)
    upper_bound = 1
    lower_bound = 0
    chosen_path = path
    for _ in range(iteration_max):
        mid_bound = lower_bound + (abs(lower_bound - upper_bound) / 2)
        approx = cv2.approxPolyDP(np.array(path), mid_bound * path_len, True)
        chosen_path = [tuple(point) for point in approx.reshape(-1, 2)]
        mid_bound = lower_bound + (abs(lower_bound - upper_bound) / 2)
        avg_dist = average_distance(chosen_path)
        if avg_dist > target_average:
            upper_bound = mid_bound
        else:
            lower_bound = mid_bound
    return chosen_path


def split_long_lines(outline: List[Tuple[int, int]], max_continuous_length: float) -> List[Tuple[int, int]]:
    new_outline = []
    for i in range(len(outline)):
        point1 = outline[i]
        point2 = outline[(i + 1) % len(outline)]
        dist = math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
        # If distance between points exceed max_continuous_length
        if dist > max_continuous_length:
            # Calculate how many new points needs to be added
            num_new_points = int(dist // max_continuous_length)
            for j in range(num_new_points):
                t = (j + 1) / (num_new_points + 1)
                new_point = (int((1 - t) * point1[0] + t * point2[0]), int((1 - t) * point1[1] + t * point2[1]))
                new_outline.append(new_point)
        new_outline.append(point2)
    return new_outline


def remove_short_lines(outline: List[Tuple[int, int]], smallest_length: float) -> List[Tuple[int, int]]:
    new_outline = [outline[0]]
    for i in range(len(outline)):
        point1 = new_outline[-1]
        point2 = outline[(i + 1) % len(outline)]
        dist = distance(point1, point2)
        # If distance between points is at least smallest_length
        if dist >= smallest_length:
            new_outline.append(point2)
    return new_outline


def filter_short_contours(contours: List[List[Tuple[int, int]]], min_length: float) -> List[List[Tuple[int, int]]]:
    return [contour for contour in contours if contour_length(contour) >= min_length]