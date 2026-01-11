from manim import *


class xx(Scene):
    def construct(self):
        BROWN = "#8B4513"
        # Parse the mc.txt file for color mapping and pixel data
        mapping = {}
        matrix = []
        with open("mc.txt", "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Lines defining mapping: e.g. 1 = "green"
                if "=" in line:
                    key, val = line.split("=")
                    mapping[key.strip()] = val.strip().strip('"')
                # Lines of 0s and 1s: pixel rows
                elif set(line) <= {"0", "1"}:
                    matrix.append(line)

        rows = len(matrix)
        cols = len(matrix[0]) if rows else 0
        square_size = 0.3  # adjust size as needed

        # Create squares for each pixel: no fill, green stroke
        pixels = VGroup()
        fill_colors = []
        for i, row in enumerate(matrix):
            for j, char in enumerate(row):
                fill_colors.append(mapping.get(char, "white"))
                sq = Square(
                    side_length=square_size,
                    fill_opacity=0,
                    stroke_color=GREEN,
                    stroke_width=2
                )
                # Center the grid around origin
                x = (j - cols / 2) * square_size + square_size / 2
                y = (rows / 2 - i) * square_size - square_size / 2
                sq.move_to([x, y, 0])
                pixels.add(sq)

        # Center the entire logo
        pixels.move_to(ORIGIN)

        # Draw green outline for all pixels
        self.play(
            LaggedStart(*[Create(sq) for sq in pixels], lag_ratio=0.02),
            run_time=2
        )

        # Change stroke to brown
        self.play(
            LaggedStart(*[sq.animate.set_stroke(color=BROWN) for sq in pixels], lag_ratio=0.02),
            run_time=2
        )

        # Fill each square with its mapped color
        self.play(
            LaggedStart(*[sq.animate.set_fill(color, opacity=1) for sq, color in zip(pixels, fill_colors)], lag_ratio=0.02),
            run_time=4
        )

        self.wait(1)

# To render this scene:
# manim -pql manim_minecraft_logo.py MinecraftLogo
