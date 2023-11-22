from interpreter import JPEGInterpreter
from generator import FileGenerator

if __name__ == '__main__':
    interpreter = JPEGInterpreter(path='images/heart.png')
    outlines = interpreter.generate_outlines()

    outline = outlines[0]
    outline_simp = interpreter.simplify_outline(outline, 0.001)
    outline_split = interpreter.split_long_lines(outline_simp, 1000)
    outline_refined = interpreter.remove_short_lines(outline_split, 5)

    print(len(outline))
    print(len(outline_simp))
    print(len(outline_split))
    print(len(outline_refined))

    interpreter.generate_image_from_contours([outline_refined], 'test-images/simp.jpeg')

    fg = FileGenerator()
    fg.convert_outline_to_instructions(outline_refined)
    fg.save_instructions_to_file(file_path='/Users/jackcampbell/workspace/artichoke/Artichoke-Farmer/src/test.art')
