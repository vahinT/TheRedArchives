import subprocess

# Write the manim animation code to a file
with open("subscribe_box.py", "w") as f:
    f.write("""
from manim import *

class SubscribeBox(Scene):
    def construct(self):
        # Step 1: Draw a red rounded rectangle outline
        box = RoundedRectangle(
            corner_radius=0.3,
            width=6,
            height=2,
            color=RED,
            stroke_width=6,
            fill_opacity=0
        )
        self.play(Create(box))
        self.wait(0.5)

        # Step 2: Outline the "subscribe" text
        text_outline = Text(
            "subscribe",
            font="Sans-Serif",
            color=RED,
            stroke_width=0,
            fill_opacity=0
        )
        text_outline.scale(1.5)
        text_outline.move_to(box.get_center())

        # Only outline
        text_outline.set_stroke(color=RED, width=2)
        self.play(Create(text_outline))
        self.wait(0.5)

        # Step 3: Fill the text in red
        text_filled = Text(
            "subscribe",
            font="Sans-Serif",
            color=RED
        )
        text_filled.scale(1.5)
        text_filled.move_to(box.get_center())

        self.play(Transform(text_outline, text_filled))
        self.wait(1)
""")

# Use subprocess to run manim
subprocess.run([
    "manim",
    "-pql",               # Low quality preview
    "subscribe_box.py",   # File name
    "SubscribeBox"        # Class name
])
