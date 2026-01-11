import math
from Engine.math3d import Vec3


def cast_ray(origin: Vec3, angle: float, parts, max_dist=15.0, step=0.5):
    ox = origin.x
    oz = origin.z
    oy = origin.y

    dx = math.cos(angle) * step
    dz = math.sin(angle) * step

    x = ox
    z = oz
    dist = 0.0

    while dist < max_dist:
        x += dx
        z += dz
        dist += step

        # manual probe (NO Vec3 creation)
        for part in parts:
            if not part.collidable:
                continue

            # quick AABB test inline (FAST)
            hx = part.size.x * 0.5
            hz = part.size.z * 0.5
            hy = part.size.y * 0.5

            if (
                part.pos.x - hx <= x <= part.pos.x + hx and
                part.pos.y - hy <= oy <= part.pos.y + hy and
                part.pos.z - hz <= z <= part.pos.z + hz
            ):
                return dist

    return max_dist
