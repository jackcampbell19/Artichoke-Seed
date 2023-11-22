import cv2
import numpy as np
from PIL import Image
from typing import List, Tuple
import math
from util import distance


class JPEGInterpreter:

    def __init__(self, path: str):
        self._path = path
        self._image = Image.open(self._path)

    def scale_image(self, size: Tuple[int, int]):
        """Scales the image to the provided size.

        Args:
            size: A tuple containing the (width, height) to which the image should be scaled.

        Returns:
            The scaled Image object.
        """
        scaled_image = self._image.resize(size, Image.LANCZOS)
        self._image = scaled_image

    def generate_outlines(self) -> List[List[Tuple[int, int]]]:
        cv2_image = np.array(self._image)
        grayscale = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY)
        outlines = cv2.Canny(grayscale, 30, 100)
        # findContours returns a list of contours found in the image
        # each contour is a numpy array of (x,y) coordinates of boundary points of the object
        contours, _ = cv2.findContours(outlines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Convert each contour (NumPy array) to a list and then all of these to a Python list
        contours_list = [list(map(tuple, contour.reshape(-1, 2))) for contour in contours]
        return contours_list

    def generate_image_from_contours(self, contours: List[List[Tuple[int, int]]], output_path: str) -> None:
        # Assume the size of the image from the maximum outline points
        # Create an empty image to start with
        new_image = np.zeros(self._image.size, np.uint8)
        # Draw each contour
        for contour in contours:
            contour_array = np.array(contour)
            cv2.drawContours(new_image, [contour_array], -1, (255, 255, 255), 4)
        # Save image at output_path
        cv2.imwrite(output_path, new_image)

    @staticmethod
    def simplify_outline(outline: List[Tuple[int, int]], factor: float) -> List[Tuple[int, int]]:
        epsilon = factor * cv2.arcLength(np.array(outline), True)
        # approximate the contour and initialize the result list
        approx = cv2.approxPolyDP(np.array(outline), epsilon, True)
        # Convert it back to a Python list
        simplified_outline = [tuple(point) for point in approx.reshape(-1, 2)]
        return simplified_outline

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def calculate_average_distance(outline: List[Tuple[int, int]]) -> float:
        num_points = len(outline)
        if num_points < 2:
            raise Exception("The minimum number of points in the outline should be 2.")
        distances = []
        for i in range(num_points):
            point1 = outline[i]
            point2 = outline[(i + 1) % num_points]  # Added modulus operator to account for last point
            distance = math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
            distances.append(distance)
        avg_distance = sum(distances) / len(distances)
        return avg_distance
