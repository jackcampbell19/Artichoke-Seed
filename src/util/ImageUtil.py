import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from typing import Dict, Tuple, List
from scipy.stats import mode
from skimage import measure
import cv2 as cv
from random import randint


def save_contours_as_image(width, height, contours: List[List[Tuple[int, int]]], output_path: str) -> None:
    # Assume the size of the image from the maximum outline points
    # Create an empty image to start with
    new_image = np.zeros((height, width, 3), np.uint8)
    # Draw each contour
    for contour in contours:
        contour_array = np.array(contour)
        cv.drawContours(
            new_image,
            [contour_array],
            -1,
            (randint(0, 255), randint(0, 255), randint(0, 255)),
            4
        )
    # Save image at output_path
    cv.imwrite(output_path, new_image)


def simplify_colors(image: Image, max_colors: int) -> Image:
    """
    Simplifies the image colors such that there are no more than max_colors.
    """
    image_array = np.array(image)  # Convert image to array
    # Reshape the image to be a list of RGB pixels
    pixels = image_array.reshape(-1, 3)
    # Run KMeans on the pixel data
    kmeans = KMeans(max_colors, n_init=10)
    kmeans.fit(pixels)
    # Replace each pixel's color with the color of its centroid
    simplified_pixels = kmeans.cluster_centers_[kmeans.labels_]
    simplified_pixels = simplified_pixels.astype(int)  # Convert colors to ints
    # Reshape the pixel data to the original image shape
    simplified_image_array = simplified_pixels.reshape(image_array.shape)
    return Image.fromarray(simplified_image_array.astype('uint8'), 'RGB')


def split_layers(image: Image.Image) -> Dict[Tuple[int, int, int], Image.Image]:
    """
    Splits the image into a series of color masks. Each color mask has a black
    background and white mask. Returns a map of color to the color mask.
    :param image: The input image.
    :return: A map of color to image mask.
    """
    if image.mode != 'RGB':
        raise ValueError("Input image must be in RGB mode")
    pixel_values = np.array(image)
    unique_colors = np.unique(pixel_values.reshape(-1, 3), axis=0)
    color_mask_images = {}
    for color in unique_colors:
        mask_pixels = np.all(pixel_values == color, axis=-1) * 255
        mask_image = Image.fromarray(mask_pixels.astype(np.uint8), mode='L')
        color_mask_images[tuple(color)] = mask_image
    return color_mask_images


def get_surrounding(image: np.ndarray, label_image: np.ndarray, region_label: int) -> np.ndarray:
    # Getting the coordinates of the region
    x, y = np.where(label_image == region_label)
    # Getting the coordinates of surrounding pixels
    surrounding_x = np.clip(np.concatenate([x-1, x, x+1]), 0, image.shape[0]-1)
    surrounding_y = np.clip(np.concatenate([y-1, y, y+1]), 0, image.shape[1]-1)
    # Making sure not to include the region pixels
    mask = (label_image[surrounding_x, surrounding_y] != region_label)[:, None]  # Make the mask have shape (12, 1) instead (12,)
    surrounding = image[surrounding_x, surrounding_y] * mask
    return surrounding


def reduce_noise(image: Image.Image, min_area_retention: int = 25) -> Image.Image:
    """
    Iterates over the pixels in the image and removes any pixel islands
    with an area < min_area_retention and replaces them with the most
    prevalent surrounding color.
    :param min_area_retention: The minimum area of an island to retain.
    :param image: The input image.
    :return: The output image.
    """
    # Converting image to an array
    image_arr = np.array(image)
    # Grayscale conversion (required for regionprops)
    gray_img = cv.cvtColor(image_arr, cv.COLOR_RGB2GRAY)
    # Labeling the regions in the image
    label_image = measure.label(gray_img)
    # Iterating over regions
    for region in measure.regionprops(label_image):
        if region.area < min_area_retention:
            # If the region area is smaller than threshold, recolor it
            # Get the most prevalent color in the surrounding pixels
            surrounding = get_surrounding(image_arr, label_image, region.label)
            prevalent_color = mode(surrounding, axis=None)[0]
            # Apply the prevalent color to the region
            image_arr[label_image == region.label] = prevalent_color
    # Converting array back to an image
    output_image = Image.fromarray(image_arr)
    return output_image
