import time
import os

from Engine.world import World
from Engine.input import InputState
from Engine.renderer import Renderer
from Engine.loader import load_workspace, load_scripts


class Engine:
    def __init__(self):
        self.running = False
        self.dt = 1 / 60

        # core systems
        self.world = World()
        self.input = InputState()
        self.renderer = Renderer(self)

        # paths
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

        # load data
        load_workspace(self, os.path.join(ROOT_DIR, "Workspace"))
        load_scripts(self.world, os.path.join(ROOT_DIR, "ScriptService"))

        # 🔥 RUN SCRIPTS ONCE
        self.world.run_scripts(self)

    def run(self):
        self.running = True
        last_time = time.time()

        while self.running:
            now = time.time()
            self.dt = now - last_time
            last_time = now

            self.input.update()
            if self.input.quit:
                self.stop()
                break

            self.update_player()
            self.renderer.draw()

    def stop(self):
        self.running = False

    def update_player(self):
        p = self.world.player
        p.yaw += self.input.turn * p.rot_speed * self.dt

        import math
        dx = math.cos(p.yaw) * self.input.forward * p.speed * self.dt
        dz = math.sin(p.yaw) * self.input.forward * p.speed * self.dt

        self.world.try_move_player(dx, dz)
