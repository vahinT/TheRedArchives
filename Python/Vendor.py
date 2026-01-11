import sys
import taichi as ti
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QSlider, QSpinBox, QGroupBox, QFormLayout, QFileDialog
from PyQt5.QtWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import imageio
import os
import tempfile

# Taichi setup for simulation
ti.init(arch=ti.gpu)

# Cloth simulation parameters
n = 128  # Reduced grid size for better performance
mass = 0.1
# Position, velocity and force for cloth particles
cloth_pos = ti.Vector.field(3, dtype=ti.f32, shape=(n, n))
cloth_vel = ti.Vector.field(3, dtype=ti.f32, shape=(n, n))
cloth_force = ti.Vector.field(3, dtype=ti.f32, shape=(n, n))
gravity_base = ti.Vector([0.0, -9.8, 0.0])
gravity_speed = 1.0  # Gravity speed multiplier

# Cloth position offset for moving cloth
cloth_position_offset = np.array([0.0, 0.0, 0.0], dtype=np.float32)

# Spheres parameters
max_spheres = 1024
sphere_radius = 0.1
spheres = ti.Vector.field(3, dtype=ti.f32, shape=max_spheres)
sphere_velocities = ti.Vector.field(3, dtype=ti.f32, shape=max_spheres)
current_num_spheres = 0

# Liquid simulation parameters
max_particles = 4096
liquid_particles = ti.Vector.field(3, dtype=ti.f32, shape=max_particles)
liquid_velocities = ti.Vector.field(3, dtype=ti.f32, shape=max_particles)
current_num_particles = 0
liquid_viscosity = 0.1  # default viscosity

# Cloth simulation spring parameters
spring_constant = 100.0
rest_length = 0.1
cloth_active = False

@ti.kernel
def initialize_cloth():
    for i, j in ti.ndrange(n, n):
        scale = 0.5  # scale down the cloth size
        x = ((i / (n - 1)) * 2 - 1) * scale
        z = ((j / (n - 1)) * 2 - 1) * scale
        y = 0.5 * scale
        cloth_pos[i, j] = ti.Vector([x, y, z])
        cloth_vel[i, j] = ti.Vector([0.0, 0.0, 0.0])
        cloth_force[i, j] = ti.Vector([0.0, 0.0, 0.0])

@ti.kernel
def initialize_sphere(index: ti.i32, pos: ti.types.vector(3, ti.f32)):
    spheres[index] = pos
    sphere_velocities[index] = ti.Vector([0.0, 0.0, 0.0])

@ti.kernel
def initialize_liquid_particle(index: ti.i32, pos: ti.types.vector(3, ti.f32)):
    liquid_particles[index] = pos
    liquid_velocities[index] = ti.Vector([0.0, 0.0, 0.0])

@ti.kernel
def compute_cloth_forces():
    for i, j in cloth_force:
        cloth_force[i, j] = mass * gravity_base * gravity_speed

    for i, j in ti.ndrange(n, n):
        if i < n - 1:
            diff = cloth_pos[i+1, j] - cloth_pos[i, j]
            dist = diff.norm()
            if dist > 1e-5:
                # Use local variable to avoid repeated division
                inv_dist = 1.0 / dist
                force = spring_constant * (dist - rest_length) * diff * inv_dist
                cloth_force[i, j] += force
                cloth_force[i+1, j] -= force

        if j < n - 1:
            diff = cloth_pos[i, j+1] - cloth_pos[i, j]
            dist = diff.norm()
            if dist > 1e-5:
                inv_dist = 1.0 / dist
                force = spring_constant * (dist - rest_length) * diff * inv_dist
                cloth_force[i, j] += force
                cloth_force[i, j+1] -= force

        if i < n - 1 and j < n - 1:
            diff = cloth_pos[i+1, j+1] - cloth_pos[i, j]
            dist = diff.norm()
            if dist > 1e-5:
                inv_dist = 1.0 / dist
                force = spring_constant * 0.7 * (dist - rest_length * 1.414) * diff * inv_dist
                cloth_force[i, j] += force
                cloth_force[i+1, j+1] -= force

