from manim import *

class SubscribeBox(Scene):
    def construct(self):
        custom_red = "#FF0033"  # Bright red color

        # Box
        box = RoundedRectangle(
            corner_radius=0.3,
            width=6,
            height=2,
            color=custom_red,
            stroke_width=6,
            fill_color=custom_red,
            fill_opacity=1
        )
        self.play(Create(box))
        self.wait(0.5)

        # "subscribe" outline text
        text_outline = Text(
            "subscribe",
            font="Sans-Serif",
            stroke_width=2,
            fill_opacity=0,
            stroke_color=WHITE,
        )
        text_outline.scale(1.5)
        text_outline.move_to(box.get_center())

        self.play(Create(text_outline))
        self.wait(0.5)

        # Fill in "subscribe" text
        text_filled = Text(
            "subscribe",
            font="Sans-Serif",
            color=WHITE,
        )
        text_filled.scale(1.75)
        text_filled.move_to(box.get_center())

        self.play(Transform(text_outline, text_filled))
        self.wait(0.5)

        # "to Vahin VVM!" outline (italic), placed further down
        subtitle_outline = Text(
            "to Vahin VVM!",
            font="Sans-Serif",
            slant=ITALIC,
            stroke_width=1.5,
            fill_opacity=0,
            stroke_color=WHITE,
        )
        subtitle_outline.scale(1)
        subtitle_outline.next_to(box, DOWN, buff=0.7)  # Lower position

        self.play(Create(subtitle_outline))
        self.wait(0.5)

        # Fill in subtitle
        subtitle_filled = Text(
            "to Vahin VVM!",
            font="Sans-Serif",
            slant=ITALIC,
            color=WHITE,
        )
        subtitle_filled.scale(2)
        subtitle_filled.move_to(subtitle_outline.get_center())

        self.play(Transform(subtitle_outline, subtitle_filled))
        self.wait(1)
