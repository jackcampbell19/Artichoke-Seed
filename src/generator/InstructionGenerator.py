

class InstructionGenerator:

    CUP_HOLDER_POSITION_HIDDEN = 0
    CUP_HOLDER_POSITION_STANDARD = 1

    CONFIGURE_SPEED = 0

    @staticmethod
    def home():
        return [0b00000000]

    @staticmethod
    def move(x, y, z, subspace):
        axis_filter = 0b0000
        if x is None and y is None and z is not None:
            axis_filter = 0b0110
            x = 0
            y = 0
        elif x is not None and y is None and z is None:
            axis_filter = 0b0010
            z = 0
            y = 0
        elif x is None and y is not None and z is None:
            axis_filter = 0b0100
            x = 0
            z = 0
        return [
            (0b0001 << 4) | ((1 if subspace else 0) << 3) | axis_filter,
            x >> 8,
            (x & 255),
            y >> 8,
            (y & 255),
            z >> 8,
            (z & 255)
        ]

    @staticmethod
    def dispense_paint(white, black, blue, yellow, red):
        return [
            0b0100 << 4,
            white,
            black,
            blue,
            yellow,
            red
        ] + [0 for _ in range(15)]

    @staticmethod
    def load_tool(tool):
        return [
            (0b0010 << 4) | (tool & 0b1111)
        ]

    @staticmethod
    def set_cup_holder_position(position, move_tool=False):
        return [
            (0b0011 << 4) | (position & 0b1111) | (0b1000 if move_tool else 0)
        ]

    @staticmethod
    def configure(parameter, values):
        return [
            (0b0101 << 4),
            parameter
        ] + values + [0 for _ in range(24 - len(values))]

    @staticmethod
    def configure_speed(ramp, speed_min, speed_max):
        return InstructionGenerator.configure(
            InstructionGenerator.CONFIGURE_SPEED, [
                ramp >> 8,
                ramp & 0b11111111,
                speed_min >> 8,
                speed_min & 0b11111111,
                speed_max >> 8,
                speed_max & 0b11111111
            ]
        )

    @staticmethod
    def wash_tool():
        return [8 << 4]