@ti.kernel
def simulate_cloth(dt: ti.f32):
    if ti.static(not cloth_active):
        return
    cloth_vel[0, 0] = ti.Vector([0.0, 0.0, 0.0])
    cloth_vel[0, n-1] = ti.Vector([0.0, 0.0, 0.0])
    cloth_vel[n-1, 0] = ti.Vector([0.0, 0.0, 0.0])
    cloth_vel[n-1, n-1] = ti.Vector([0.0, 0.0, 0.0])

    for i, j in ti.ndrange(n, n):
        if (i == 0 and j == 0) or (i == 0 and j == n-1) or (i == n-1 and j == 0) or (i == n-1 and j == n-1):
            continue
        cloth_vel[i, j] += cloth_force[i, j] / mass * dt
        cloth_vel[i, j] *= 0.99
        cloth_pos[i, j] += cloth_vel[i, j] * dt

        for s in range(current_num_spheres):
            sphere_center = spheres[s]
            diff = cloth_pos[i, j] - sphere_center
            dist = diff.norm()
            if dist < sphere_radius + 0.02:
                if dist > 1e-5:
                    normal = diff / dist
                    cloth_pos[i, j] = sphere_center + normal * (sphere_radius + 0.02)
                    normal_vel = cloth_vel[i, j].dot(normal)
                    if normal_vel < 0:
                        cloth_vel[i, j] -= (1.0 + 0.5) * normal_vel * normal

@ti.kernel
def simulate_spheres(dt: ti.f32):
    for i in range(current_num_spheres):
        sphere_velocities[i] += gravity_base * gravity_speed * dt
        spheres[i] += sphere_velocities[i] * dt

        if spheres[i][1] - sphere_radius < -1.0:
            spheres[i][1] = -1.0 + sphere_radius
            sphere_velocities[i][1] *= -0.8
            sphere_velocities[i][0] *= 0.95
            sphere_velocities[i][2] *= 0.95

        if spheres[i][0] - sphere_radius < -1.0:
            spheres[i][0] = -1.0 + sphere_radius
            sphere_velocities[i][0] *= -0.8
        elif spheres[i][0] + sphere_radius > 1.0:
            spheres[i][0] = 1.0 - sphere_radius
            sphere_velocities[i][0] *= -0.8

        if spheres[i][2] - sphere_radius < -1.0:
            spheres[i][2] = -1.0 + sphere_radius
            sphere_velocities[i][2] *= -0.8
        elif spheres[i][2] + sphere_radius > 1.0:
            spheres[i][2] = 1.0 - sphere_radius
            sphere_velocities[i][2] *= -0.8

@ti.kernel
def simulate_liquid(dt: ti.f32):
    for i in range(current_num_particles):
        liquid_velocities[i] += gravity_base * gravity_speed * dt
        liquid_velocities[i] *= (1.0 - liquid_viscosity)
        liquid_particles[i] += liquid_velocities[i] * dt

        if liquid_particles[i][1] < -1.0:
            liquid_particles[i][1] = -1.0
            # Removed ti.random() calls here to avoid error
            # Use numpy random in Python code instead

        for d in ti.static(range(3)):
            if liquid_particles[i][d] < -1.0:
                liquid_particles[i][d] = -1.0
            elif liquid_particles[i][d] > 1.0:
                liquid_particles[i][d] = 1.0

