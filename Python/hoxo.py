import numpy as np
import matplotlib.pyplot as plt
import moviepy.editor as mpy
from matplotlib import cm

# Constants
g = -10  # gravity
cloth_sizes = [2**i for i in range(1, 7)]  # 2x2 to 64x64
frame_count = 60
dt = 0.033  # seconds per frame

def simulate_cloth(n):
    pos = np.zeros((n, n, 3))
    vel = np.zeros((n, n, 3))
    
    # Init cloth positions (flat plane above the sphere)
    for i in range(n):
        for j in range(n):
            pos[i, j] = np.array([i - n//2, 5, j - n//2])

    sphere_center = np.array([0, 0, 0])
    sphere_radius = 2

    frames = []
    for f in range(frame_count):
        vel[:, :, 1] += g * dt  # Apply gravity
        pos += vel * dt         # Update positions

        # Simple collision with sphere
        for i in range(n):
            for j in range(n):
                p = pos[i, j]
                dir_vec = p - sphere_center
                dist = np.linalg.norm(dir_vec)
                if dist < sphere_radius:
                    norm = dir_vec / dist
                    pos[i, j] = sphere_center + norm * sphere_radius
                    vel[i, j] = np.zeros(3)

        # Plot
        fig = plt.figure(figsize=(5, 5))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlim(-n//2, n//2)
        ax.set_ylim(-n//2, n//2)
        ax.set_zlim(-2, 10)
        ax.axis('off')

        ax.plot_surface(
            pos[:, :, 0], pos[:, :, 2], pos[:, :, 1],
            rstride=1, cstride=1, color='yellow', edgecolor='black', linewidth=0.1
        )

        # Plot red sphere
        u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        x = sphere_radius * np.cos(u) * np.sin(v)
        y = sphere_radius * np.sin(u) * np.sin(v)
        z = sphere_radius * np.cos(v)
        ax.plot_surface(x, z, y, color='red')

        fname = f"frame_{f}.png"
        plt.savefig(fname, bbox_inches='tight')
        frames.append(fname)
        plt.close()

    return frames

# Run simulation for a single cloth size (example: 32x32)
frames = simulate_cloth(32)

# Convert to mp4
clip = mpy.ImageSequenceClip(frames, fps=30)
clip.write_videofile("cloth_fall.mp4", codec='libx264')

# Optional: Cleanup PNGs
import os
for f in frames:
    os.remove(f)
