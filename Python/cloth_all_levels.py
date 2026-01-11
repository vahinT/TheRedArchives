import bpy

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_sphere():
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(0, 0, 0))
    sphere = bpy.context.object
    sphere.name = "RedSphere"

    mat = bpy.data.materials.new(name="RedMat")
    mat.diffuse_color = (1.0, 0.0, 0.0, 1.0)
    sphere.data.materials.append(mat)

    bpy.ops.object.modifier_add(type='COLLISION')

def create_cloth(subdivisions):
    # Create a plane mesh from scratch
    bpy.ops.mesh.primitive_plane_add(size=5, location=(0, 0, 5))
    cloth = bpy.context.object
    cloth.name = f"Cloth_{subdivisions}x{subdivisions}"

    # Enter edit mode and subdivide the plane
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=subdivisions)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Ensure the cloth is at the correct position after subdivision
    cloth.location = (0, 0, 5)
    cloth.rotation_euler = (0, 0, 0)
    cloth.scale = (1, 1, 1)

    # Add yellow material
    mat = bpy.data.materials.get("YellowMat")
    if not mat:
        mat = bpy.data.materials.new(name="YellowMat")
        mat.diffuse_color = (1.0, 1.0, 0.0, 1.0)
    cloth.data.materials.append(mat)

    # Add cloth physics
    bpy.ops.object.modifier_add(type='CLOTH')
    cloth.modifiers["Cloth"].settings.gravity[2] = -10.0

def setup_scene():
    # Camera
    bpy.ops.object.camera_add(location=(10, -10, 8), rotation=(1.1, 0, 0.9))
    cam = bpy.context.object
    bpy.context.scene.camera = cam

    # Light
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))

def render_range(start_frame, end_frame):
    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame

def bake_cloth():
    bpy.ops.ptcache.bake_all(bake=True)

def simulate_and_append(subdivisions, start_frame):
    end_frame = start_frame + 149  # 50 frames
    render_range(start_frame, end_frame)

    # Clean and set up
    clear_scene()
    create_sphere()
    create_cloth(subdivisions)
    setup_scene()

    # Bake cloth and leave baked frames in the timeline
    bake_cloth()

    # Render animation
    bpy.context.scene.render.filepath = f"//cloth_fall_temp_{subdivisions}f_"
    bpy.ops.render.render(animation=True)

    return end_frame + 1

# Set render settings for MP4 output
scene = bpy.context.scene
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'HIGH'
scene.render.fps = 30
scene.render.resolution_x = 640
scene.render.resolution_y = 640

# Master output
scene.render.filepath = "//cloth_fall_all.mp4"

# Simulate cloth for each level and append to single timeline
current_frame = 1
for power in range(1, 13):  # 2^1 = 2, ..., 2^12 = 4096
    cuts = 2**power
    print(f"Simulating {cuts}x{cuts} cloth...")  # will show up in terminal
    current_frame = simulate_and_append(cuts, current_frame)

# Set total frame range to match the combined video
scene.frame_start = 1
scene.frame_end = current_frame - 1

# Re-render all combined as a single MP4
scene.render.filepath = "//cloth_fall_all.mp4"
bpy.ops.render.render(animation=True)
