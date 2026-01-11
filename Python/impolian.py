from manim import *

class MinecraftLogoDraw(Scene):
    def construct(self):
        # Load the Minecraft-like text (you can use a pixel font if available)
        logo = Text("MINECRAFT", font="Minecraftia")  # Replace with a pixel/blocky font
        logo.set_color(GRAY)
        logo.scale(1.5)

        self.play(Write(logo, run_time=3))
        self.wait(2)

