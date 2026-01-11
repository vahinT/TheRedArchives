from Engine.math3d import Vec3

class Part:
    __slots__ = ("pos", "size", "collidable", "color")

    def __init__(self, pos: Vec3, size: Vec3, collidable=True, color=(200, 200, 200)):
        self.pos = pos
        self.size = size
        self.collidable = collidable
        self.color = color  # new color attribute

    # Axis-Aligned Bounding Box (AABB) point test
    def intersects_point(self, p: Vec3) -> bool:
        return (
            self.pos.x <= p.x <= self.pos.x + self.size.x and
            self.pos.y <= p.y <= self.pos.y + self.size.y and
            self.pos.z <= p.z <= self.pos.z + self.size.z
        )

    def __repr__(self):
        return f"Part(pos={self.pos}, size={self.size}, collidable={self.collidable}, color={self.color})"
