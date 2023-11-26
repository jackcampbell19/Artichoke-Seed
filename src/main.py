from interpreter import ImageInterpreter
from generator import FileGenerator
from util import *


ROOT_PATH = '/Users/jackcampbell/workspace/artichoke/Artichoke-Seed'


if __name__ == '__main__':
    interpreter = ImageInterpreter(f"{ROOT_PATH}/input/images/butterfly.jpg")
    outlines = interpreter.get_outlines()
    outlines = filter_short_contours(outlines, min_length=100)
    outlines = [simplify_path(p, target_average=50) for p in outlines]
    width, height = interpreter.get_size()
    save_contours_as_image(width, height, outlines, f"{ROOT_PATH}/output/visualization/contours.png")
