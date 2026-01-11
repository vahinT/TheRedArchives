import bpy
import os
import math

# ⚠️ CHANGE THIS PATH to your actual output folder
output_path = "C:/your/output/folder"

# Ensure output folder exists
if not os.path.exists(output_path):
    os.makedirs(output_path)

# Rendering setup
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 90  # Shorter duration = faster
scene.render.fps = 30
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'

# Use Cycles GPU
scene.render.engine = 'CYCLES'
bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"  # Or "OPTIX" / "HIP"
scene.cycles.device = 'GPU'

# Helper: Create material
def create_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    return mat

# Helper: Camera & Light
def setup_camera_light():
    bpy.ops.object.camera_add(location=(0, -5, 2), rotation=(math.radians(75), 0, 0))
    cam = bpy.context.object
    scene.camera = cam
    bpy.ops.object.light_add(type='AREA', location=(0, -2, 5))
    light = bpy.context.object
    light.data.energy = 1000

# Create cloth
def create_cloth():
    bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 3))
    cloth = bpy.context.object
    cloth.name = "Cloth"
    cloth.location = (0, 0, 3)
    cloth.rotation_euler = (0, 0, 0)

    bpy.ops.object.shade_smooth()
    sub = cloth.modifiers.new("Subdivision", 'SUBSURF')
    sub.levels = 2
    sub.render_levels = 2

    cloth_mod = cloth.modifiers.new("Cloth", 'CLOTH')
    cloth_mod.settings.quality = 3
    cloth_mod.settings.mass = 0.3
    cloth_mod.settings.air_damping = 1
    cloth_mod.collision_settings.use_self_collision = True

    yellow = create_material("Yellow", (1, 1, 0, 1))
    cloth.data.materials.append(yellow)

    return cloth

# Create low-poly collision sphere
def create_low_poly_sphere():
    bpy.ops.mesh.primitive_uv_sphere_add(location=(0, 0, 0), segments=16, ring_count=8)
    sphere = bpy.context.object
    sphere.name = "Sphere"
    bpy.ops.object.shade_smooth()
    sphere.modifiers.new("Collision", 'COLLISION')
    return sphere

# Swap in high-subdiv render-only sphere
def create_high_subdiv_sphere(subdiv_level):
    bpy.ops.mesh.primitive_uv_sphere_add(location=(0, 0, 0))
    sphere = bpy.context.object
    sphere.name = "RenderSphere"
    bpy.ops.object.shade_smooth()
    mod = sphere.modifiers.new("Subdivision", 'SUBSURF')
    levels = int(math.log2(subdiv_level)) if subdiv_level > 1 else 0
    mod.levels = levels
    mod.render_levels = levels
    red = create_material("Red", (1, 0, 0, 1))
    sphere.data.materials.append(red)
    return sphere

# Bake & render loop
for subdiv in [2**i for i in range(0, 12)]:  # 1 to 2048
    print(f"\n🔄 Subdivision: {subdiv}")

    # Clean scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Setup scene
    setup_camera_light()
    cloth = create_cloth()
    collision_sphere = create_low_poly_sphere()

    # Bake simulation
    bpy.context.view_layer.objects.active = cloth
    bpy.ops.ptcache.free_bake_all()
    bpy.ops.ptcache.bake_all(bake=True)

    # Delete low-poly sphere, insert high-res version
    bpy.data.objects.remove(collision_sphere, do_unlink=True)
    create_high_subdiv_sphere(subdiv)

    # Render animation
    scene.render.filepath = os.path.join(output_path, f"cloth_subdiv_{subdiv}.mp4")
    bpy.ops.render.render(animation=True)

    # Free cache
    bpy.ops.ptcache.free_bake_all()

print("✅ All simulations and renders complete!")
