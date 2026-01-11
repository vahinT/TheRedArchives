import math
from Engine.math3d import Vec3

def cast_ray(origin: Vec3, angle: float, parts, max_dist=20.0, step=0.05):
    x = origin.x
    z = origin.z

    dx = math.cos(angle) * step
    dz = math.sin(angle) * step

    dist = 0.0

    while dist < max_dist:
        x += dx
        z += dz
        dist += step

        probe = Vec3(x, origin.y, z)

        for part in parts:
            if not part.collidable:
                continue
            if part.intersects_point(probe):
                return dist

    return max_dist
