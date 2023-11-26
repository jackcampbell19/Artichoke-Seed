import cv2
import numpy as np
from PIL import Image
from typing import List, Tuple
from sklearn.cluster import KMeans
from util import simplify_colors, split_layers, reduce_noise


class ImageInterpreter:
    """
    Interprets a JPEG image to produce a series of paths that can
    be converted into instructions.
    """

    def __init__(self, path: str):
        self._path = path
        self._image: Image.Image = Image.open(self._path)

    def get_size(self):
        return self._image.size

    def scale_image(self, size: Tuple[int, int]) -> None:
        """
        Scales the image to the provided size.
        Args:
            size: A tuple containing the (width, height) to which the image should be scaled.
        Returns:
            The scaled Image object.
        """
        scaled_image = self._image.resize(size, Image.LANCZOS)
        self._image = scaled_image

    def split_color_layers(self):
        """
        Splits the image into layers, each one representing a specific color.
        :return:
        """
        pass

    def get_outlines(self) -> List[List[Tuple[int, int]]]:
        cv2_image = np.array(self._image)
        grayscale = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY)
        outlines = cv2.Canny(grayscale, 30, 100)
        # findContours returns a list of contours found in the image
        # each contour is a numpy array of (x,y) coordinates of boundary points of the object
        contours, _ = cv2.findContours(outlines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Convert each contour (NumPy array) to a list and then all of these to a Python list
        contours_list = [list(map(tuple, contour.reshape(-1, 2))) for contour in contours]
        return contours_list

    def process(self, max_colors=5):
        output_path = '/Users/jackcampbell/workspace/artichoke/Artichoke-Seed/output/visualization'
        # Simplify colors
        simplified_colors: Image = simplify_colors(self._image, max_colors=max_colors)
        simplified_colors.save(f"{output_path}/simplified-colors.png")
        # Reduce noise
        reduced_noise = reduce_noise(simplified_colors)
        reduced_noise.save(f"{output_path}/reduced-noise.png")
        # Separate layers
        split_colors = split_layers(reduced_noise)
        for color in split_colors.keys():
            color_mask = split_colors[color]
            color_mask.save(f"{output_path}/{color[0]}-{color[1]}-{color[2]}.png")

