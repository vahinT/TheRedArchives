from Engine.math3d import Vec3

class Part:
    __slots__ = ("pos", "size", "collidable", "color")

    def __init__(self, pos: Vec3, size: Vec3, collidable=True, color=(200, 200, 200)):
        self.pos = pos
        self.size = size
        self.collidable = collidable
        self.color = color  # new color attribute

    # Axis-Aligned Bounding Box (AABB) point test
    def intersects_point(self, p):
        hx = self.size.x / 2
        hy = self.size.y / 2
        hz = self.size.z / 2

        return (
            self.pos.x - hx <= p.x <= self.pos.x + hx and
            self.pos.y - hy <= p.y <= self.pos.y + hy and
            self.pos.z - hz <= p.z <= self.pos.z + hz
        )


    def __repr__(self):
        return f"Part(pos={self.pos}, size={self.size}, collidable={self.collidable}, color={self.color})"
