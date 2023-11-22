import math
from typing import List, Tuple
from .InstructionGenerator import InstructionGenerator as ig
from util import distance
from math import ceil


class FileGenerator:

    def __init__(self):
        self._max_continuous_length: float = 6000
        self._clearance_z: int = 2500
        self._contact_z: int = 1600
        self._instructions = []

    def quick_z_speed(self):
        self._instructions.append(
            ig.configure_speed(300, 80, 120)
        )

    def normal_speed(self):
        # self._instructions.append(
        #     ig.configure_speed(500, 120, 600)
        # )
        self._instructions.append(
            ig.configure_speed(800, 120, 1200)
        )

    def dip_paint_brush(self):
        self.quick_z_speed()
        self._instructions += [
            ig.move(None, None, 2000, False),
            ig.set_cup_holder_position(ig.CUP_HOLDER_POSITION_STANDARD),
            ig.move(None, None, 10000, False),
            ig.move(None, None, 8000, False),
            ig.move(None, None, 9000, False),
            ig.move(None, None, 2000, False),
            ig.set_cup_holder_position(ig.CUP_HOLDER_POSITION_HIDDEN),
        ]
        self.normal_speed()

    def convert_outline_to_instructions(self, outline: List[Tuple[int, int]]):
        fx, fy = outline[0]
        self._instructions.append(
            ig.move(fx, fy, self._clearance_z, subspace=True)
        )
        running_length: float = math.inf
        for i in range(len(outline) - 1):
            v0, v1 = outline[i], outline[i + 1]
            length: float = distance(v0, v1)
            if running_length + length < self._max_continuous_length:
                running_length += length
                x, y = v1
                self._instructions.append(
                    ig.move(x, y, self._contact_z, subspace=True)
                )
            else:
                self.dip_paint_brush()
                sx, sy = v0
                ex, ey = v1
                self._instructions += [
                    ig.move(sx, sy, self._contact_z, subspace=True),
                    ig.move(ex, ey, self._contact_z, subspace=True),
                ]
                running_length = distance(v0, v1)
        self._instructions.append(
            ig.move(None, None, self._clearance_z, subspace=True)
        )

    def get_instructions(self):
        return self._instructions

    def save_instructions_to_file(self, file_path: str):
        with open(file_path, 'wb') as f:
            for instruction in self._instructions:
                f.write(bytes(instruction))
