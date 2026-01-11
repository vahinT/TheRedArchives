from Engine.math3d import Vec3
from Engine.part import Part

# -------------------------
# PLAYER
# -------------------------
class Player:
    __slots__ = ("pos","yaw","speed","rot_speed")
    def __init__(self):
        self.pos = Vec3(0,1.6,0)
        self.yaw = 0.0
        self.speed = 5.0
        self.rot_speed = 2.5

# -------------------------
# UTILITY
# -------------------------
def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2],16) for i in (0,2,4))

# -------------------------
# SCRIPT API
# -------------------------
class ScriptPart:
    def __init__(self, engine, name):
        self._engine = engine
        self._name = name
        self._part = Part(Vec3(0,0,0), Vec3(1,1,1), True)
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
            print(f"[{i}] pos={part.pos.x,part.pos.y,part.pos.z}, size={part.size.x,part.size.y,part.size.z}, collidable={part.collidable}, color={part.color}")

    def player(self):
        p = self.engine.world.player
        print(f"Player pos={p.pos.x, p.pos.y, p.pos.z}, yaw={p.yaw}")

    def log(self, msg):
        print(f"[DEBUG] {msg}")

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

    def add_script(self, code: str):
        self.scripts.append(code)

    def run_scripts(self, engine):
        for code in self.scripts:
            env = {
                "create": CreateAPI(engine),
                "debug": DebugAPI(engine),
                "print": print,
                "range": range,
                "len": len
            }
            try:
                exec(code, {}, env)
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
            if not part.collidable:
                continue
            if part.intersects_point(pos):
                return True
        return False