class GLViewportWidget(QOpenGLWidget):
    def __init__(self):
        super(GLViewportWidget, self).__init__()
        self.setWindowTitle('3D Physics Simulation')
        self.setGeometry(100, 100, 800, 600)
        self.setFormat(QSurfaceFormat.defaultFormat())
        self.quadric = None

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        self.quadric = gluNewQuadric()
        gluQuadricNormals(self.quadric, GLU_SMOOTH)

        # Setup lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION,  (0, 5, 5, 1))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.7, 0.7, 0.7, 1.0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
        glMateriali(GL_FRONT_AND_BACK, GL_SHININESS, 50)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h if h != 0 else 1.0, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5)

        if cloth_active:
            glPushMatrix()
            glTranslatef(cloth_position_offset[0], cloth_position_offset[1], cloth_position_offset[2])
            self.draw_cloth()
            glPopMatrix()
        if current_num_spheres > 0:
            self.draw_spheres()
        if current_num_particles > 0:
            self.draw_liquid()

    def draw_cloth(self):
        # Cache numpy array to avoid repeated conversion
        if not hasattr(self, '_cloth_np_cache') or self._cloth_np_cache.shape[0] != n:
            self._cloth_np_cache = cloth_pos.to_numpy()
        cloth_np = self._cloth_np_cache

        glColor3f(0.0, 1.0, 0.0)
        for i in range(n):
            for j in range(n):
                pos = cloth_np[i, j]
                glPushMatrix()
                glTranslatef(pos[0], pos[1], pos[2])
                gluSphere(self.quadric, 0.02, 8, 8)
                glPopMatrix()

        glColor3f(0.5, 0.8, 0.5)
        glBegin(GL_LINES)
        for i in range(n):
            for j in range(n):
                pos = cloth_np[i, j]
                if i < n - 1:
                    pos2 = cloth_np[i + 1, j]
                    glVertex3f(pos[0], pos[1], pos[2])
                    glVertex3f(pos2[0], pos2[1], pos2[2])
                if j < n - 1:
                    pos2 = cloth_np[i, j + 1]
                    glVertex3f(pos[0], pos[1], pos[2])
                    glVertex3f(pos2[0], pos2[1], pos2[2])
        glEnd()

    def draw_spheres(self):
        spheres_np = spheres.to_numpy()
        for i in range(current_num_spheres):
            pos = spheres_np[i]
            r = 0.8 + (i % 3) * 0.2
            g = 0.2 + (i % 5) * 0.15
            b = 0.2 + (i % 7) * 0.1
            glColor3f(r, g, b)
            glPushMatrix()
            glTranslatef(pos[0], pos[1], pos[2])
            gluSphere(self.quadric, sphere_radius, 16, 16)
            glPopMatrix()

    def draw_liquid(self):
        liquid_np = liquid_particles.to_numpy()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.2, 0.4, 0.8, 0.6)
        for i in range(current_num_particles):
            pos = liquid_np[i]
            glPushMatrix()
            glTranslatef(pos[0], pos[1], pos[2])
            gluSphere(self.quadric, 0.02, 8, 8)
            glPopMatrix()
        glDisable(GL_BLEND)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('3D Physics Simulation with PyQt5 and Taichi')
        self.setGeometry(100, 100, 1000, 600)

        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.gl_widget = GLViewportWidget()
        main_layout.addWidget(self.gl_widget, 4)

        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(300)
        sidebar_layout = QVBoxLayout()
        self.sidebar.setLayout(sidebar_layout)
        main_layout.addWidget(self.sidebar, 1)

        self.btn_add_sphere = QPushButton("Add Sphere")
        self.btn_add_sphere.clicked.connect(self.add_sphere)
        sidebar_layout.addWidget(self.btn_add_sphere)

        self.btn_add_cloth = QPushButton("Add Cloth")
        self.btn_add_cloth.clicked.connect(self.add_cloth)
        sidebar_layout.addWidget(self.btn_add_cloth)

        self.btn_add_liquid = QPushButton("Add Liquid")
        self.btn_add_liquid.clicked.connect(self.add_liquid)
        sidebar_layout.addWidget(self.btn_add_liquid)

        # New button to render and save MP4
        self.btn_render_mp4 = QPushButton("Render and Save MP4")
        self.btn_render_mp4.clicked.connect(self.render_and_save_mp4)
        sidebar_layout.addWidget(self.btn_render_mp4)

        # New buttons for subdividing cloth and liquid
        self.btn_subdivide_cloth = QPushButton("Subdivide Cloth")
        self.btn_subdivide_cloth.clicked.connect(self.subdivide_cloth)
        sidebar_layout.addWidget(self.btn_subdivide_cloth)

        self.btn_add_more_liquid = QPushButton("Add More Liquid Particles")
        self.btn_add_more_liquid.clicked.connect(self.add_more_liquid_particles)
        sidebar_layout.addWidget(self.btn_add_more_liquid)

        params_group = QGroupBox("Simulation Parameters")
        params_layout = QFormLayout()
        params_group.setLayout(params_layout)
        sidebar_layout.addWidget(params_group)

        self.viscosity_slider = QSlider(Qt.Horizontal)
        self.viscosity_slider.setMinimum(0)
        self.viscosity_slider.setMaximum(100)
        self.viscosity_slider.setValue(int(liquid_viscosity * 100))
        self.viscosity_slider.valueChanged.connect(self.change_viscosity)
        params_layout.addRow(QLabel("Liquid Viscosity"), self.viscosity_slider)

        self.gravity_slider = QSlider(Qt.Horizontal)
        self.gravity_slider.setMinimum(0)
        self.gravity_slider.setMaximum(200)
        self.gravity_slider.setValue(int(gravity_speed * 100))
        self.gravity_slider.valueChanged.connect(self.change_gravity_speed)
        params_layout.addRow(QLabel("Gravity Speed"), self.gravity_slider)

        pos_group = QGroupBox("Position Controls (Last Selected Object)")
        pos_layout = QFormLayout()
        pos_group.setLayout(pos_layout)
        sidebar_layout.addWidget(pos_group)

        # Add combo box to select object type (sphere or liquid or cloth)
        from PyQt5.QtWidgets import QComboBox
        self.object_type_combo = QComboBox()
        self.object_type_combo.addItems(["Sphere", "Liquid", "Cloth"])
        self.object_type_combo.currentIndexChanged.connect(self.object_type_changed)
        pos_layout.addRow(QLabel("Object Type"), self.object_type_combo)

        # Add spin box to select object index (only for sphere and liquid)
        self.object_index_spin = QSpinBox()
        self.object_index_spin.setRange(0, 0)
        self.object_index_spin.valueChanged.connect(self.object_index_changed)
        pos_layout.addRow(QLabel("Object Index"), self.object_index_spin)

        self.pos_x_spin = QSpinBox()
        self.pos_x_spin.setRange(-100, 100)
        self.pos_x_spin.setValue(0)
        self.pos_x_spin.valueChanged.connect(self.change_position)
        pos_layout.addRow(QLabel("X"), self.pos_x_spin)

        self.pos_y_spin = QSpinBox()
        self.pos_y_spin.setRange(-100, 100)
        self.pos_y_spin.setValue(0)
        self.pos_y_spin.valueChanged.connect(self.change_position)
        pos_layout.addRow(QLabel("Y"), self.pos_y_spin)

        self.pos_z_spin = QSpinBox()
        self.pos_z_spin.setRange(-100, 100)
        self.pos_z_spin.setValue(0)
        self.pos_z_spin.valueChanged.connect(self.change_position)
        pos_layout.addRow(QLabel("Z"), self.pos_z_spin)

        sidebar_layout.addStretch()

        self.last_selected_type = "Sphere"
        self.last_selected_index = 0

        self.timer = self.startTimer(16)

        # For MP4 rendering
        self.recording = False
        self.frames = []
        self.record_frame_count = 0
        self.max_record_frames = 300  # e.g., 5 seconds at 60 FPS

    def add_sphere(self):
        global current_num_spheres
        if current_num_spheres >= max_spheres:
            return
        pos = np.array([0.0, 0.5, 0.0], dtype=np.float32)
        initialize_sphere(current_num_spheres, ti.Vector(pos))
        current_num_spheres += 1
        self.last_selected_type = "Sphere"
        self.last_selected_index = current_num_spheres - 1
        self.update_position_controls(pos)
        self.update_object_index_range()

    def add_cloth(self):
        global cloth_active
        if cloth_active:
            return
        initialize_cloth()
        cloth_active = True
        # Reset cloth position offset when adding cloth
        global cloth_position_offset
        cloth_position_offset = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        if self.object_type_combo.currentText() == "Cloth":
            self.update_position_controls_for_selected()

    def add_liquid(self):
        global current_num_particles
        if current_num_particles + 100 > max_particles:
            return
        base_y = 1.0
        for i in range(100):
            pos = np.array([
                (np.random.rand() - 0.5) * 0.5,
                base_y + (np.random.rand() * 0.5),
                (np.random.rand() - 0.5) * 0.5
            ], dtype=np.float32)
            initialize_liquid_particle(current_num_particles, ti.Vector(pos))
            current_num_particles += 1
        self.last_selected_type = "Liquid"
        self.last_selected_index = current_num_particles - 1
        self.update_position_controls(liquid_particles[self.last_selected_index].to_numpy())
        self.update_object_index_range()

    def change_position(self):
        x = self.pos_x_spin.value() / 100.0
        y = self.pos_y_spin.value() / 100.0
        z = self.pos_z_spin.value() / 100.0
        pos = ti.Vector([x, y, z])
        if self.last_selected_type == "Sphere":
            if 0 <= self.last_selected_index < current_num_spheres:
                spheres[self.last_selected_index] = pos
                sphere_velocities[self.last_selected_index] = ti.Vector([0.0, 0.0, 0.0])
        elif self.last_selected_type == "Liquid":
            if 0 <= self.last_selected_index < current_num_particles:
                liquid_particles[self.last_selected_index] = pos
                liquid_velocities[self.last_selected_index] = ti.Vector([0.0, 0.0, 0.0])
        elif self.last_selected_type == "Cloth":
            global cloth_position_offset
            cloth_position_offset = np.array([x, y, z], dtype=np.float32)
            # No need to update cloth_pos field, just offset in drawing

    def update_position_controls_for_selected(self):
        if self.last_selected_type == "Sphere" and current_num_spheres > 0:
            pos = spheres[self.last_selected_index].to_numpy()
            self.object_index_spin.setEnabled(True)
        elif self.last_selected_type == "Liquid" and current_num_particles > 0:
            pos = liquid_particles[self.last_selected_index].to_numpy()
            self.object_index_spin.setEnabled(True)
        elif self.last_selected_type == "Cloth":
            pos = cloth_position_offset
            self.object_index_spin.setEnabled(False)
        else:
            pos = np.array([0.0, 0.0, 0.0])
            self.object_index_spin.setEnabled(False)
        self.update_position_controls(pos)

    def object_type_changed(self, index):
        self.last_selected_type = self.object_type_combo.currentText()
        self.update_object_index_range()
        self.update_position_controls_for_selected()

    def object_index_changed(self, index):
        self.last_selected_index = index
        self.update_position_controls_for_selected()

    def add_cloth(self):
        global cloth_active
        if cloth_active:
            return
        initialize_cloth()
        cloth_active = True

    def add_liquid(self):
        global current_num_particles
        if current_num_particles + 100 > max_particles:
            return
        base_y = 1.0
        for i in range(100):
            pos = np.array([
                (np.random.rand() - 0.5) * 0.5,
                base_y + (np.random.rand() * 0.5),
                (np.random.rand() - 0.5) * 0.5
            ], dtype=np.float32)
            initialize_liquid_particle(current_num_particles, ti.Vector(pos))
            current_num_particles += 1
        self.last_selected_type = "Liquid"
        self.last_selected_index = current_num_particles - 1
        self.update_position_controls(liquid_particles[self.last_selected_index].to_numpy())
        self.update_object_index_range()

    def add_more_liquid_particles(self):
        global current_num_particles
        add_count = 100
        if current_num_particles + add_count > max_particles:
            add_count = max_particles - current_num_particles
        base_y = 1.0
        for i in range(add_count):
            pos = np.array([
                (np.random.rand() - 0.5) * 0.5,
                base_y + (np.random.rand() * 0.5),
                (np.random.rand() - 0.5) * 0.5
            ], dtype=np.float32)
            initialize_liquid_particle(current_num_particles, ti.Vector(pos))
            current_num_particles += 1
        self.update_object_index_range()

    def subdivide_cloth(self):
        global n, cloth_pos, cloth_vel, cloth_force
        if cloth_active:
            # Increase resolution by doubling n (up to a max)
            max_n = 256
            if n >= max_n:
                return
            n = min(n * 2, max_n)
            cloth_pos = ti.Vector.field(3, dtype=ti.f32, shape=(n, n))
            cloth_vel = ti.Vector.field(3, dtype=ti.f32, shape=(n, n))
            cloth_force = ti.Vector.field(3, dtype=ti.f32, shape=(n, n))
            initialize_cloth()

    def change_viscosity(self, value):
        global liquid_viscosity
        liquid_viscosity = value / 100.0

    def change_gravity_speed(self, value):
        global gravity_speed
        gravity_speed = value / 100.0

    def object_type_changed(self, index):
        self.last_selected_type = self.object_type_combo.currentText()
        self.update_object_index_range()
        self.update_position_controls_for_selected()

    def object_index_changed(self, index):
        self.last_selected_index = index
        self.update_position_controls_for_selected()

    def update_object_index_range(self):
        if self.last_selected_type == "Sphere":
            max_index = max(0, current_num_spheres - 1)
        else:
            max_index = max(0, current_num_particles - 1)
        self.object_index_spin.blockSignals(True)
        self.object_index_spin.setMaximum(max_index)
        if self.last_selected_index > max_index:
            self.last_selected_index = max_index
            self.object_index_spin.setValue(max_index)
        self.object_index_spin.blockSignals(False)

    def update_position_controls_for_selected(self):
        if self.last_selected_type == "Sphere" and current_num_spheres > 0:
            pos = spheres[self.last_selected_index].to_numpy()
        elif self.last_selected_type == "Liquid" and current_num_particles > 0:
            pos = liquid_particles[self.last_selected_index].to_numpy()
        else:
            pos = np.array([0.0, 0.0, 0.0])
        self.update_position_controls(pos)

    def change_position(self):
        x = self.pos_x_spin.value() / 100.0
        y = self.pos_y_spin.value() / 100.0
        z = self.pos_z_spin.value() / 100.0
        pos = ti.Vector([x, y, z])
        if self.last_selected_type == "Sphere":
            if 0 <= self.last_selected_index < current_num_spheres:
                spheres[self.last_selected_index] = pos
                sphere_velocities[self.last_selected_index] = ti.Vector([0.0, 0.0, 0.0])
        elif self.last_selected_type == "Liquid":
            if 0 <= self.last_selected_index < current_num_particles:
                liquid_particles[self.last_selected_index] = pos
                liquid_velocities[self.last_selected_index] = ti.Vector([0.0, 0.0, 0.0])

    def update_position_controls(self, pos):
        self.pos_x_spin.blockSignals(True)
        self.pos_y_spin.blockSignals(True)
        self.pos_z_spin.blockSignals(True)
        self.pos_x_spin.setValue(int(pos[0] * 100))
        self.pos_y_spin.setValue(int(pos[1] * 100))
        self.pos_z_spin.setValue(int(pos[2] * 100))
        self.pos_x_spin.blockSignals(False)
        self.pos_y_spin.blockSignals(False)
        self.pos_z_spin.blockSignals(False)

    def timerEvent(self, event):
        dt = 0.016
        compute_cloth_forces()
        simulate_cloth(dt)
        simulate_spheres(dt)
        simulate_liquid(dt)
        self.gl_widget.update()

        if self.recording:
            self.capture_frame()
            self.record_frame_count += 1
            if self.record_frame_count >= self.max_record_frames:
                self.finish_recording()

    def capture_frame(self):
        # Capture the current OpenGL framebuffer as an image
        w = self.gl_widget.width()
        h = self.gl_widget.height()
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        data = glReadPixels(0, 0, w, h, GL_RGBA, GL_UNSIGNED_BYTE)
        image = np.frombuffer(data, dtype=np.uint8).reshape(h, w, 4)
        image = np.flipud(image)  # Flip vertically
        self.frames.append(image)

    def render_and_save_mp4(self):
        if self.recording:
            return  # Already recording
        self.recording = True
        self.frames = []
        self.record_frame_count = 0
        self.max_record_frames = 300  # 5 seconds at 60 FPS
        self.btn_render_mp4.setEnabled(False)
        self.btn_render_mp4.setText("Recording...")

    def finish_recording(self):
        self.recording = False
        self.btn_render_mp4.setEnabled(True)
        self.btn_render_mp4.setText("Render and Save MP4")

        # Ask user for save location
        filename, _ = QFileDialog.getSaveFileName(self, "Save Video", "", "MP4 Video (*.mp4)")
        if filename:
            if not filename.endswith(".mp4"):
                filename += ".mp4"
            # Save frames as MP4 using imageio
            with imageio.get_writer(filename, fps=60) as video:
                for frame in self.frames:
                    video.append_data(frame)
        self.frames = []

