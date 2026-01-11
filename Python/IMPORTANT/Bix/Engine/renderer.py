import pygame
import math
from Engine.math3d import Vec3
from Engine.raycast import cast_ray


class Renderer:
    def __init__(self, engine):
        self.engine = engine

        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Bix Engine")

        self.width, self.height = self.screen.get_size()
        self.clock = pygame.time.Clock()

        # render settings
        self.fov = math.pi / 3  # 60 degrees
        self.bg_color = (25, 25, 25)

    def draw(self):
        self._handle_quit()
        self.screen.fill(self.bg_color)
        self._draw_world()
        pygame.display.flip()
        self.clock.tick(60)

    # -------------------------
    # INTERNALS
    # -------------------------
    def _draw_world(self):
        p = self.engine.world.player
        parts = self.engine.world.parts

        half_h = self.height // 2
        ray_count = self.width

        for x in range(ray_count):
            # calculate angle for this ray
            ray_angle = p.yaw - self.fov / 2 + (x / ray_count) * self.fov

            hit_part = None
            dist = cast_ray(p.pos, ray_angle, parts)

            # find the part that was hit
            hit_point = Vec3(
                p.pos.x + math.cos(ray_angle) * dist,
                p.pos.y,
                p.pos.z + math.sin(ray_angle) * dist
            )
            for part in parts:
                if part.collidable and part.intersects_point(hit_point):
                    hit_part = part
                    break

            # fish-eye correction
            dist *= math.cos(ray_angle - p.yaw)
            if dist <= 0:
                dist = 0.0001

            wall_height = int(self.height / dist)

            # pick color: part color or distance shade
            if hit_part:
                color = hit_part.color
            else:
                shade = max(40, 255 - int(dist * 25))
                color = (shade, shade, shade)

            y1 = half_h - wall_height // 2
            y2 = half_h + wall_height // 2

            pygame.draw.line(self.screen, color, (x, y1), (x, y2))

    def _handle_quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.engine.stop()
