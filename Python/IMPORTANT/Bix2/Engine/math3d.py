class Vec3:
    __slots__ = ("x", "y", "z")

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def copy(self):
        return Vec3(self.x, self.y, self.z)

    # basic ops (useful later)
    def __add__(self, other):
        return Vec3(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )

    def __sub__(self, other):
        return Vec3(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z
        )

    def __mul__(self, scalar):
        return Vec3(
            self.x * scalar,
            self.y * scalar,
            self.z * scalar
        )

    def __repr__(self):
        return f"Vec3({self.x}, {self.y}, {self.z})"