def main():
    app = QApplication(sys.argv)
    fmt = QSurfaceFormat()
    fmt.setDepthBufferSize(24)
    fmt.setSamples(4)
    QSurfaceFormat.setDefaultFormat(fmt)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

class GLViewportWidget(QOpenGLWidget):
    def __init__(self):
        super(GLViewportWidget, self).__init__()
        self.setWindowTitle('3D Physics Simulation')
        self.setGeometry(100, 100, 800, 600)
        self.setFormat(QSurfaceFormat.defaultFormat())
        self.quadric = None

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        self.quadric = gluNewQuadric()
        gluQuadricNormals(self.quadric, GLU_SMOOTH)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h if h != 0 else 1.0, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5)

        if cloth_active:
            self.draw_cloth()
        if current_num_spheres > 0:
            self.draw_spheres()
        if current_num_particles > 0:
            self.draw_liquid()

    def draw_cloth(self):
        cloth_np = cloth_pos.to_numpy()
        glColor3f(0.0, 1.0, 0.0)
        for i in range(n):
            for j in range(n):
                pos = cloth_np[i, j]
                glPushMatrix()
                glTranslatef(pos[0], pos[1], pos[2])
                gluSphere(self.quadric, 0.02, 8, 8)
                glPopMatrix()

        glColor3f(0.5, 0.8, 0.5)
        glBegin(GL_LINES)
        for i in range(n):
            for j in range(n):
                pos = cloth_np[i, j]
                if i < n - 1:
                    pos2 = cloth_np[i + 1, j]
                    glVertex3f(pos[0], pos[1], pos[2])
                    glVertex3f(pos2[0], pos2[1], pos2[2])
                if j < n - 1:
                    pos2 = cloth_np[i, j + 1]
                    glVertex3f(pos[0], pos[1], pos[2])
                    glVertex3f(pos2[0], pos2[1], pos2[2])
        glEnd()

    def draw_spheres(self):
        spheres_np = spheres.to_numpy()
        for i in range(current_num_spheres):
            pos = spheres_np[i]
            r = 0.8 + (i % 3) * 0.2
            g = 0.2 + (i % 5) * 0.15
            b = 0.2 + (i % 7) * 0.1
            glColor3f(r, g, b)
            glPushMatrix()
            glTranslatef(pos[0], pos[1], pos[2])
            gluSphere(self.quadric, sphere_radius, 16, 16)
            glPopMatrix()

    def draw_liquid(self):
        liquid_np = liquid_particles.to_numpy()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.2, 0.4, 0.8, 0.6)
        for i in range(current_num_particles):
            pos = liquid_np[i]
            glPushMatrix()
            glTranslatef(pos[0], pos[1], pos[2])
            gluSphere(self.quadric, 0.02, 8, 8)
            glPopMatrix()
        glDisable(GL_BLEND)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('3D Physics Simulation with PyQt5 and Taichi')
        self.setGeometry(100, 100, 1000, 600)

        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.gl_widget = GLViewportWidget()
        main_layout.addWidget(self.gl_widget, 4)

        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(300)
        sidebar_layout = QVBoxLayout()
        self.sidebar.setLayout(sidebar_layout)
        main_layout.addWidget(self.sidebar, 1)

        self.btn_add_sphere = QPushButton("Add Sphere")
        self.btn_add_sphere.clicked.connect(self.add_sphere)
        sidebar_layout.addWidget(self.btn_add_sphere)

        self.btn_add_cloth = QPushButton("Add Cloth")
        self.btn_add_cloth.clicked.connect(self.add_cloth)
        sidebar_layout.addWidget(self.btn_add_cloth)

        self.btn_add_liquid = QPushButton("Add Liquid")
        self.btn_add_liquid.clicked.connect(self.add_liquid)
        sidebar_layout.addWidget(self.btn_add_liquid)

        params_group = QGroupBox("Simulation Parameters")
        params_layout = QFormLayout()
        params_group.setLayout(params_layout)
        sidebar_layout.addWidget(params_group)

        self.viscosity_slider = QSlider(Qt.Horizontal)
        self.viscosity_slider.setMinimum(0)
        self.viscosity_slider.setMaximum(100)
        self.viscosity_slider.setValue(int(liquid_viscosity * 100))
        self.viscosity_slider.valueChanged.connect(self.change_viscosity)
        params_layout.addRow(QLabel("Liquid Viscosity"), self.viscosity_slider)

        self.gravity_slider = QSlider(Qt.Horizontal)
        self.gravity_slider.setMinimum(0)
        self.gravity_slider.setMaximum(200)
        self.gravity_slider.setValue(int(gravity_speed * 100))
        self.gravity_slider.valueChanged.connect(self.change_gravity_speed)
        params_layout.addRow(QLabel("Gravity Speed"), self.gravity_slider)

        pos_group = QGroupBox("Position Controls (Last Added Sphere/Liquid)")
        pos_layout = QFormLayout()
        pos_group.setLayout(pos_layout)
        sidebar_layout.addWidget(pos_group)

        self.pos_x_spin = QSpinBox()
        self.pos_x_spin.setRange(-100, 100)
        self.pos_x_spin.setValue(0)
        self.pos_x_spin.valueChanged.connect(self.change_position)
        pos_layout.addRow(QLabel("X"), self.pos_x_spin)

        self.pos_y_spin = QSpinBox()
        self.pos_y_spin.setRange(-100, 100)
        self.pos_y_spin.setValue(0)
        self.pos_y_spin.valueChanged.connect(self.change_position)
        pos_layout.addRow(QLabel("Y"), self.pos_y_spin)

        self.pos_z_spin = QSpinBox()
        self.pos_z_spin.setRange(-100, 100)
        self.pos_z_spin.setValue(0)
        self.pos_z_spin.valueChanged.connect(self.change_position)
        pos_layout.addRow(QLabel("Z"), self.pos_z_spin)

        sidebar_layout.addStretch()

        self.last_added_type = None
        self.last_added_index = -1

        self.timer = self.startTimer(16)

    def add_sphere(self):
        global current_num_spheres
        if current_num_spheres >= max_spheres:
            return
        pos = ti.Vector([0.0, 0.5, 0.0])
        initialize_sphere(current_num_spheres, pos)
        current_num_spheres += 1
        self.last_added_type = 'sphere'
        self.last_added_index = current_num_spheres - 1
        self.update_position_controls(pos)

    def add_cloth(self):
        global cloth_active
        if cloth_active:
            return
        initialize_cloth()
        cloth_active = True

    def add_liquid(self):
        global current_num_particles
        if current_num_particles + 100 > max_particles:
            return
        base_y = 1.0
        for i in range(100):
            pos = ti.Vector([
                (ti.random() - 0.5) * 0.5,
                base_y + (ti.random() * 0.5),
                (ti.random() - 0.5) * 0.5
            ])
            initialize_liquid_particle(current_num_particles, pos)
            current_num_particles += 1
        self.last_added_type = 'liquid'
        self.last_added_index = current_num_particles - 1
        self.update_position_controls(liquid_particles[self.last_added_index].to_numpy())

    def change_viscosity(self, value):
        global liquid_viscosity
        liquid_viscosity = value / 100.0

    def change_gravity_speed(self, value):
        global gravity_speed
        gravity_speed = value / 100.0

    def change_position(self):
        if self.last_added_type is None or self.last_added_index < 0:
            return
        x = self.pos_x_spin.value() / 100.0
        y = self.pos_y_spin.value() / 100.0
        z = self.pos_z_spin.value() / 100.0
        pos = ti.Vector([x, y, z])
        if self.last_added_type == 'sphere':
            spheres[self.last_added_index] = pos
            sphere_velocities[self.last_added_index] = ti.Vector([0.0, 0.0, 0.0])
        elif self.last_added_type == 'liquid':
            liquid_particles[self.last_added_index] = pos
            liquid_velocities[self.last_added_index] = ti.Vector([0.0, 0.0, 0.0])

    def update_position_controls(self, pos):
        self.pos_x_spin.blockSignals(True)
        self.pos_y_spin.blockSignals(True)
        self.pos_z_spin.blockSignals(True)
        self.pos_x_spin.setValue(int(pos[0] * 100))
        self.pos_y_spin.setValue(int(pos[1] * 100))
        self.pos_z_spin.setValue(int(pos[2] * 100))
        self.pos_x_spin.blockSignals(False)
        self.pos_y_spin.blockSignals(False)
        self.pos_z_spin.blockSignals(False)

    def timerEvent(self, event):
        dt = 0.016
        compute_cloth_forces()
        simulate_cloth(dt)
        simulate_spheres(dt)
        simulate_liquid(dt)
        self.gl_widget.update()

def main():
    app = QApplication(sys.argv)
    fmt = QSurfaceFormat()
    fmt.setDepthBufferSize(24)
    fmt.setSamples(4)
    QSurfaceFormat.setDefaultFormat(fmt)

    # Do not initialize cloth, spheres, or liquid on startup
    # initialize_cloth()
    # initialize_spheres()
    # initialize_liquid()

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
