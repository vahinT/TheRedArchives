from Engine.math3d import Vec3
from Engine.part import Part
import os
import sys

class Player:
    __slots__ = ("pos", "yaw", "speed", "rot_speed")

    def __init__(self):
        self.pos = Vec3(0, 2, 0)
        self.yaw = 0.0
        self.speed = 5.0
        self.rot_speed = 2.5


def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


# -------------------------
# SCRIPT API
# -------------------------

class ScriptPart:
    def __init__(self, engine, name):
        self._engine = engine
        self._part = Part(Vec3(0, 0, 0), Vec3(1, 1, 1), True)
        self._engine.world.add_part(self._part)

    @property
    def pos(self):
        return (self._part.pos.x, self._part.pos.y, self._part.pos.z)

    @pos.setter
    def pos(self, value):
        self._part.pos = Vec3(*value)

    @property
    def size(self):
        return (self._part.size.x, self._part.size.y, self._part.size.z)

    @size.setter
    def size(self, value):
        self._part.size = Vec3(*value)

    @property
    def CanCollide(self):
        return self._part.collidable

    @CanCollide.setter
    def CanCollide(self, value):
        self._part.collidable = bool(value)

    @property
    def Colour(self):
        return self._part.color

    @Colour.setter
    def Colour(self, hex_str):
        self._part.color = hex_to_rgb(hex_str)


class CreateAPI:
    def __init__(self, engine):
        self.engine = engine

    def part(self, name):
        return ScriptPart(self.engine, name)


class DebugAPI:
    def __init__(self, engine):
        self.engine = engine

    def parts(self):
        for i, part in enumerate(self.engine.world.parts):
            print(
                f"[{i}] pos={(part.pos.x, part.pos.y, part.pos.z)} "
                f"size={(part.size.x, part.size.y, part.size.z)} "
                f"collidable={part.collidable} color={part.color}"
            )


# -------------------------
# WORLD
# -------------------------

class World:
    def __init__(self):
        self.parts = []
        self.scripts = []
        self.player = Player()

    def add_part(self, part):
        self.parts.append(part)

    def add_script(self, code):
        self.scripts.append(code)

    def run_scripts(self, engine):
        engine_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if engine_root not in sys.path:
            sys.path.insert(0, engine_root)

        for code in self.scripts:
            env = {
                "__import__": __import__,
                "create": CreateAPI(engine),
                "debug": DebugAPI(engine),
                "print": print,
                "range": range,
                "len": len,
            }
            try:
                exec(code, env, env)
            except Exception as e:
                print("Script error:", e)


    def try_move_player(self, dx, dz):
        test = self.player.pos.copy()
        test.x += dx
        if not self._collides(test):
            self.player.pos.x = test.x

        test = self.player.pos.copy()
        test.z += dz
        if not self._collides(test):
            self.player.pos.z = test.z

    def _collides(self, pos):
        for part in self.parts:
            if part.collidable and part.intersects_point(pos):
                return True
        return False
