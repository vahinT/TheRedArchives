from manim import *

class VahinVVMOutlineToRed(Scene):
    def construct(self):
        text = Text("VahinVVM", font_size=72, fill_opacity=0, stroke_color=WHITE)
        text.move_to(ORIGIN)

        # Step 1: Show outline
        self.play(Write(text), run_time=1)
        self.wait(0.5)

        # Step 2: Fill with white
        self.play(text.animate.set_fill(WHITE, opacity=1), run_time=0.5)
        self.wait(0.5)

        # Step 3: Scale with bounce effect
        self.play(text.animate.scale(2.2), run_time=0.3)
        self.play(text.animate.scale(0.91), run_time=0.2)  # 2.2 × 0.91 ≈ 2.0
        self.wait(0.5)

        # Step 4: Change color to red
        self.play(text.animate.set_color(RED), run_time=0.5)
        self.wait(1)
