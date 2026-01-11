from manim import *

class MinecraftBlock(Scene):
    def construct(self):
        # ============
        # BLOCK POINTS
        # ============
        top = Polygon(
            [-2, 1, 0], [0, 2, 0], [2, 1, 0], [0, 0, 0],
            stroke_color=WHITE, stroke_width=4, fill_opacity=0
        )

        left = Polygon(
            [-2, 1, 0], [-2, -1, 0], [0, -2, 0], [0, 0, 0],
            stroke_color=WHITE, stroke_width=4, fill_opacity=0
        )

        right = Polygon(
            [0, 0, 0], [2, 1, 0], [2, -1, 0], [0, -2, 0],
            stroke_color=WHITE, stroke_width=4, fill_opacity=0
        )

        # ============
        # DRAW OUTLINE
        # ============
        self.play(Create(top))
        self.play(Create(left))
        self.play(Create(right))

        self.wait(0.5)

        # ============
        # FILL COLORS
        # ============
        grass = top.copy().set_fill(GREEN, 1).set_stroke(width=0)
        dirt_left = left.copy().set_fill("#8B4513", 1).set_stroke(width=0)
        dirt_right = right.copy().set_fill("#5A2E0F", 1).set_stroke(width=0)

        self.play(FadeIn(grass))
        self.play(FadeIn(dirt_left))
        self.play(FadeIn(dirt_right))

        self.wait(2)
