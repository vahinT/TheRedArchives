import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Add the ball (UV Sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
sphere = bpy.context.object
sphere.name = "Ball"

# Add the cloth (Plane)
bpy.ops.mesh.primitive_plane_add(size=3, location=(0, 0, 5))
cloth = bpy.context.object
cloth.name = "Cloth"

# Subdivide the plane for initial cloth mesh resolution
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=1)
bpy.ops.object.mode_set(mode='OBJECT')

# Add Subdivision Surface modifier to the cloth
subsurf = cloth.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 2

# Add Cloth physics to the cloth object
bpy.ops.object.modifier_add(type='CLOTH')
cloth_physics = cloth.modifiers["Cloth"]
cloth_physics.settings.quality = 5
cloth_physics.settings.mass = 0.3
cloth_physics.settings.air_damping = 1.0
cloth_physics.settings.bending_model = 'ANGULAR'
cloth_physics.settings.use_pressure = False

# Add collision to the ball
bpy.ops.object.modifier_add(type='COLLISION')
sphere_collision = sphere.modifiers["Collision"]
sphere_collision.settings.thickness_outer = 0.1

# Set up the scene
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 100
bpy.context.scene.render.fps = 30

# Keyframe the subdivision modifier
subsurf.keyframe_insert(data_path="levels", frame=1)
subsurf.levels = 4  # Increase subdivision
subsurf.keyframe_insert(data_path="levels", frame=20)
subsurf.levels = 8  # Increase subdivision
subsurf.keyframe_insert(data_path="levels", frame=40)
subsurf.levels = 16  # Increase subdivision
subsurf.keyframe_insert(data_path="levels", frame=60)
subsurf.levels = 32  # Increase subdivision
subsurf.keyframe_insert(data_path="levels", frame=80)
subsurf.levels = 64  # Increase subdivision
subsurf.keyframe_insert(data_path="levels", frame=100)

# Set gravity
bpy.context.scene.gravity = (0, 0, -9.81)

# Set the output format and path
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.render.filepath = "/desktop/cloth_simulation.mp4"

# Run the animation
bpy.ops.render.render(animation=True)
