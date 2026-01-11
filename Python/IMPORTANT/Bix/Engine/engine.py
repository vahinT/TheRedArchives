import time
import os

from Engine.world import World
from Engine.input import InputState
from Engine.renderer import Renderer
from Engine.loader import load_workspace, load_scripts
from Engine.world import World, CreateAPI, DebugAPI



class Engine:
    def __init__(self):
        self.running = False
        self.dt = 1 / 60

        # core systems
        self.world = World()
        self.input = InputState()
        self.renderer = Renderer(self)

        # project root
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

        # load data-driven content
        load_workspace(self, os.path.join(ROOT_DIR, "Workspace"))
        load_scripts(self.world, os.path.join(ROOT_DIR, "ScriptService"))

        # ✅ run scripts ONCE at init
        self.world.run_scripts(self)

    def run(self):
        self.running = True
        last_time = time.time()

        while self.running:
            now = time.time()
            self.dt = now - last_time
            last_time = now

            # 1. input
            self.input.update()
            if self.input.quit:
                self.stop()
                break

            # 2. update player/world
            self.update_player()

            # ❌ no scripts here

            # 3. render
            self.renderer.draw()

    def stop(self):
        self.running = False

    # -------------------------
    # PLAYER UPDATE
    # -------------------------
    def update_player(self):
        p = self.world.player

        # rotation
        p.yaw += self.input.turn * p.rot_speed * self.dt

        # movement (FPS style)
        import math
        dx = math.cos(p.yaw) * self.input.forward * p.speed * self.dt
        dz = math.sin(p.yaw) * self.input.forward * p.speed * self.dt

        self.world.try_move_player(dx, dz)
