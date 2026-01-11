import os
import random

# Path to your Workspace folder
workspace_path = os.path.join(os.path.dirname(__file__), "Workspace")
os.makedirs(workspace_path, exist_ok=True)

# Maze configuration
maze_width = 10
maze_height = 10
cell_size = 5

# Part template
part_template = """pos:{x},{y},{z}
size:{sx},{sy},{sz}
collidable:true
"""

# Simple maze generation using randomized DFS
def generate_maze(width, height):
    maze = [[1 for _ in range(width)] for _ in range(height)]
    stack = [(0, 0)]
    visited = {(0, 0)}

    while stack:
        x, y = stack[-1]
        maze[y][x] = 0  # mark path

        # get unvisited neighbors
        neighbors = []
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                neighbors.append((nx, ny))

        if neighbors:
            nx, ny = random.choice(neighbors)
            visited.add((nx, ny))
            stack.append((nx, ny))
        else:
            stack.pop()

    return maze

# Convert maze cells to parts
def create_maze_parts(maze):
    part_count = 0
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == 1:  # wall
                part_count += 1
                part_name = f"part_{part_count}.part"
                part_path = os.path.join(workspace_path, part_name)
                pos_x = x * cell_size
                pos_y = 0
                pos_z = y * cell_size
                size_x = cell_size
                size_y = 3
                size_z = cell_size

                with open(part_path, "w") as f:
                    f.write(part_template.format(
                        x=pos_x, y=pos_y, z=pos_z,
                        sx=size_x, sy=size_y, sz=size_z
                    ))

# Main
maze = generate_maze(maze_width, maze_height)
create_maze_parts(maze)

print(f"Maze generated with {maze_width*maze_height} cells and parts created in {workspace_path}")
